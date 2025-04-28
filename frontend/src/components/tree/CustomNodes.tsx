import React, { useState } from 'react';
import { Handle, Position } from 'reactflow';
import { getNodeStyle } from '../../utils/convertToFlowGraph';

// Base node styles
const baseNodeStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  textAlign: 'center',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  minHeight: '40px',
  cursor: 'pointer',
};

// Common component for all node types
interface NodeProps {
  data: {
    label: string;
    nodeType: string;
    actions?: string[];
  };
}

// Root Node Component
export function RootNode({ data }: NodeProps) {
  const nodeStyle = { ...baseNodeStyle, ...getNodeStyle('root') };
  
  return (
    <div style={nodeStyle}>
      <div>{data.label}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Skill Node Component with Actions Popover
export function SkillNode({ data }: NodeProps) {
  const [showActions, setShowActions] = useState(false);
  const nodeStyle = { ...baseNodeStyle, ...getNodeStyle('skill') };
  
  return (
    <>
      <div 
        style={nodeStyle} 
        onClick={() => setShowActions(!showActions)}
      >
        <div>{data.label}</div>
        <Handle type="target" position={Position.Top} />
        <Handle type="source" position={Position.Bottom} />
      </div>
      
      {showActions && data.actions && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'white',
          padding: '10px',
          borderRadius: '5px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          zIndex: 1000,
          width: '200px',
          marginTop: '10px',
        }}>
          <h3 style={{ 
            margin: '0 0 10px 0', 
            fontSize: '14px', 
            fontWeight: 'bold',
            color: '#3b82f6'
          }}>
            Actions
          </h3>
          <ul style={{ 
            listStyleType: 'disc', 
            paddingLeft: '20px',
            margin: 0,
            fontSize: '12px'
          }}>
            {data.actions.map((action, index) => (
              <li key={index} style={{ marginBottom: '5px' }}>{action}</li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}

// Outcome Node Component
export function OutcomeNode({ data }: NodeProps) {
  const nodeStyle = { ...baseNodeStyle, ...getNodeStyle('outcome') };
  
  return (
    <div style={nodeStyle}>
      <div>{data.label}</div>
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Career Node Component
export function CareerNode({ data }: NodeProps) {
  const nodeStyle = { ...baseNodeStyle, ...getNodeStyle('career') };
  
  return (
    <div style={nodeStyle}>
      <div>🏁 {data.label}</div>
      <Handle type="target" position={Position.Top} />
    </div>
  );
} 