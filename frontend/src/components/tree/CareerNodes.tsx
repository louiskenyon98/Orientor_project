import React, { useState, useRef } from 'react';
import { Handle, Position } from 'reactflow';
import { motion, AnimatePresence } from 'framer-motion';

// Animation variants for nodes - matches the CustomNodes.tsx animations
const nodeVariants = {
  hidden: { opacity: 0, scale: 0.85 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: { 
      type: 'spring',
      stiffness: 100,
      damping: 12,
      delay: 0.05
    }
  }
};

// Base node styles - common for career node types
const baseNodeStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  textAlign: 'center',
  borderRadius: '8px',
  padding: '12px 16px',
  minWidth: '120px',
  maxWidth: '160px',
  minHeight: '80px',
  fontSize: '14px',
  fontWeight: 500,
  lineHeight: 1.4,
  boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
  color: 'white',
  transition: 'box-shadow 0.2s ease, transform 0.1s ease',
  userSelect: 'none',
};

// Common interface for career node types
interface CareerNodeProps {
  data: {
    label: string;
    actions?: string[];
  };
  selected: boolean;
}

// Career Domain Node (Level 1)
export function CareerDomainNode({ data, selected }: CareerNodeProps) {
  const nodeStyle = { 
    ...baseNodeStyle,
    background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)', // Strong blue gradient
    color: 'white',
    borderRadius: '12px',
    fontSize: '16px',
    fontWeight: 600,
    padding: '16px 20px',
    minHeight: '90px',
    minWidth: '140px',
    boxShadow: selected 
      ? '0 0 0 2px #93c5fd, 0 4px 12px rgba(59, 130, 246, 0.35)' 
      : '0 4px 12px rgba(59, 130, 246, 0.25)',
  };
  
  return (
    <motion.div 
      style={nodeStyle}
      initial="hidden"
      animate="visible"
      variants={nodeVariants}
      whileHover={{ y: -2, scale: 1.02, boxShadow: '0 6px 15px rgba(59, 130, 246, 0.3)' }}
    >
      <div>{data.label}</div>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ background: '#bfdbfe', border: '2px solid #3b82f6', width: '8px', height: '8px' }}
      />
    </motion.div>
  );
}

// Career Family Node (Level 2)
export function CareerFamilyNode({ data, selected }: CareerNodeProps) {
  const nodeStyle = { 
    ...baseNodeStyle, 
    background: 'linear-gradient(135deg, #0f766e 0%, #0d9488 100%)', // Teal gradient
    color: 'white',
    minHeight: '80px',
    maxWidth: '150px',
    boxShadow: selected 
      ? '0 0 0 2px #99f6e4, 0 4px 12px rgba(13, 148, 136, 0.25)' 
      : '0 4px 12px rgba(13, 148, 136, 0.2)',
  };
  
  return (
    <motion.div 
      style={nodeStyle}
      initial="hidden"
      animate="visible"
      variants={nodeVariants}
      whileHover={{ y: -2, boxShadow: '0 6px 15px rgba(13, 148, 136, 0.25)' }}
    >
      <div>{data.label}</div>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ background: '#99f6e4', border: '2px solid #0d9488', width: '8px', height: '8px' }}
      />
      {/* Add source handle for future expansion to Level 3 if needed */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ background: '#99f6e4', border: '2px solid #0d9488', width: '8px', height: '8px' }}
      />
    </motion.div>
  );
}

// Optional: Career Specialization Node (Level 3) - Prepared for future expansion
export function CareerSpecializationNode({ data, selected }: CareerNodeProps) {
  const nodeStyle = { 
    ...baseNodeStyle, 
    background: 'linear-gradient(135deg, #7e22ce 0%, #a855f7 100%)', // Purple gradient
    color: 'white',
    minHeight: '70px',
    maxWidth: '140px',
    boxShadow: selected 
      ? '0 0 0 2px #d8b4fe, 0 4px 12px rgba(168, 85, 247, 0.25)' 
      : '0 4px 12px rgba(168, 85, 247, 0.2)',
  };
  
  return (
    <motion.div 
      style={nodeStyle}
      initial="hidden"
      animate="visible"
      variants={nodeVariants}
      whileHover={{ y: -2, boxShadow: '0 6px 15px rgba(168, 85, 247, 0.25)' }}
    >
      <div>{data.label}</div>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ background: '#d8b4fe', border: '2px solid #a855f7', width: '6px', height: '6px' }}
      />
    </motion.div>
  );
}

// Career Skill Node (Level 3)
export function CareerSkillNode({ data, selected }: CareerNodeProps) {
  const [showActions, setShowActions] = useState(false);
  const nodeRef = useRef<HTMLDivElement>(null);
  
  const nodeStyle = { 
    ...baseNodeStyle, 
    background: 'linear-gradient(135deg, #4c1d95 0%, #8b5cf6 100%)', // Purple gradient
    color: 'white',
    minHeight: '70px',
    maxWidth: '140px',
    boxShadow: selected 
      ? '0 0 0 2px #c4b5fd, 0 4px 12px rgba(124, 58, 237, 0.25)' 
      : '0 4px 12px rgba(124, 58, 237, 0.2)',
    cursor: 'pointer',
  };
  
  // Secondary text style (smaller text below main label)
  const secondaryTextStyle: React.CSSProperties = {
    fontSize: '12px',
    opacity: 0.9,
    marginTop: '6px',
    fontStyle: 'italic',
    fontWeight: 400,
  };
  
  // Extract action text if available
  const actionPreview = data.actions && data.actions.length > 0 
    ? data.actions[0].split(' ').slice(0, 3).join(' ') + '...'
    : null;
  
  return (
    <motion.div 
      ref={nodeRef}
      style={nodeStyle}
      initial="hidden"
      animate="visible"
      variants={nodeVariants}
      whileHover={{ y: -2, boxShadow: '0 6px 15px rgba(124, 58, 237, 0.25)' }}
      onClick={() => setShowActions(!showActions)}
    >
      <div>{data.label}</div>
      
      {/* Secondary small preview text */}
      {actionPreview && (
        <div style={secondaryTextStyle}>{actionPreview}</div>
      )}
      
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ background: '#c4b5fd', border: '2px solid #8b5cf6', width: '6px', height: '6px' }}
      />
      
      {/* Show actions panel when clicked */}
      <AnimatePresence>
        {showActions && data.actions && data.actions.length > 0 && (
          <motion.div
            className="w-full mt-4 bg-white rounded-lg p-4 shadow-lg border border-gray-200 text-gray-700 text-sm"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            style={{ overflow: 'hidden' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-3 pb-2 border-b border-gray-200">
              <h3 className="text-purple-600 font-semibold text-sm">Suggested Actions</h3>
              <button 
                onClick={(e) => { 
                  e.stopPropagation(); 
                  setShowActions(false); 
                }}
                className="text-gray-400 hover:text-gray-600 transition-colors text-xs"
              >
                ✕
              </button>
            </div>
            
            <ul className="space-y-2 list-disc list-inside">
              {data.actions.map((action, index) => (
                <li key={index} className="text-gray-600 text-xs">
                  {action}
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
} 