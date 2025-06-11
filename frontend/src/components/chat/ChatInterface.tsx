'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';
import ChatMessage from './ChatMessage';
import ConversationList from './ConversationList';
import ConversationManager from './ConversationManager';
import SearchInterface from './SearchInterface';
import CategoryManager from './CategoryManager';
import AnalyticsDashboard from './AnalyticsDashboard';
import { Menu, Search, Folder, BarChart3, Plus } from 'lucide-react';

interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  tokens_used?: number;
}

interface Conversation {
  id: number;
  title: string;
  auto_generated_title: boolean;
  category_id: number | null;
  is_favorite: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  last_message_at: string | null;
  message_count: number;
  total_tokens_used: number;
}

interface Category {
  id: number;
  name: string;
  description: string | null;
  color: string | null;
  conversation_count: number;
  created_at: string;
}

interface ChatInterfaceProps {
  currentUserId: number;
}

export default function ChatInterface({ currentUserId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showSearch, setShowSearch] = useState(false);
  const [showCategories, setShowCategories] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [sidebarView, setSidebarView] = useState<'conversations' | 'categories' | 'analytics'>('conversations');
  const [refreshConversationList, setRefreshConversationList] = useState(0);
  
  const router = useRouter();
  const searchParams = useSearchParams();
  const inputRef = useRef<HTMLInputElement>(null);

  // Load conversation when selected
  useEffect(() => {
    if (currentConversation) {
      loadConversationMessages();
    }
  }, [currentConversation?.id]);

  const loadConversationMessages = async () => {
    if (!currentConversation) {
      console.log('No current conversation to load messages for');
      return;
    }
    
    console.log('Loading messages for conversation:', currentConversation.id);
    
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}/messages`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      console.log('Messages API response:', response.data);
      
      // Handle both unified format {"messages": [...]} and legacy format [...]
      let messagesData;
      if (response.data.messages) {
        // Unified format from conversations_router  
        messagesData = response.data.messages;
        console.log('Using unified format - Number of messages loaded:', messagesData.length);
      } else if (Array.isArray(response.data)) {
        // Legacy format from chat_router (fallback)
        messagesData = response.data;
        console.log('Using legacy format - Number of messages loaded:', messagesData.length);
      } else {
        console.warn('Unexpected response format:', response.data);
        messagesData = [];
      }
      
      setMessages(messagesData);
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
      setMessages([]);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim() || isTyping) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    setIsTyping(true);
    const userMessage = inputText;
    setInputText('');

    try {
      // If no conversation exists, create one and wait for completion
      let conversationId = currentConversation?.id;
      let conversationToUse = currentConversation;
      
      console.log('handleSend - currentConversation:', currentConversation);
      console.log('handleSend - conversationId:', conversationId);
      
      if (!conversationId) {
        console.log('No conversation ID found, creating new conversation');
        const createResponse = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations`,
          {
            initial_message: userMessage,
            category_id: selectedCategory?.id
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        conversationId = createResponse.data.id;
        conversationToUse = createResponse.data;
        
        // Update state and wait for it to propagate  
        setCurrentConversation(conversationToUse);
        // Trigger conversation list refresh
        setRefreshConversationList(prev => prev + 1);
        
        // Small delay to ensure state has propagated
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Send message to existing conversation
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/send/${conversationId}`,
        {
          message: userMessage
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Add both user and assistant messages
      const newMessages: Message[] = [
        {
          id: response.data.user_message_id,
          role: 'user',
          content: userMessage,
          created_at: new Date().toISOString()
        },
        {
          id: response.data.assistant_message_id,
          role: 'assistant',
          content: response.data.response,
          created_at: new Date().toISOString(),
          tokens_used: response.data.tokens_used
        }
      ];
      
      setMessages(prev => [...prev, ...newMessages]);
    } catch (error: any) {
      console.error('Failed to send message:', error);
      
      if (error.response?.status === 401) {
        router.push('/login');
        return;
      }
      
      // Show error message
      const errorMsg: Message = {
        id: Date.now(),
        role: 'system',
        content: "Sorry, I'm having trouble connecting. Please try again.",
        created_at: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
      // Keep focus on input after sending message
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };

  const handleSelectConversation = (conversation: Conversation) => {
    setCurrentConversation(conversation);
    if (window.innerWidth < 768) {
      setShowSidebar(false);
    }
  };

  const handleCreateNewConversation = () => {
    setCurrentConversation(null);
    setMessages([]);
    setSelectedCategory(null);
    if (window.innerWidth < 768) {
      setShowSidebar(false);
    }
    // Focus on input for new conversation
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const handleSearchResult = (conversationId: number, messageId: number) => {
    // Load the conversation and scroll to the message
    axios.get(
      `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${conversationId}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    ).then(response => {
      setCurrentConversation(response.data);
      setShowSearch(false);
      
      // After messages load, scroll to the specific message
      setTimeout(() => {
        const messageElement = document.getElementById(`message-${messageId}`);
        if (messageElement) {
          messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          messageElement.classList.add('bg-yellow-100', 'dark:bg-yellow-900/20');
          setTimeout(() => {
            messageElement.classList.remove('bg-yellow-100', 'dark:bg-yellow-900/20');
          }, 2000);
        }
      }, 500);
    });
  };

  const handleArchiveConversation = async () => {
    if (!currentConversation) return;
    
    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}/archive`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      
      // Refresh conversation list
      window.location.reload();
    } catch (error) {
      console.error('Failed to archive conversation:', error);
    }
  };

  const handleDeleteConversation = async () => {
    if (!currentConversation) return;
    
    try {
      await axios.delete(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      
      setCurrentConversation(null);
      setMessages([]);
      window.location.reload();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  const handleTitleUpdate = (newTitle: string) => {
    if (currentConversation) {
      setCurrentConversation({ ...currentConversation, title: newTitle });
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] max-w-7xl mx-auto">
      {/* Sidebar */}
      <div className={`${showSidebar ? 'block' : 'hidden'} md:block w-80 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex flex-col`}>
        {/* Sidebar Navigation */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex space-x-1">
            <button
              onClick={() => setSidebarView('conversations')}
              className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                sidebarView === 'conversations'
                  ? 'bg-primary text-white'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              Chats
            </button>
            <button
              onClick={() => setSidebarView('categories')}
              className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                sidebarView === 'categories'
                  ? 'bg-primary text-white'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              Categories
            </button>
            <button
              onClick={() => setSidebarView('analytics')}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                sidebarView === 'analytics'
                  ? 'bg-primary text-white'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {/* Sidebar Content */}
        <div className="flex-1 overflow-y-auto">
          {sidebarView === 'conversations' && (
            <ConversationList
              selectedConversationId={currentConversation?.id}
              onSelectConversation={handleSelectConversation}
              onCreateNew={handleCreateNewConversation}
              refreshTrigger={refreshConversationList}
            />
          )}
          {sidebarView === 'categories' && (
            <div className="p-4">
              <CategoryManager
                selectedCategoryId={selectedCategory?.id}
                onSelectCategory={setSelectedCategory}
              />
            </div>
          )}
          {sidebarView === 'analytics' && (
            <AnalyticsDashboard />
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        {currentConversation ? (
          <ConversationManager
            conversationId={currentConversation.id}
            conversationTitle={currentConversation.title}
            isArchived={currentConversation.is_archived}
            onTitleUpdate={handleTitleUpdate}
            onArchive={handleArchiveConversation}
            onDelete={handleDeleteConversation}
            onRefresh={loadConversationMessages}
          />
        ) : (
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowSidebar(!showSidebar)}
                  className="md:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                >
                  <Menu className="w-5 h-5" />
                </button>
                <h2 className="text-lg font-medium">New Conversation</h2>
              </div>
              <button
                onClick={() => setShowSearch(!showSearch)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <Search className="w-5 h-5" />
              </button>
            </div>
            {selectedCategory && (
              <div className="mt-2 flex items-center gap-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Category:</span>
                <span 
                  className="px-2 py-1 rounded text-sm"
                  style={{ 
                    backgroundColor: `${selectedCategory.color}20`,
                    color: selectedCategory.color 
                  }}
                >
                  {selectedCategory.name}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
          
          {!messages || messages.filter(m => m.role !== 'system').length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <Plus className="w-16 h-16 mb-4 opacity-20" />
              <p className="text-lg mb-2">Start a new conversation</p>
              <p className="text-sm">Ask me anything about your career path!</p>
            </div>
          ) : (
            (messages || [])
              .filter(message => message.role !== 'system') // Filter out system messages
              .map((message) => (
                <div key={message.id} id={`message-${message.id}`} className="transition-colors">
                  <ChatMessage 
                    message={message.content}
                    type={message.role === 'user' ? 'user' : 'ai'}
                    userColor="bg-blue-500"
                    aiColor="bg-gray-100 dark:bg-gray-800"
                  />
                </div>
              ))
          )}
          {isTyping && (
            <ChatMessage 
              message="Thinking..."
              type="ai"
              userColor="bg-blue-500"
              aiColor="bg-gray-100 dark:bg-gray-800"
            />
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-3 md:p-4 bg-white dark:bg-gray-900">
          <div className="flex items-center space-x-2">
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isTyping && handleSend()}
              placeholder="Type your message..."
              className="flex-1 p-3 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isTyping}
            />
            <button 
              onClick={handleSend}
              disabled={!inputText.trim() || isTyping}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 h-[46px] min-w-[80px] rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
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

      {/* Search Modal */}
      {showSearch && (
        <SearchInterface
          onSelectResult={handleSearchResult}
          onClose={() => setShowSearch(false)}
        />
      )}
    </div>
  );
}