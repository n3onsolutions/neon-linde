import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

const ChatArea = ({ messages, onSendMessage }) => {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!input.trim()) return;
        onSendMessage(input);
        setInput('');
    };

    return (
        <div className="flex-1 flex flex-col bg-white overflow-hidden">
            {/* Messages List */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center px-4">
                        <div className="max-w-md bg-gray-50 border border-gray-100 rounded-2xl p-8 shadow-sm">
                            <h3 className="text-lg font-semibold text-gray-800 mb-2">Bienvenido al Asistente Comercial de Sogacsa-Linde</h3>
                            <p className="text-gray-500 leading-relaxed">
                                Estoy a su disposición para proporcionarle cualquier información técnica o comercial que necesite sobre nuestros servicios y productos.
                                <br /><br />
                                <strong>¿En qué puedo ayudarle en este momento?</strong>
                            </p>
                        </div>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <div
                            key={msg.id || index}
                            className={`flex gap-4 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
                        >
                            {/* Avatar */}
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${msg.sender === 'user' ? 'bg-red-50 text-linde-red border border-red-100' : 'bg-gray-100 text-gray-600'
                                }`}>
                                {msg.sender === 'user' ? <User size={20} /> : <Bot size={20} />}
                            </div>

                            {/* Bubble */}
                            <div className={`max-w-[70%] p-4 rounded-2xl text-sm leading-relaxed ${msg.sender === 'user'
                                ? 'bg-soft-red text-gray-800 rounded-tr-none'
                                : 'bg-soft-grey text-gray-800 rounded-tl-none'
                                }`}>
                                {msg.text}
                            </div>
                        </div>
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-100">
                <form onSubmit={handleSubmit} className="flex gap-2 max-w-4xl mx-auto">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-100 focus:border-linde-red transition-all"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim()}
                        className="bg-linde-red hover:brightness-110 text-white p-3 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send size={20} />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatArea;
