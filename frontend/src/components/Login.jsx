import React, { useState } from 'react';

const Login = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await onLogin(username, password);
        } catch (err) {
            setError('Invalid credentials');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 border border-gray-100">
                <div className="text-center mb-10 flex flex-col items-center">
                    <div className="flex items-center justify-center gap-6 mb-8 w-full">
                        <img src="/logo_linde_login.png" alt="Linde Logo" className="h-20 object-contain" />
                        <div className="w-px h-16 bg-gray-200"></div>
                        <img src="/logo_sogacsa.jpeg" alt="Sogacsa Logo" className="h-20 object-contain" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-800 tracking-tight">Asistente Comercial Sogacsa-Linde</h2>
                    <p className="text-gray-500 text-sm mt-2 font-medium">Inicia sesión para continuar</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {error && (
                        <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg text-center border border-red-100">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-red-100 focus:border-linde-red transition-all"
                            placeholder="Enter your username"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-red-100 focus:border-linde-red transition-all"
                            placeholder="Enter your password"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-linde-red hover:brightness-110 text-white font-medium py-3 rounded-lg transition-all shadow-sm hover:shadow-md"
                    >
                        Sign In
                    </button>

                    <div className="text-center text-xs text-gray-400 mt-4">
                        Contact administrator for access.
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Login;
