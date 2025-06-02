'use client';
import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
// import type { AxiosError, isAxiosError } from 'axios';
import MainLayout from '@/components/layout/MainLayout';

interface Message {
    id: number;
    text: string;
    sender: 'user' | 'ai';
    timestamp: Date;
}
interface ChatResponse {
    text: string;
}

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

export default function ChatPage() {
    const router = useRouter();
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isClearingChat, setIsClearingChat] = useState(false);
    const [authError, setAuthError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Check authentication on mount
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            router.push('/login');
            return;
        }

        // Display welcome message when component mounts and user is authenticated
        const welcomeMessage: Message = {
            id: Date.now(),
            text: "Hello! I'm your Socratic mentor. What would you like to explore today about your career path or personal interests?",
            sender: 'ai',
            timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputMessage.trim() || isTyping) return;

        const userMessage: Message = {
            id: Date.now(),
            text: inputMessage,
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsTyping(true);

        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                router.push('/login');
                return;
            }

            const response = await axios.post<ChatResponse>(
                `${cleanApiUrl}/chat/send`,
                { text: inputMessage },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                }
            );

            const aiMessage: Message = {
                id: Date.now() + 1,
                text: response.data.text,
                sender: 'ai',
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (error: unknown) {
            console.error('Error sending message:', error);
            if (error && typeof error === 'object' && 'response' in error && 
                typeof error.response === 'object' && error.response && 
                'status' in error.response && error.response.status === 401) {
                setAuthError('Your session has expired. Please log in again.');
                setTimeout(() => router.push('/login'), 2000);
            } else {
                setAuthError('An error occurred while sending your message. Please try again.');
            }
        } finally {
            setIsTyping(false);
        }
    };

    const handleClearChat = async () => {
        if (isClearingChat || messages.length === 0) return;
        setIsClearingChat(true);

        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                router.push('/login');
                return;
            }

            await axios.post(
                `${cleanApiUrl}/chat/clear`,
                {},
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                }
            );

            setMessages([]);
            const welcomeMessage: Message = {
                id: Date.now(),
                text: "Hello! I'm your Socratic mentor. What would you like to explore today about your career path or personal interests?",
                sender: 'ai',
                timestamp: new Date(),
            };
            setMessages([welcomeMessage]);
        } catch (error: unknown) {
            console.error('Error clearing chat:', error);
            if (error && typeof error === 'object' && 'response' in error && 
                typeof error.response === 'object' && error.response && 
                'status' in error.response && error.response.status === 401) {
                setAuthError('Your session has expired. Please log in again.');
                setTimeout(() => router.push('/login'), 2000);
            } else {
                setAuthError('An error occurred while clearing the chat. Please try again.');
            }
        } finally {
            setIsClearingChat(false);
        }
    };

    return (
        <>
            {/* Full-screen cinematic background */}
            <div
                className="fixed inset-0 z-0"
                style={{
                    background: `radial-gradient(circle at 80% center, #000000 0%, #000000 40%, #fdc500 60%, #ffd500 75%, #fffbe0 85%, #000000 100%)`
                }}
            ></div>

            {/* Grain texture overlay - blends with gradient */}
            <div
                className="fixed inset-0 z-0 pointer-events-none opacity-[0.03]"
                style={{
                    backgroundImage: `url('/patterns/realistic-grainy-texture-background/6497230.jpg')`,
                    backgroundSize: 'cover',
                    backgroundRepeat: 'no-repeat',
                    mixBlendMode: 'overlay'
                }}
            ></div>

            {/* Ambient glow layer */}
            <div
                className="fixed inset-0 z-0 pointer-events-none"
                style={{
                    background: `radial-gradient(circle at 70% center, rgba(253, 197, 0, 0.2) 0%, transparent 60%)`,
                    filter: 'blur(80px)'
                }}
            ></div>

            {/* Massive translucent watermark behind everything */}
            <div className="fixed inset-0 z-0 flex items-center justify-center pointer-events-none overflow-hidden">
                <div
                    className="text-[20vw] font-extrabold text-white opacity-[0.08] select-none whitespace-nowrap tracking-widest"
                    style={{
                        fontFamily: 'inherit',
                        filter: 'blur(1px)',
                        background: 'linear-gradient(90deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.5) 50%, rgba(255,255,255,0.2) 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                        textShadow: '0 0 20px rgba(255,255,255,0.1)'
                    }}
                >
                    NAVIGO
                </div>
            </div>

            {/* MainLayout with navigation */}
            <MainLayout>
                <div className="relative z-10 w-full h-[calc(100vh-4rem)]">
                    {/* Header with clear chat button */}
                    <div className="absolute top-6 right-6 z-20">
                        <button
                            onClick={handleClearChat}
                            disabled={isClearingChat || messages.length === 0}
                            className="px-4 py-2 bg-black/60 text-white rounded-lg backdrop-blur-sm hover:bg-black/80 transition-colors disabled:opacity-50 shadow-lg"
                        >
                            Clear Chat
                        </button>
                    </div>

                    {/* Auth Error */}
                    {authError && (
                        <div className="absolute top-6 left-6 right-24 z-20">
                            <div className="bg-red-900/80 border border-red-500 text-red-200 px-4 py-3 rounded-lg backdrop-blur-sm shadow-lg">
                                {authError}
                            </div>
                        </div>
                    )}

                    {/* Messages Area */}
                    <div className="absolute inset-x-0 top-20 bottom-32 z-10">
                        <div className="h-full overflow-y-auto px-6">
                            <div className="max-w-4xl mx-auto">
                                {messages.map((message) => (
                                    <div
                                        key={message.id}
                                        className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-6`}
                                    >
                                        <div className={`max-w-2xl ${message.sender === 'user' ? 'bg-black/80' : 'bg-white/90'} rounded-xl p-4 backdrop-blur-sm shadow-lg border border-white/10`}>
                                            <div className={`whitespace-pre-wrap ${message.sender === 'user' ? 'text-white' : 'text-black'}`}>
                                                {message.text}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {isTyping && (
                                    <div className="flex justify-start mb-6">
                                        <div className="bg-white/90 rounded-xl p-4 backdrop-blur-sm shadow-lg flex items-center space-x-2 border border-white/10">
                                            <div className="flex space-x-1">
                                                <div className="h-2 w-2 bg-gray-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                                <div className="h-2 w-2 bg-gray-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                                <div className="h-2 w-2 bg-gray-600 rounded-full animate-bounce"></div>
                                            </div>
                                            <span className="text-sm text-gray-600">Thinking...</span>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>
                        </div>
                    </div>

                    {/* Enhanced Chat Input */}
                    <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-20 w-full max-w-2xl px-6">
                        <form onSubmit={handleSubmit} className="relative">
                            <div
                                className="relative bg-black/80 rounded-xl shadow-lg backdrop-blur-sm border border-yellow-500/20"
                                style={{
                                    boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.3), 0 4px 20px rgba(0,0,0,0.4)'
                                }}
                            >
                                <input
                                    type="text"
                                    value={inputMessage}
                                    onChange={(e) => setInputMessage(e.target.value)}
                                    placeholder="I'm listening...."
                                    className="w-full px-6 py-4 pr-16 bg-transparent text-white placeholder-gray-400 border-none outline-none rounded-xl"
                                    disabled={isTyping}
                                />
                                <button
                                    type="submit"
                                    disabled={!inputMessage.trim() || isTyping}
                                    className="absolute right-3 top-1/2 transform -translate-y-1/2 w-10 h-10 bg-white rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                                >
                                    <svg
                                        className="w-5 h-5 text-black"
                                        viewBox="0 0 24 24"
                                        fill="currentColor"
                                    >
                                        <path d="M12 2l10 10-10 10v-6H2v-8h10V2z"/>
                                    </svg>
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </MainLayout>
        </>
    );
} 
