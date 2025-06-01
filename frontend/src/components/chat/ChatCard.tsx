import React from 'react';
import { motion } from 'framer-motion';

interface ChatCardProps {
  children: React.ReactNode;
  className?: string;
}

export default function ChatCard({ children, className = '' }: ChatCardProps) {
  return (
    <motion.div 
      className={`w-[190px] h-[254px] rounded-[30px] bg-[#e0e0e0] shadow-[15px_15px_30px_#bebebe,-15px_-15px_30px_#ffffff] overflow-hidden ${className}`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="h-full overflow-y-auto p-4 space-y-3">
        {children}
      </div>
    </motion.div>
  );
} 