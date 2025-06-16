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

// Paper Chat Message Component - mimics writing on paper
interface PaperChatMessageProps {
  message: Message;
  isLast: boolean;
}

const PaperChatMessage: React.FC<PaperChatMessageProps> = ({ message, isLast }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className="space-y-4">
      {/* AI/System message with elegant blue accent */}
      {!isUser && (
        <div className="border-l-3 border-blue-500 pl-8 py-2">
          <p className="text-xl leading-relaxed text-blue-600 font-light tracking-wide">
            {message.content}
          </p>
        </div>
      )}
      
      {/* User message as elegant plain text */}
      {isUser && (
        <div className="pl-4 py-1">
          <p className="text-xl leading-relaxed text-gray-800 font-light tracking-wide">
            {message.content}
          </p>
        </div>
      )}
    </div>
  );
};

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
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editingTitleValue, setEditingTitleValue] = useState('');
  
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

  const handleTitleEdit = () => {
    if (currentConversation) {
      setEditingTitleValue(currentConversation.title);
      setIsEditingTitle(true);
    }
  };

  const handleTitleSave = async () => {
    if (!currentConversation || !editingTitleValue.trim()) {
      setIsEditingTitle(false);
      setEditingTitleValue('');
      return;
    }

    const newTitle = editingTitleValue.trim();
    if (newTitle === currentConversation.title) {
      setIsEditingTitle(false);
      setEditingTitleValue('');
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({ title: newTitle })
        }
      );

      console.log('Title update response status:', response.status);
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('Title update response data:', responseData);
        
        // Update local state
        setCurrentConversation({ ...currentConversation, title: newTitle });
        setIsEditingTitle(false);
        setEditingTitleValue('');
        
        // Trigger conversation list refresh to show updated title
        setRefreshConversationList(prev => prev + 1);
        
        console.log('Title successfully updated to:', newTitle);
      } else {
        const errorData = await response.text();
        console.error('Failed to update title. Status:', response.status, 'Response:', errorData);
        throw new Error(`HTTP ${response.status}: ${errorData}`);
      }
      
    } catch (error) {
      console.error('Failed to update conversation title:', error);
      
      // Revert to original title on error
      setIsEditingTitle(false);
      setEditingTitleValue('');
      
      // Show error message to user
      alert('Failed to update conversation title. Please try again.');
    }
  };

  if (!chatStarted && !currentConversation) {
    // Paper-like initial state
    return (
      <div className="min-h-screen bg-white flex flex-col">
        {/* Header with conversations history icon */}
        <div className="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-gray-100 p-6">
          <div className="flex items-center justify-between max-w-4xl mx-auto">
            <div className="flex-1">
              <h1 className="text-2xl font-light text-gray-800 tracking-wide">Chat</h1>
            </div>
            <button
              onClick={() => setShowConversations(true)}
              className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-full hover:bg-blue-50"
              title="View conversation history"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </button>
          </div>
        </div>

        {/* Paper-like Chat Interface */}
        <div className="flex-1 overflow-y-auto px-8 py-12">
          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              {/* Welcome prompt */}
              <div className="border-l-3 border-blue-500 pl-8 py-2">
                <p className="text-xl leading-relaxed text-blue-600 font-light tracking-wide">
                  What would you like to talk about today?
                </p>
              </div>
              
              {/* Paper-like input area */}
              <div className="pl-4 py-2">
                <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="w-full">
                  <textarea
                    ref={inputRef}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Write here.."
                    className="w-full text-xl leading-relaxed text-gray-800 placeholder-gray-300 
                      bg-transparent border-none outline-none resize-none font-light tracking-wide
                      focus:text-gray-900 transition-all duration-300 min-h-[2.5rem]
                      focus:placeholder-gray-200 focus:outline-none focus:ring-0 focus:border-none"
                    rows={1}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                      }
                      // Auto-resize textarea
                      const target = e.target as HTMLTextAreaElement;
                      target.style.height = 'auto';
                      target.style.height = `${target.scrollHeight}px`;
                    }}
                    onInput={(e) => {
                      // Auto-resize textarea
                      const target = e.target as HTMLTextAreaElement;
                      target.style.height = 'auto';
                      target.style.height = `${target.scrollHeight}px`;
                    }}
                    disabled={isTyping}
                    autoFocus
                    style={{ minHeight: '2.5rem' }}
                  />
                </form>
              </div>
            </div>
          </div>
        </div>

        {/* Conversations History Popup */}
        {showConversations && (
          <>
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 z-40"
              onClick={() => setShowConversations(false)}
            />
            <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 max-w-90vw max-h-80vh bg-white rounded-lg shadow-xl z-50 overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-800">Conversation History</h3>
                  <button
                    onClick={() => setShowConversations(false)}
                    className="p-1 text-gray-400 hover:text-gray-600 rounded"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <div className="p-4 max-h-96 overflow-y-auto">
                <ConversationList
                  selectedConversationId={currentConversation?.id}
                  onSelectConversation={(conversation) => {
                    handleSelectConversation(conversation);
                    setShowConversations(false);
                  }}
                  onCreateNew={() => {
                    handleCreateNewConversation();
                    setShowConversations(false);
                  }}
                  refreshTrigger={refreshConversationList}
                />
              </div>
            </div>
          </>
        )}
      </div>
    );
  }

  // Paper-like full chat interface
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header with conversations history icon */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-gray-100 p-6">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex-1">
            {isEditingTitle ? (
              <input
                type="text"
                value={editingTitleValue}
                onChange={(e) => setEditingTitleValue(e.target.value)}
                onBlur={handleTitleSave}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleTitleSave();
                  } else if (e.key === 'Escape') {
                    setIsEditingTitle(false);
                    setEditingTitleValue('');
                  }
                }}
                className="text-2xl font-light text-gray-800 tracking-wide bg-transparent border-none outline-none focus:outline-none focus:ring-0 focus:border-none w-full"
                autoFocus
              />
            ) : (
              <h1 
                className="text-2xl font-light text-gray-800 tracking-wide cursor-pointer hover:text-blue-600 hover:bg-blue-50 px-2 py-1 rounded transition-all duration-200"
                onClick={handleTitleEdit}
                title="Click to edit conversation name"
              >
                {currentConversation?.title || 'Chat'}
                <span className="ml-2 text-gray-400 opacity-0 hover:opacity-100 transition-opacity text-sm">✏️</span>
              </h1>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowConversations(true)}
              className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-full hover:bg-blue-50"
              title="View conversation history"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </button>
            <button
              onClick={handleCreateNewConversation}
              className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-full hover:bg-blue-50"
              title="New conversation"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Paper-like Messages Area */}
      <div className="flex-1 overflow-y-auto px-8 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="space-y-8">
            {(messages || [])
              .filter(message => message.role !== 'system')
              .map((message, index) => (
                <PaperChatMessage 
                  key={message.id} 
                  message={message}
                  isLast={index === messages.length - 1}
                />
              ))}
            
            {isTyping && (
              <div className="border-l-3 border-blue-500 pl-8 py-2">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-blue-500 text-sm font-light">Thinking...</span>
                </div>
              </div>
            )}

            {/* Inline input for continuing conversation */}
            <div className="pl-4 py-2">
              <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="w-full">
                <textarea
                  ref={inputRef}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Continue writing.."
                  className="w-full text-xl leading-relaxed text-gray-800 placeholder-gray-300 
                    bg-transparent border-none outline-none resize-none font-light tracking-wide
                    focus:text-gray-900 transition-all duration-300 min-h-[2.5rem]
                    focus:placeholder-gray-200 focus:outline-none focus:ring-0 focus:border-none"
                  rows={1}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                    // Auto-resize textarea
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = `${target.scrollHeight}px`;
                  }}
                  onInput={(e) => {
                    // Auto-resize textarea
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = `${target.scrollHeight}px`;
                  }}
                  disabled={isTyping}
                  style={{ minHeight: '2.5rem' }}
                />
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* Conversations History Popup */}
      {showConversations && (
        <>
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setShowConversations(false)}
          />
          <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 max-w-90vw max-h-80vh bg-white rounded-lg shadow-xl z-50 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-800">Conversation History</h3>
                <button
                  onClick={() => setShowConversations(false)}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="p-4 max-h-96 overflow-y-auto">
              <ConversationList
                selectedConversationId={currentConversation?.id}
                onSelectConversation={(conversation) => {
                  handleSelectConversation(conversation);
                  setShowConversations(false);
                }}
                onCreateNew={() => {
                  handleCreateNewConversation();
                  setShowConversations(false);
                }}
                refreshTrigger={refreshConversationList}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}