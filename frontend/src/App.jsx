import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MessageSquare, List, BarChart3, LogOut, Plus, Trash2, Send, User, Bot } from 'lucide-react';

// --- CONFIGURACIÓN DE AXIOS ---
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/chat';
axios.defaults.withCredentials = true;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

axios.interceptors.request.use(config => {
    const token = getCookie('csrftoken');
    if (token) config.headers['X-CSRFToken'] = token;
    return config;
});

// --- COMPONENTE LOGIN ---
const Login = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4 font-sans">
            <div className="bg-white p-8 rounded-2xl shadow-xl max-w-sm w-full border border-gray-100">
                <div className="flex items-center justify-center gap-4 mb-6">
                    <img src="/logo_linde_chat.png" alt="Linde" className="h-10 object-contain" />
                    <div className="w-px h-8 bg-gray-200"></div>
                    <img src="/logo_sogacsa.jpeg" alt="Sogacsa" className="h-10 object-contain mix-blend-multiply" />
                </div>
                <div className="text-center mb-8">
                    <h2 className="text-xl font-bold text-gray-800">Asistente Comercial</h2>
                    <p className="text-gray-500 text-sm">Sogacsa - Linde</p>
                </div>
                <form onSubmit={(e) => { e.preventDefault(); onLogin(username, password); }} className="space-y-4">
                    <input
                        type="text"
                        placeholder="Username"
                        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 outline-none transition-all"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 outline-none transition-all"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <button className="w-full bg-[#c3002f] hover:bg-red-700 text-white font-bold py-3 rounded-xl shadow-lg transition-all active:scale-[0.98]">
                        Sign In
                    </button>
                </form>
                <p className="text-center text-xs text-gray-400 mt-8">Contact administrator for access.</p>
            </div>
        </div>
    );
};

