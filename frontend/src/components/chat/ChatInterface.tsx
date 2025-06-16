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
import styles from './ChatBot.module.css';

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
  const [showSidebar, setShowSidebar] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [showCategories, setShowCategories] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [sidebarView, setSidebarView] = useState<'conversations' | 'categories' | 'analytics'>('conversations');
  const [refreshConversationList, setRefreshConversationList] = useState(0);
  const [chatStarted, setChatStarted] = useState(false);
  const [showConversations, setShowConversations] = useState(false);
  
  const router = useRouter();
  const searchParams = useSearchParams();
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Load conversation when selected
  useEffect(() => {
    if (currentConversation) {
      loadConversationMessages();
      setChatStarted(true); // Show full chat interface when conversation is loaded
    }
  }, [currentConversation?.id]);

  // Check if chat should be started based on messages
  useEffect(() => {
    if (messages && messages.filter(m => m.role !== 'system').length > 0) {
      setChatStarted(true);
    }
  }, [messages]);

  // Handle initial message from URL parameters
  useEffect(() => {
    const initialMessage = searchParams.get('initial_message');
    const messageType = searchParams.get('type');
    
    if (initialMessage && !currentConversation && messages.length === 0) {
      // Decode the message and set it as the input text
      const decodedMessage = decodeURIComponent(initialMessage);
      setInputText(decodedMessage);
      setChatStarted(true);
      
      // Focus the input field
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 100);
    }
  }, [searchParams, currentConversation, messages.length]);

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
      setChatStarted(true); // Transition to full chat interface after sending first message
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
    setShowSidebar(false); // Always hide sidebar when selecting conversation
  };

  const handleCreateNewConversation = () => {
    setCurrentConversation(null);
    setMessages([]);
    setSelectedCategory(null);
    setChatStarted(false); // Reset to initial state
    setShowConversations(false);
    setShowSidebar(false); // Always hide sidebar when creating new conversation
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

  if (!chatStarted && !currentConversation) {
    // Initial state - centered chat interface
    return (
      <div className="flex h-[calc(100vh-4rem)] relative">
        {/* Conversations Sidebar - Slides in from left */}
        <div className={`absolute left-0 top-0 h-full w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ease-in-out z-10 ${
          showConversations ? 'translate-x-0' : '-translate-x-full'
        }`}>
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Conversations</h3>
              <button
                onClick={() => setShowConversations(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                ×
              </button>
            </div>
          </div>
          <ConversationList
            selectedConversationId={currentConversation?.id}
            onSelectConversation={handleSelectConversation}
            onCreateNew={handleCreateNewConversation}
            refreshTrigger={refreshConversationList}
          />
        </div>

        {/* Main centered content */}
        <div className="flex-1 flex flex-col items-center justify-center p-8">
          {/* NAVIGO Title with Gradient */}
          <div className="mb-12 text-center">
            <h1 className="text-6xl md:text-8xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent mb-4">
              NAVIGO
            </h1>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Your AI career guidance companion
            </p>
          </div>

          {/* Chat Interface Container */}
          <div className={styles.container_chat_bot}>
            <div className={styles['container-chat-options']}>
              <div className={styles.chat}>
                <div className={styles['chat-bot']}>
                  <textarea
                    ref={inputRef}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && !isTyping && (e.preventDefault(), handleSend())}
                    placeholder="Ask me anything about your career path..."
                    disabled={isTyping}
                  />
                </div>
                <div className={styles.options}>
                  <div className={styles['btns-add']}>
                    <button
                      onClick={() => setShowConversations(true)}
                      className="flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                        <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
                      </svg>
                      <span className="text-xs">History</span>
                    </button>
                  </div>
                  <button
                    onClick={handleSend}
                    disabled={!inputText.trim() || isTyping}
                    className={styles['btn-submit']}
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Overlay when conversations are shown */}
        {showConversations && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-5"
            onClick={() => setShowConversations(false)}
          />
        )}
      </div>
    );
  }

  // Full chat interface after first message
  return (
    <div className="flex h-[calc(100vh-4rem)] max-w-7xl mx-auto relative">
      {/* Sidebar - Hidden by default, slides in when shown */}
      <div className={`absolute left-0 top-0 h-full w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ease-in-out z-20 ${
        showSidebar ? 'translate-x-0' : '-translate-x-full'
      } flex flex-col`}>
        {/* Sidebar Navigation */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Chat Menu</h3>
            <button
              onClick={() => setShowSidebar(false)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              ×
            </button>
          </div>
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

      {/* Overlay when sidebar is shown */}
      {showSidebar && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-10"
          onClick={() => setShowSidebar(false)}
        />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col w-full">
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
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
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
          {(messages || [])
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
            ))}
          {isTyping && (
            <ChatMessage 
              message="Thinking..."
              type="ai"
              userColor="bg-blue-500"
              aiColor="bg-gray-100 dark:bg-gray-800"
            />
          )}
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-3 md:p-4 bg-white dark:bg-gray-900">
          <div className="flex items-center space-x-2">
            <textarea
              ref={inputRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && !isTyping && (e.preventDefault(), handleSend())}
              placeholder="Type your message..."
              className="flex-1 p-3 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows="1"
              disabled={isTyping}
            />
            <button 
              onClick={handleSend}
              disabled={!inputText.trim() || isTyping}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 min-w-[80px] rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
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