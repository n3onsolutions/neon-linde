import React from 'react';

const LoggingPanel = () => {
    return (
        <div className="flex-1 p-8 overflow-y-auto bg-gray-50">
            <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">System Logs</h2>
                <p className="text-gray-500 mb-6">Real-time interaction logs with the AI Backend.</p>

                <div className="border border-gray-200 rounded-lg overflow-hidden">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-gray-50 text-gray-600 font-medium border-b border-gray-200">
                            <tr>
                                <th className="px-6 py-3">Timestamp</th>
                                <th className="px-6 py-3">Level</th>
                                <th className="px-6 py-3">Event</th>
                                <th className="px-6 py-3">User</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {/* Mock Logs */}
                            <tr className="hover:bg-gray-50">
                                <td className="px-6 py-4 text-gray-500">2023-12-21 16:20:01</td>
                                <td className="px-6 py-4"><span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">INFO</span></td>
                                <td className="px-6 py-4">New Request /api/chat</td>
                                <td className="px-6 py-4 text-gray-500">Anonymous</td>
                            </tr>
                            <tr className="hover:bg-gray-50">
                                <td className="px-6 py-4 text-gray-500">2023-12-21 16:20:05</td>
                                <td className="px-6 py-4"><span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">DEBUG</span></td>
                                <td className="px-6 py-4">Context Retrieved from VectorDB</td>
                                <td className="px-6 py-4 text-gray-500">System</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div className="mt-4 text-center text-xs text-gray-400">
                    End of logs
                </div>
            </div>
        </div>
    );
};

export default LoggingPanel;