// --- COMPONENTE APP ---
function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loadingAuth, setLoadingAuth] = useState(true);
    const [sessions, setSessions] = useState([]);
    const [selectedSessionId, setSelectedSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');

    useEffect(() => { checkAuth(); }, []);

    const checkAuth = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/check-auth/`);
            if (res.data.is_authenticated) {
                setIsAuthenticated(true);
                fetchSessions();
            }
        } catch (e) { setIsAuthenticated(false); }
        finally { setLoadingAuth(false); }
    };

    const handleLogin = async (username, password) => {
        try {
            await axios.post(`${API_BASE_URL}/login/`, { username, password });
            setIsAuthenticated(true);
            fetchSessions();
        } catch (e) { alert("Error de autenticación"); }
    };

    const handleLogout = async () => {
        await axios.post(`${API_BASE_URL}/logout/`);
        setIsAuthenticated(false);
        setSessions([]);
        setMessages([]);
    };

    const fetchSessions = async () => {
        const res = await axios.get(`${API_BASE_URL}/sessions/`);
        setSessions(res.data);
    };

    const handleSelectSession = async (id) => {
        setSelectedSessionId(id);
        const res = await axios.get(`${API_BASE_URL}/sessions/${id}/`);
        setMessages(res.data.interactions.map(ia => ({
            id: ia.id, text: ia.message, sender: ia.is_user ? 'user' : 'ai'
        })));
    };

    const handleSendMessage = async (e) => {
        if (e) e.preventDefault();
        if (!inputText.trim()) return;

        const text = inputText;
        setInputText('');
        setMessages(prev => [...prev, { id: Date.now(), text, sender: 'user' }]);

        try {
            const res = await axios.post(API_BASE_URL + '/', {
                message: text,
                session_id: selectedSessionId
            });
            if (!selectedSessionId) {
                setSelectedSessionId(res.data.session_id);
                fetchSessions();
            }
            setMessages(prev => [...prev, { id: res.data.answer_id, text: res.data.answer, sender: 'ai' }]);
        } catch (e) {
            setMessages(prev => [...prev, { id: Date.now(), text: "Error de conexión", sender: 'ai', isError: true }]);
        }
    };

    const handleDeleteSession = async (sessionId) => {
        try {
            if (!confirm('¿Seguro que deseas eliminar este chat?')) return;
            await axios.post(`${API_BASE_URL}/sessions/${sessionId}/delete/`);
            setSessions(prev => prev.filter(s => s.id !== sessionId));
            if (sessionId === selectedSessionId) {
                setSelectedSessionId(null);
                setMessages([]);
            }
        } catch (error) {
            console.error("Error deleting session", error);
        }
    };

    if (loadingAuth) return <div className="h-screen flex items-center justify-center">Cargando...</div>;
    if (!isAuthenticated) return <Login onLogin={handleLogin} />;

    return (
        <div className="flex h-screen bg-gray-50 overflow-hidden">
            {/* Sidebar */}
            <aside className="w-72 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-4">
                    <button
                        onClick={() => { setSelectedSessionId(null); setMessages([]); }}
                        className="w-full flex items-center justify-center gap-2 bg-gray-900 text-white py-3 rounded-xl hover:bg-gray-800 transition-all shadow-sm"
                    >
                        <Plus size={18} /> Nuevo Chat
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto px-3 space-y-1">
                    {sessions.map(s => (
                        <div
                            key={s.id}
                            onClick={() => handleSelectSession(s.id)}
                            className={`group p-3 rounded-xl cursor-pointer flex items-center justify-between gap-3 transition-all ${selectedSessionId === s.id ? 'bg-red-50 text-red-700 font-medium' : 'hover:bg-gray-100 text-gray-600'}`}
                        >
                            <div className="flex items-center gap-3 overflow-hidden">
                                <MessageSquare size={16} className="shrink-0" />
                                <span className="truncate text-sm">{s.summary || `Chat ${s.id}`}</span>
                            </div>
                            <button
                                onClick={(e) => { e.stopPropagation(); handleDeleteSession(s.id); }}
                                className="p-1 text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                title="Eliminar chat"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                    ))}
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col min-w-0 bg-white">
                {/* Header Mejorado */}
                <header className="h-16 border-b border-gray-100 flex items-center justify-between px-6 shrink-0">
                    <h1 className="text-lg font-bold text-gray-800 tracking-tight">Asistente Comercial</h1>

                    <div className="flex items-center gap-4">
                        {/* Logos juntos y pequeños */}
                        <div className="flex items-center gap-2 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-100">
                            <img src="/logo_sogacsa.jpeg" alt="Sogacsa" className="h-5 w-auto object-contain mix-blend-multiply" />
                            <div className="w-px h-4 bg-gray-300"></div>
                            <img src="/logo_linde_chat.png" alt="Linde" className="h-5 w-auto object-contain" />
                        </div>

                        <button onClick={handleLogout} className="p-2 text-gray-400 hover:text-red-600 transition-colors">
                            <LogOut size={20} />
                        </button>
                    </div>
                </header>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
                            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                                <MessageSquare size={32} />
                            </div>
                            <p>¿En qué puedo ayudarte hoy?</p>
                        </div>
                    )}
                    {messages.map(m => (
                        <div key={m.id} className={`flex gap-4 ${m.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                            {/* Avatar */}
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${m.sender === 'user' ? 'bg-red-50 text-[#c3002f] border border-red-100' : 'bg-gray-100 text-gray-600'}`}>
                                {m.sender === 'user' ? <User size={20} /> : <Bot size={20} />}
                            </div>

                            {/* Bubble */}
                            <div className={`max-w-[70%] p-4 rounded-2xl shadow-sm text-sm leading-relaxed ${m.sender === 'user' ? 'bg-[#c3002f] text-white rounded-tr-none' : 'bg-gray-100 text-gray-800 rounded-tl-none border border-gray-200'}`}>
                                {m.text}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Input Area */}
                <div className="p-6 border-t border-gray-100">
                    <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto relative">
                        <input
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder="Escribe tu consulta sobre carretillas o repuestos..."
                            className="w-full pl-6 pr-16 py-4 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-red-500 outline-none shadow-inner"
                        />
                        <button className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-[#c3002f] text-white rounded-xl hover:bg-red-700 transition-all">
                            <Send size={20} />
                        </button>
                    </form>
                </div>
            </main>
        </div>
    );
}

export default App;