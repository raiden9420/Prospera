import React, { createContext, useContext, useState, ReactNode } from 'react';
import { apiService } from '../services/api';
import type { ChatMessage, AIResponse } from '../types';

interface ChatContextType {
    messages: ChatMessage[];
    loading: boolean;
    sendMessage: (query: string) => Promise<void>;
    setChatQuery: (query: string) => void;
    chatQuery: string;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [loading, setLoading] = useState(false);
    const [chatQuery, setChatQuery] = useState('');

    const sendMessage = async (query: string) => {
        if (!query.trim()) return;

        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            text: query,
            isUser: true,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setLoading(true);

        try {
            const response: AIResponse = await apiService.askAI(query);

            const aiMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                text: JSON.stringify(response.response, null, 2),
                isUser: false,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            const errorMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                text: 'Sorry, I encountered an error processing your request. Please try again.',
                isUser: false,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
            console.error('Error sending message:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <ChatContext.Provider value={{ messages, loading, sendMessage, setChatQuery, chatQuery }}>
            {children}
        </ChatContext.Provider>
    );
};

export const useChat = () => {
    const context = useContext(ChatContext);
    if (context === undefined) {
        throw new Error('useChat must be used within a ChatProvider');
    }
    return context;
};
