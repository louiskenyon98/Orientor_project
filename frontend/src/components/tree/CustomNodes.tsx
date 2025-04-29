import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position } from 'reactflow';
import { motion, AnimatePresence } from 'framer-motion';

// Animation variants for nodes
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

// Animation variants for popover
const popoverVariants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: { 
      type: 'spring',
      stiffness: 200,
      damping: 15,
    }
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    transition: {
      duration: 0.15
    }
  }
};

// Base node styles - common for all nodes
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

// Style for the popover container
const popoverContainerStyle: React.CSSProperties = {
  position: 'absolute',
  backgroundColor: 'white',
  padding: '20px',
  borderRadius: '10px',
  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.15)',
  zIndex: 1000,
  width: '280px',
  maxWidth: '400px',
  border: '1px solid rgba(0, 0, 0, 0.05)',
  backdropFilter: 'blur(8px)',
  lineHeight: 1.6
};

// Common component for all node types
interface NodeProps {
  data: {
    label: string;
    nodeType: string;
    actions?: string[];
  };
  id: string;
  selected: boolean;
}

// Root Node Component
export function RootNode({ data, selected }: NodeProps) {
  const nodeStyle = { 
    ...baseNodeStyle,
    background: 'linear-gradient(135deg, #0f2c61 0%, #2563eb 100%)', // Dark blue gradient
    color: 'white',
    borderRadius: '12px',
    fontSize: '16px',
    fontWeight: 600,
    padding: '16px 20px',
    minHeight: '80px',
    boxShadow: selected 
      ? '0 0 0 2px #93c5fd, 0 4px 12px rgba(29, 78, 216, 0.35)' 
      : '0 4px 12px rgba(29, 78, 216, 0.25)',
  };
  
  return (
    <motion.div 
      style={nodeStyle}
      initial="hidden"
      animate="visible"
      variants={nodeVariants}
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

// Skill Node Component with Actions Tooltip
export function SkillNode({ data, id, selected }: NodeProps) {
  const [showActions, setShowActions] = useState(false);
  const nodeRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  
  const nodeStyle = { 
    ...baseNodeStyle, 
    background: 'linear-gradient(135deg, #0f4c81 0%, #0ea5e9 100%)', // Blue gradient like the screenshot
    color: 'white',
    minHeight: '90px',
    maxWidth: '150px',
    boxShadow: selected 
      ? '0 0 0 2px #bae6fd, 0 4px 12px rgba(3, 105, 161, 0.25)' 
      : '0 4px 12px rgba(3, 105, 161, 0.2)',
    cursor: 'pointer',
    position: 'relative', // Needed for proper tooltip positioning
  };

  // Secondary text style (smaller text below main label)
  const secondaryTextStyle: React.CSSProperties = {
    fontSize: '12px',
    opacity: 0.9,
    marginTop: '6px',
    fontStyle: 'italic',
    fontWeight: 400,
  };

  // Calculate tooltip position
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0, placement: 'right' });

  useEffect(() => {
    if (showActions && nodeRef.current) {
      const nodeRect = nodeRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      
      // Default to right placement
      let placement = 'right';
      let x = nodeRect.right + 16; // 16px gap
      let y = nodeRect.top + (nodeRect.height / 2);
      
      // If not enough space on the right, try left
      if (x + 280 > viewportWidth) { // 280px is approx tooltip width
        placement = 'left';
        x = nodeRect.left - 16;
      }
      
      setTooltipPosition({ x, y, placement });
    }
  }, [showActions]);

  // Close tooltip when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        nodeRef.current && 
        tooltipRef.current && 
        !nodeRef.current.contains(event.target as Node) && 
        !tooltipRef.current.contains(event.target as Node)
      ) {
        setShowActions(false);
      }
    };
    
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setShowActions(false);
      }
    };
    
    if (showActions) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscKey);
    }
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [showActions]);

  // Extract action text if available
  const actionPreview = data.actions && data.actions.length > 0 
    ? data.actions[0].split(' ').slice(0, 3).join(' ') + '...'
    : null;
  
    return (
      <motion.div 
        ref={nodeRef}
        style={{ ...nodeStyle, position: 'relative' }}
        onClick={() => setShowActions(!showActions)}
        initial="hidden"
        animate="visible"
        variants={nodeVariants}
        whileHover={{ y: -2, boxShadow: '0 6px 15px rgba(3, 105, 161, 0.25)' }}
      >
        {/* Node Label */}
        <div>{data.label}</div>
    
        {/* Secondary small preview text */}
        {actionPreview && (
          <div style={secondaryTextStyle}>{actionPreview}</div>
        )}
    
        {/* Handles */}
        <Handle 
          type="target" 
          position={Position.Top} 
          style={{ background: '#bae6fd', border: '2px solid #0ea5e9', width: '8px', height: '8px' }}
        />
        <Handle 
          type="source" 
          position={Position.Bottom} 
          style={{ background: '#bae6fd', border: '2px solid #0ea5e9', width: '8px', height: '8px' }}
        />
    
        {/* Recommended Actions Panel INSIDE node */}
        <AnimatePresence>
          {showActions && data.actions && data.actions.length > 0 && (
            <motion.div
              className="w-full mt-4 bg-white rounded-lg p-4 shadow-lg border border-gray-200 text-gray-700 text-sm"
              initial="hidden"
              animate="visible"
              exit="exit"
              variants={popoverVariants}
              style={{
                overflow: 'hidden',
                minWidth: '280px',
                maxWidth: '400px',
                lineHeight: 1.6,
              }}
            >
              <div className="flex justify-between items-center mb-3 pb-2 border-b border-gray-200">
                <h3 className="text-blue-600 font-semibold text-sm">Recommended Actions</h3>
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

// Outcome Node Component
export function OutcomeNode({ data, selected }: NodeProps) {
  const nodeStyle = { 
    ...baseNodeStyle, 
    background: 'white',
    color: '#334155',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    minHeight: '70px',
    fontSize: '14px',
    fontWeight: 600,
    boxShadow: selected 
      ? '0 0 0 2px #bae6fd, 0 4px 12px rgba(226, 232, 240, 0.6)' 
      : '0 3px 10px rgba(226, 232, 240, 0.4)',
  };

  // Title style
  const titleStyle: React.CSSProperties = {
    fontWeight: 600,
    marginBottom: '6px',
    color: '#1e293b',
  };

  // Content style
  const contentStyle: React.CSSProperties = {
    fontSize: '12px',
    color: '#64748b',
    fontWeight: 400,
  };
  
  // Parse outcome content (typically has a title and description)
  const parsedLabel = data.label.split('in');
  const title = parsedLabel.length > 1 ? 'Outcome' : data.label;
  const content = parsedLabel.length > 1 ? parsedLabel.slice(1).join('in') : null;
  
  return (
    <motion.div 
      style={nodeStyle}
      initial="hidden"
      animate="visible"
      variants={nodeVariants}
      whileHover={{ y: -2, boxShadow: '0 6px 15px rgba(226, 232, 240, 0.6)' }}
    >
      <div style={titleStyle}>{title}</div>
      {content && <div style={contentStyle}>{content}</div>}
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ background: '#e2e8f0', border: '1px solid #94a3b8', width: '6px', height: '6px' }}
      />
      <Handle 
        type="source" 
        position={Position.Bottom}
        style={{ background: '#e2e8f0', border: '1px solid #94a3b8', width: '6px', height: '6px' }}
      />
    </motion.div>
  );
}

// Career Node Component
export function CareerNode({ data, selected }: NodeProps) {
  const nodeStyle = { 
    ...baseNodeStyle, 
    background: 'linear-gradient(135deg, #b45309 0%, #fcd34d 100%)', // Gold/orange gradient
    color: 'white',
    minHeight: '80px',
    maxWidth: '160px',
    boxShadow: selected 
      ? '0 0 0 2px #fcd34d, 0 4px 12px rgba(217, 119, 6, 0.25)' 
      : '0 4px 12px rgba(217, 119, 6, 0.2)',
  };
  
  return (
    <motion.div 
      style={nodeStyle}
      initial="hidden"
      animate="visible"
      variants={nodeVariants}
      whileHover={{ y: -2, boxShadow: '0 6px 15px rgba(217, 119, 6, 0.25)' }}
    >
      <div>{data.label}</div>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ background: '#fef3c7', border: '2px solid #f59e0b', width: '6px', height: '6px' }}
      />
    </motion.div>
  );
}
