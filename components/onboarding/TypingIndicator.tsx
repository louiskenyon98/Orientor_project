'use client';

import React from 'react';
import { motion } from 'framer-motion';

const TypingIndicator: React.FC = () => {
  return (
    <div className="typing-indicator" data-testid="typing-indicator">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="typing-dot"
          animate={{
            opacity: [0.4, 1, 0.4],
            scale: [0.8, 1, 0.8]
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            delay: i * 0.2,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  );
};

export default TypingIndicator;