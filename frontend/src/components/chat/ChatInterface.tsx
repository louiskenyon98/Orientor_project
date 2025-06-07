'use client';// frontend/src/components/chat/Chatinterface.tsx
// frontend/src/components/chat/Chatinterface.tsx

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import ChatMessage from './ChatMessage';

interface Message {
  text: string;
  type: 'user' | 'ai';
  id: number;
  timestamp: Date;
}

interface ChatResponse {
  text: string;
}

export default function Chatinterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check authentication and show welcome message
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Display welcome message when component mounts
    const welcomeMessage: Message = {
      id: Date.now(),
      text: "Hello! I'm your Career Advisor. How can I help you today?",
      type: 'ai',
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, [router]);

  const handleSend = async () => {
    if (!inputText.trim() || isTyping) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    const newMessage: Message = {
      id: Date.now(),
      text: inputText,
      type: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      const response = await axios.post<ChatResponse>(
        'http://localhost:8000/chat/send',
        { text: newMessage.text },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      const aiMessage: Message = {
        id: Date.now(),
        text: response.data.text,
        type: 'ai',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error: any) {
      console.error('Failed to get AI response:', error);
      
      let errorMessage = "Sorry, I'm having trouble connecting to my brain right now. Please try again later.";
      
      if (error.response?.status === 401) {
        router.push('/login');
        return;
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      const errorMsg: Message = {
        id: Date.now(),
        text: errorMessage,
        type: 'ai',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
      // Focus back on input after message is sent
      inputRef.current?.focus();
    }
  };

  return (
    <div className="premium-card flex flex-col h-[calc(100vh-12rem)] md:h-[600px] max-w-4xl mx-auto">
      <div className="px-4 py-3 border-b border-theme-border">
        <h2 className="text-lg font-medium text-theme-text">Career Advisor Chat</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 scroll-smooth">
        {messages.map((message) => (
          <ChatMessage 
            key={message.id}
            message={message.text}
            type={message.type}
            userColor="bg-theme-accent"
            aiColor="bg-theme-card"
          />
        ))}
        {isTyping && (
          <ChatMessage 
            message="Typing..."
            type="ai"
            userColor="bg-theme-accent"
            aiColor="bg-theme-card"
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-theme-border p-3 md:p-4">
        <div className="flex items-center space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !isTyping && handleSend()}
            placeholder="Type your message..."
            className="flex-1 p-3 rounded-lg bg-theme-card border border-theme-border text-theme-text placeholder-theme-text-secondary focus:outline-none focus:ring-2 focus:ring-theme-accent focus:border-transparent"
            disabled={isTyping}
          />
          <button 
            onClick={handleSend}
            disabled={!inputText.trim() || isTyping}
            className="bg-theme-accent hover:bg-theme-accent-secondary text-theme-text px-4 py-3 h-[46px] min-w-[80px] rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            aria-label="Send message"
          >
            <span className="hidden xs:inline">Send</span>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 xs:ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}