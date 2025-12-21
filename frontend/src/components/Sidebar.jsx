import React from 'react';
import { PlusCircle, MessageCircle, Trash2 } from 'lucide-react';
import { format } from 'date-fns';

const Sidebar = ({ sessions, selectedSessionId, onSelectSession, onNewChat, onDeleteSession }) => {
    return (
        <div className="w-80 border-r border-gray-200 flex flex-col bg-gray-50 h-full">
            <div className="h-20 px-4 flex items-center border-b border-gray-200 flex-shrink-0">
                <button
                    onClick={onNewChat}
                    className="w-full flex items-center justify-center gap-2 bg-linde-red hover:brightness-110 text-white py-2 px-4 rounded-lg transition-all shadow-sm"
                >
                    <PlusCircle size={18} />
                    <span className="font-medium">New Chat</span>
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-2 scrollbar-thin">
                <div className="space-y-2">
                    {sessions.map((session) => (
                        <div
                            key={session.id}
                            onClick={() => onSelectSession(session.id)}
                            className={`group w-full text-left p-3 rounded-lg flex items-start justify-between gap-1 transition-colors cursor-pointer ${selectedSessionId === session.id
                                ? 'bg-white shadow-sm border border-gray-200'
                                : 'hover:bg-gray-100'
                                }`}
                        >
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 text-gray-700 font-medium">
                                    <MessageCircle size={16} className="flex-shrink-0" />
                                    <span className="truncate">{session.summary || "New Session"}</span>
                                </div>
                                <span className="text-xs text-gray-400 pl-6 block">
                                    {format(new Date(session.created_at), 'MMM d, h:mm a')}
                                </span>
                            </div>

                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (window.confirm('Delete this session?')) onDeleteSession(session.id);
                                }}
                                className="p-1 text-gray-400 hover:text-linde-red opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                    ))}

                    {sessions.length === 0 && (
                        <div className="text-center text-gray-400 mt-10 text-sm">
                            No history yet.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
