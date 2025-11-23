import React, { useState, useRef, useEffect } from 'react';
import { Send, PieChart, User as UserIcon } from 'lucide-react';
import { apiService } from '../services/api';
import { ChartRenderer } from './ChartRenderer';

interface VisualizationMessage {
    id: string;
    text: string;
    isUser: boolean;
    timestamp: Date;
    chartData?: {
        chartType: string;
        data: any[];
        options: any;
    };
}

export const VisualizationChat: React.FC = () => {
    const [messages, setMessages] = useState<VisualizationMessage[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (query?: string) => {
        const messageText = query || inputValue.trim();
        if (!messageText) return;

        const userMessage: VisualizationMessage = {
            id: Date.now().toString(),
            text: messageText,
            isUser: true,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setLoading(true);

        try {
            const response = await apiService.visualize(messageText);

            const aiMessage: VisualizationMessage = {
                id: (Date.now() + 1).toString(),
                text: response.error ? `I couldn't generate that chart: ${response.error}` : "Here is the visualization you requested:",
                isUser: false,
                timestamp: new Date(),
                chartData: response.error ? undefined : {
                    chartType: response.chartType,
                    data: response.data,
                    options: response.options
                }
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            const errorMessage: VisualizationMessage = {
                id: (Date.now() + 1).toString(),
                text: 'Sorry, I encountered an error generating the chart. Please try again.',
                isUser: false,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
            console.error('Error generating chart:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        handleSendMessage();
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="border-b border-gray-200 p-4">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                    <PieChart className="h-6 w-6 mr-2 text-purple-600" />
                    Data Visualization
                </h2>
                <p className="text-gray-600 text-sm">Ask for charts about your spending, investments, or trends</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && !loading && (
                    <div className="text-center text-gray-500 py-8">
                        <PieChart className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                        <p>Visualize your financial data instantly!</p>
                        <div className="mt-4 space-y-2">
                            <button
                                onClick={() => handleSendMessage("Show my spending trend for the last 6 months")}
                                className="block mx-auto bg-purple-50 hover:bg-purple-100 text-purple-700 px-4 py-2 rounded-md text-sm"
                            >
                                Show spending trend (last 6 months)
                            </button>
                            <button
                                onClick={() => handleSendMessage("Show spending by category")}
                                className="block mx-auto bg-purple-50 hover:bg-purple-100 text-purple-700 px-4 py-2 rounded-md text-sm"
                            >
                                Show spending by category
                            </button>
                            <button
                                onClick={() => handleSendMessage("Show my investment portfolio allocation")}
                                className="block mx-auto bg-purple-50 hover:bg-purple-100 text-purple-700 px-4 py-2 rounded-md text-sm"
                            >
                                Show investment portfolio
                            </button>
                        </div>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex flex-col ${message.isUser ? 'items-end' : 'items-start'}`}
                    >
                        <div
                            className={`max-w-[85%] lg:max-w-[75%] px-4 py-2 rounded-lg mb-2 ${message.isUser
                                    ? 'bg-purple-600 text-white'
                                    : 'bg-gray-100 text-gray-900'
                                }`}
                        >
                            <div className="flex items-start space-x-2">
                                {!message.isUser && (
                                    <PieChart className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                )}
                                {message.isUser && (
                                    <UserIcon className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                )}
                                <div className="flex-1">
                                    <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                                    <p className={`text-xs mt-1 ${message.isUser ? 'text-purple-200' : 'text-gray-500'
                                        }`}>
                                        {message.timestamp.toLocaleTimeString()}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Render Chart if available */}
                        {message.chartData && (
                            <div className="w-full max-w-2xl mb-4 ml-2">
                                <ChartRenderer
                                    chartType={message.chartData.chartType}
                                    data={message.chartData.data}
                                    options={message.chartData.options}
                                />
                            </div>
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-100 rounded-lg p-4">
                            <div className="flex items-center space-x-2">
                                <PieChart className="h-4 w-4" />
                                <div className="flex space-x-1">
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Form */}
            <div className="border-t border-gray-200 p-4">
                <form onSubmit={handleSubmit} className="flex space-x-2">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Ask for a chart (e.g., 'spending trend')..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !inputValue.trim()}
                        className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                    >
                        <Send className="h-4 w-4" />
                    </button>
                </form>
            </div>
        </div>
    );
};
