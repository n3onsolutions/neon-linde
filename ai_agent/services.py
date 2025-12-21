import os
import logging
import json
from typing import Tuple
from openai import OpenAI
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Clients initialization
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

# Model configuration from environment
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

async def get_ai_response_with_summary(message: str, current_summary: str) -> Tuple[str, str]:
    """
    1. Optimiza la búsqueda (Query Transformation).
    2. Busca en Supabase.
    3. Responde y resume.
    """
    
    # --- PASO 1: Optimizar la frase para la búsqueda (NUEVO) ---
    # Convertimos "tienen la pala esa grande?" en "Especificaciones técnicas de cargadoras de ruedas con cuchara de alta capacidad"
    search_optimization_prompt = f"""Basado en la pregunta del usuario y el historial, genera una única frase técnica que optimice la búsqueda en una base de datos vectorial de maquinaria.
Historial: {current_summary}
Pregunta: {message}
Frase de búsqueda óptima:"""

    opt_resp = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": search_optimization_prompt}],
        max_completion_tokens=50
    )
    optimized_query = opt_resp.choices[0].message.content

    # --- PASO 2: Generar Embeddings de la frase OPTIMIZADA ---
    embedding_resp = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=optimized_query, # Usamos la frase técnica, no la pregunta original
    )
    embedding = embedding_resp.data[0].embedding

    # --- PASO 3: Recuperar de Supabase ---
    context_chunks = ""
    if supabase:
        try:
            params = {
                "query_embedding": embedding,
                "match_count": 8,
                "filter": {}
            }
            rpc_resp = supabase.rpc("match_documents", params).execute()
            docs = rpc_resp.data or []
            context_chunks = "\n".join([doc.get("content", "") for doc in docs])
        except Exception as e:
            logger.error(f"Supabase RAG error: {e}")

    # --- PASO 4: Generar Respuesta Final y Resumen ---
    system_prompt = """Eres un experto técnico de Sogacsa-Linde. 
Responde en JSON con:
- "answer": Respuesta técnica precisa. No desperdiciar ni una palabra. Se lo mas rapido y preciso posible. 
- "summary": Un resumen corto de la conversación (máximo 40 palabras)."""

    user_prompt = f"""Contexto técnico:
{context_chunks}

Pregunta original del usuario: {message}
(Referencia de búsqueda optimizada: {optimized_query})

Responde en formato JSON con 'answer' y 'summary'."""

    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        return result.get("answer"), result.get("summary")
    except Exception:
        return response.choices[0].message.content, current_summary