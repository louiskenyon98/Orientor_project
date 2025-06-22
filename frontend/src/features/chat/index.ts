// Chat feature exports with lazy loading support
import dynamic from 'next/dynamic';

// Regular exports for types and hooks
export * from './types/chat.types';
export * from './hooks/useChat';

// Component exports
export { MessageList } from './components/MessageList';
export { MessageInput } from './components/MessageInput';
export { ChatHeader } from './components/ChatHeader';

// Lazy loaded main component
export const ChatInterface = dynamic(
  () => import('./components/ChatInterface').then(mod => mod.ChatInterface),
  {
    loading: () => <div>Loading Chat...</div>,
    ssr: false
  }
);