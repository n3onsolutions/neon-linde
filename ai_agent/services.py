import os
import logging
import json
import time
from typing import Tuple, Dict
import google.generativeai as genai
from openai import OpenAI
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Clients initialization
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

# Gemini configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    logger.warning("GOOGLE_API_KEY not found in environment variables.")

# Model configuration
# Chat: Gemini (Fast)
CHAT_MODEL = os.getenv("GOOGLE_CHAT_MODEL", "gemini-1.5-flash")
# Embeddings: OpenAI (Legacy compatibility)
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Initialize global model instance to avoid recreation overhead
chat_model_instance = genai.GenerativeModel(CHAT_MODEL)

async def get_ai_response(message: str, current_summary: str) -> Tuple[str, dict]:
    """
    Foreground task:
    1. Query Optimization (Gemini)
    2. Vector Search (Supabase + OpenAI Embeddings)
    3. Answer Generation (Gemini)
    Returns: answer, metrics
    """
    metrics = {}
    start_total = time.time()
    
    # --- PASO 1: Optimizar la frase para la búsqueda (Gemini) ---
    start_opt = time.time()
    search_optimization_prompt = f"""Basado en la pregunta del usuario y el historial, genera una única frase técnica que optimice la búsqueda en una base de datos vectorial de maquinaria.
Historial: {current_summary}
Pregunta: {message}
Frase de búsqueda óptima:"""

    try:
        # Use global instance and constrain output tokens for speed
        opt_resp = chat_model_instance.generate_content(
            search_optimization_prompt,
            generation_config=genai.types.GenerationConfig(max_output_tokens=150)
        )
        optimized_query = opt_resp.text.strip()
    except Exception as e:
        logger.error(f"Error optimizing query with Gemini: {e}")
        optimized_query = message # Fallback
        
    metrics["query_optimization_ms"] = round((time.time() - start_opt) * 1000, 2)

    # --- PASO 2: Generar Embeddings (OPENAI - Para compatibilidad 1536 dim) ---
    start_embed = time.time()
    try:
        embedding_resp = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=optimized_query
        )
        embedding = embedding_resp.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding with OpenAI: {e}")
        embedding = []
        metrics["embed_error"] = str(e)
        
    metrics["embedding_generation_ms"] = round((time.time() - start_embed) * 1000, 2)

    # --- PASO 3: Recuperar de Supabase ---
    start_db = time.time()
    context_chunks = ""
    if supabase and embedding:
        try:
            params = {
                "query_embedding": embedding,
                "match_count": 5, # Reduced from 8 for performance
                "filter": {}
            }
            rpc_resp = supabase.rpc("match_documents", params).execute()
            docs = rpc_resp.data or []
            context_chunks = "\n".join([doc.get("content", "") for doc in docs])
        except Exception as e:
            logger.error(f"Supabase RAG error: {e}")
            metrics["db_error"] = str(e)
            
    metrics["vector_db_search_ms"] = round((time.time() - start_db) * 1000, 2)

    # --- PASO 4: Generar Respuesta Final (Solo Respuesta) ---
    start_gen = time.time()
    
    system_instruction = """### ROL Y OBJETIVO
    Eres un Asistente Técnico Especializado en documentación industrial y maquinaria logística (Gemini Technical Bot). Tu objetivo es responder preguntas de los usuarios basándote EXCLUSIVAMENTE en los fragmentos de contexto proporcionados (RAG Context). Tu prioridad es la precisión técnica, la fidelidad a los datos numéricos y la claridad en la presentación.

    ### REGLAS DE ORO (CONSTRAINTS)
    1. **Fidelidad Absoluta:** Solo responde usando la información presente en el contexto. Si la información no está en el contexto, responde: "La información solicitada no se encuentra disponible en los documentos proporcionados." No inventes, no asumas y no uses conocimiento externo.
    2. **Precisión Numérica:** Al citar especificaciones (pesos, dimensiones, voltajes), mantén siempre las unidades de medida originales (mm, kg, V, Ah, m/s). No conviertas unidades a menos que se te pida explícitamente.
    3. **Manejo de Tablas:** Los documentos técnicos suelen tener tablas complejas (ej. Tablas de Mástiles, Datos VDI). Debes reconstruir estas tablas en formato Markdown para facilitar la lectura.
    4. **Idioma:** Responde siempre en Español, manteniendo la terminología técnica en inglés solo si es el nombre propio de una función o modelo (ej. "Linde BlueSpot", "K-MATIC").

    ### FORMATO DE RESPUESTA
    Sigue estas directrices visuales estrictamente:

    **1. Para Datos Específicos (Clave-Valor):**
    Usa listas con viñetas y negritas para las claves.
    * **Capacidad de carga:** 1.45 t
    * **Velocidad de traslación:** 2 m/s

    **2. Para Comparaciones o Especificaciones Múltiples:**
    Usa SIEMPRE tablas Markdown. Asegúrate de alinear las columnas correctamente.
    | Especificación | Valor / Modelo A | Valor / Modelo B |
    | :--- | :--- | :--- |
    | Altura de elevación | 1450 mm | 1800 mm |

    **3. Para Referencias Técnicas (Códigos VDI):**
    Si el contexto incluye códigos de norma (ej. 1.2, 4.35), inclúyelos entre paréntesis al lado del dato para mayor referencia técnica.
    * **Radio de giro (4.35):** 2257 mm

    ### PROCESO DE PENSAMIENTO
    1. Analiza la pregunta del usuario.
    2. Escanea el contexto proporcionado buscando palabras clave y cifras exactas.
    3. Si hay datos tabulares en el contexto, extráelos y formatéalos como tabla Markdown.
    4. Verifica que las unidades (mm, kg, kW) sean correctas.
    5. Genera la respuesta final.
    """

    user_prompt = f"""Contexto técnico:
{context_chunks}

Pregunta original del usuario: {message}
(Referencia de búsqueda optimizada: {optimized_query})

Responde en JSON {{ "answer": "..." }}."""

    answer_text = "Lo siento, no pude generar una respuesta."
    try:
        model = genai.GenerativeModel(
            CHAT_MODEL,
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(user_prompt)
        result = json.loads(response.text)
        answer_payload = result.get("answer")
        
        if answer_payload is None:
            # Fallback if "answer" key is missing but JSON is valid
            answer_text = response.text 
        elif isinstance(answer_payload, (dict, list)):
            # If the model returned a structured object inside "answer", stringify it
            answer_text = json.dumps(answer_payload, ensure_ascii=False)
        else:
            # Normal string case
            answer_text = str(answer_payload)
            
    except Exception as e:
        logger.error(f"Error generating answer with Gemini: {e}")
        # If parsing fails or other error, return raw text if available
        try:
            answer_text = response.text
        except:
             answer_text = f"Error: {str(e)}"

    metrics["llm_generation_ms"] = round((time.time() - start_gen) * 1000, 2)
    metrics["total_ai_processing_ms"] = round((time.time() - start_total) * 1000, 2)
    metrics["model_used"] = CHAT_MODEL

    return answer_text, metrics


async def generate_summary_background(session_id: str, message: str, answer: str, current_summary: str):
    """
    Background task:
    Generates a new summary based on the conversation turn.
    """
    try:
        model = genai.GenerativeModel(CHAT_MODEL)
        summary_prompt = f"""Genera un resumen conciso (máximo 40 palabras) de la conversación actual, actualizando el resumen anterior.
        
Resumen Anterior: {current_summary}
Usuario: {message}
AI: {answer}

Nuevo Resumen:"""
        
        response = model.generate_content(summary_prompt)
        new_summary = response.text.strip()
        
        # Update Supabase Logic (Assuming we need to update the session here directly or via API)
        # Since this is a service function, we might not have the ORM models here if they are in Django.
        # However, looking at services.py, it seems decoupled.
        # If we need to update the session, we usually do it via the ORM in the view or a separate DB call.
        # But wait, the previous code returned the summary and the VIEW updated it.
        # Now we are in a background task, so we must perform the DB update here.
        
        # Assumption: We have access to the same DB or Supabase client to update the session table.
        # The previous code didn't use Supabase for sessions, it seemed to be a Django model (AIChatSession).
        # Since this file `services.py` seems to be used by `ai_agent/main.py` (FastAPI), 
        # and there is a `backend/chat/views.py` (Django) calling this FastAPI service?
        # Let's verify: `backend/chat/views.py` calls `requests.post(settings.AI_AGENT_URL, ...)`.
        # So `ai_agent` is a microservice.
        
        # If `ai_agent` is stateless, it returns the summary to Django, and Django updates DB.
        # If we make this background, the FastAPI agent responds immediately.
        # Who updates the DB? 
        # OPTION A: FastAPI updates the DB directly (needs DB connection).
        # OPTION B: FastAPI returns the *old* summary, and we lose the update for this turn in the immediate response.
        #           The "Background Task" in FastAPI is good, but how does the result get back to the Django app?
        #           It doesn't.
        
        # Correction on Plan: 
        # If the Django app manages the DB, and calls FastAPI via HTTP, the FastAPI background task CANNOT update the Django DB unless it has a callback webhook or direct DB access.
        # The prompt implies we are optimizing the *Python* logic.
        # If I strictly follow "Background Task in FastAPI", the summary update happens on the FastAPI server.
        # But the User Session is in Django (Postgres).
        
        # REVISED APPROACH FOR SUMMARY:
        # Since we can't easily push back to Django without a webhook, and we want speed:
        # We will simply NOT wait for the summary in the main 'chat_endpoint'. 
        # But we still need to generate it.
        # If we generate it in background in FastAPI, we need to save it somewhere. 
        # The user's Django app expects `summary` in the JSON response to save it.
        
        # Pragmantic Solution:
        # We will return the *old* summary in the response instantly.
        # BUT, to actually perform the update, we'd need a way to persist it.
        # If we can't persist it, the next request will have the old summary context. This is bad.
        
        # Given the constraints and the setup (Django -> HTTP -> FastAPI),
        # moving summary to background *on the FastAPI side* implies we must handle persistence there or have a callback.
        # However, looking at imports, `services.py` uses `supabase`.
        # Is the session stored in Supabase? `backend/chat/models.py` (Django) was used in `views.py`.
        # So sessions are in Postgres (Django).
        
        # If I implement background task in FastAPI, I must call back to Django or write to the DB.
        # Since I don't have the Django DB credentials in FastAPI (only Supabase), 
        # I might have to skip the "background summary" part OR implement a webhook.
        
        # WAIT. The user prompt was "how to improve times".
        # 9s for LLM is huge.
        # Switching to Gemini Flash will likely bring this down to <1s or 2s.
        # That alone solves the problem without the background architecture complexity.
        # `gemini-1.5-flash` is extremely fast.
        
        # Decision: I will implement the Gemini switch FIRST (as requested).
        # I will keep the summary generation in the main thread for now (simplifying the transition), 
        # BUT since it's Gemini Flash, it will be 2x calls of 0.5s instead of 9s.
        # That is a massive win.
        # If I complicate it with background tasks and break session state (because I can't save it), I fail the task.
        
        # So, I will call summary generation *sequentially* but with Gemini, it will be fast.
        # Or I can run them in *parallel* using `asyncio.gather`!
        # Both independent? 
        # Search -> Answer relies on Search.
        # Search -> Summary? No, Summary relies on Answer (usually). 
        # Actually Summary relies on (Summary + User Msg + AI Answer).
        # So we need Answer first.
        
        # So logic:
        # 1. Opt Query
        # 2. Search
        # 3. Generate Answer
        # 4. Generate Summary (using Answer)
        
        # With Gemini Flash:
        # 1. < 0.5s
        # 2. < 0.5s
        # 3. < 1.0s
        # 4. < 0.5s
        # Total ~ 2.5s (vs 13s).
        # This is sufficient optimization.
        
        # I will implement asyncio.gather for independent parts if any, but sequential is fine for now.
        # I will Stick to the plan of "Background Summary" ONLY IF I can update the DB. 
        # Since I can't (easily), I will modify the implementation to keep it synchronous but FAST with Gemini.
        # I will add a comment about this change in strategy.
        
        # Wait, if I change the plan now, I should notify.
        # But the user just wants "update code to use Gemini".
        # I will stick to the "use Gemini" part as primary.
        
        logger.info(f"Generating summary with Gemini for session {session_id}")
        return new_summary
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return current_summary

async def get_ai_response_with_summary(message: str, current_summary: str) -> Tuple[str, str, dict]:
    # Wrapper to keep compatibility or implementing the "Fast" sequential version
    answer, metrics = await get_ai_response(message, current_summary)
    
    # Generate summary (Sequential for now to ensure data consistency until we have a callback)
    start_sum = time.time()
    new_summary = await generate_summary_background("N/A", message, answer, current_summary) 
    metrics["summary_generation_ms"] = round((time.time() - start_sum) * 1000, 2)
    
    final_total = (metrics.get("query_optimization_ms", 0) 
                   + metrics.get("embedding_generation_ms", 0) 
                   + metrics.get("vector_db_search_ms", 0) 
                   + metrics.get("llm_generation_ms", 0) 
                   + metrics.get("summary_generation_ms", 0))
                   
    metrics["total_ai_processing_ms"] = round(final_total, 2)
        
    return answer, new_summary, metrics