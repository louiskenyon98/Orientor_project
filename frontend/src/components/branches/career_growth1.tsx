import ReactFlow, {   Background, Controls,MarkerType, useNodesState, useEdgesState} from 'reactflow';
import 'reactflow/dist/style.css';
import { useCallback, useState } from 'react';
import type { Node, Edge } from 'reactflow';

const Tooltip = ({ text, tip }: { text: string; tip?: string }) => (
  <div className="relative group cursor-help">
    <span>{text}</span>
    {tip && (
      <div className="absolute hidden group-hover:block bg-gray-800 text-white text-xs rounded px-2 py-1 bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-50 whitespace-nowrap">
        {tip}
      </div>
    )}
  </div>
);

const initialNodes: Node[] = [
  { id: 'root', position: { x: 320, y: 700 }, data: { label: <Tooltip text="You are here" /> }, type: 'input' },

  { id: 'writing', position: { x: 100, y: 1000 }, data: { label: <Tooltip text="Writing" tip="💡 Read: 'On Writing' by Stephen King" /> }, type: 'default', style: { background: '#2563eb', color: '#fff', borderRadius: '50%' } },
  { id: 'analyticalThinking', position: { x: 320, y: 1000 }, data: { label: <Tooltip text="Analytical Thinking" tip="💡 Read: 'Thinking in Systems' by Donella Meadows" /> }, type: 'default', style: { background: '#2563eb', color: '#fff', borderRadius: '50%' } },
  { id: 'publicSpeaking', position: { x: 540, y: 1000 }, data: { label: <Tooltip text="Public Speaking" tip="💡 Watch: TEDx Talk by Julian Treasure" /> }, type: 'default', style: { background: '#2563eb', color: '#fff', borderRadius: '50%' } },

  { id: 'contentStrategy', position: { x: 100, y: 500 }, data: { label: <Tooltip text="Content Strategy" tip="💡 Read: 'Everybody Writes' by Ann Handley" /> }, type: 'default', style: { background: '#2563eb', color: '#fff', borderRadius: '50%' } },
  { id: 'sql', position: { x: 320, y: 500 }, data: { label: <Tooltip text="SQL" tip="💡 Practice: SQLZoo.net" /> }, type: 'default', style: { background: '#2563eb', color: '#fff', borderRadius: '50%' } },
  { id: 'storyMapping', position: { x: 320, y: 400 }, data: { label: <Tooltip text="Story Mapping" tip="💡 Read: 'User Story Mapping' by Jeff Patton" /> }, type: 'default', style: { background: '#14b8a6', color: '#fff', borderRadius: '50%' } },
  { id: 'dataViz', position: { x: 320, y: 450 }, data: { label: <Tooltip text="Data Visualization" tip="💡 Book: 'Storytelling with Data'" /> }, type: 'default', style: { background: '#2563eb', color: '#fff', borderRadius: '50%' } },
  { id: 'userPsychology', position: { x: 540, y: 300 }, data: { label: <Tooltip text="User Psychology" tip="💡 Take: Intro to Psychology (Coursera)" /> }, type: 'default', style: { background: '#14b8a6', color: '#fff', borderRadius: '50%' } },

  { id: 'contentStrategist', position: { x: 60, y: 300 }, data: { label: <Tooltip text="Content Strategist" /> }, type: 'output', style: { background: '#9333ea', color: '#fff', borderRadius: '10%' } },
  { id: 'uxContentDesigner', position: { x: 140, y: 300 }, data: { label: <Tooltip text="UX Content Designer" /> }, type: 'output', style: { background: '#9333ea', color: '#fff', borderRadius: '10%' } },
  { id: 'dataAnalyst', position: { x: 260, y: 200 }, data: { label: <Tooltip text="Data Analyst" /> }, type: 'output', style: { background: '#9333ea', color: '#fff', borderRadius: '10%' } },
  { id: 'behavioralResearcher', position: { x: 380, y: 200 }, data: { label: <Tooltip text="Behavioral Researcher" /> }, type: 'output', style: { background: '#9333ea', color: '#fff', borderRadius: '10%' } },
  { id: 'productEvangelist', position: { x: 460, y: 150 }, data: { label: <Tooltip text="Product Evangelist" /> }, type: 'output', style: { background: '#9333ea', color: '#fff', borderRadius: '10%' } },
  { id: 'workshopFacilitator', position: { x: 540, y: 150 }, data: { label: <Tooltip text="Workshop Facilitator" /> }, type: 'output', style: { background: '#9333ea', color: '#fff', borderRadius: '10%' } },
  { id: 'designStrategist', position: { x: 100, y: 200 }, data: { label: <Tooltip text="Design Strategist" /> }, type: 'output', style: { background: '#c084fc', color: '#fff', borderRadius: '10%' } },
  { id: 'policyAdvisor', position: { x: 540, y: 50 }, data: { label: <Tooltip text="Policy Advisor" /> }, type: 'output', style: { background: '#c084fc', color: '#fff', borderRadius: '10%' } },
];

const edges: Edge[] = [
  { id: 'e0', source: 'root', target: 'writing', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e1', source: 'root', target: 'analyticalThinking', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e2', source: 'root', target: 'publicSpeaking', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e3', source: 'writing', target: 'contentStrategy', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e4', source: 'contentStrategy', target: 'storyMapping', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e5', source: 'storyMapping', target: 'contentStrategist', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e6', source: 'storyMapping', target: 'uxContentDesigner', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e7', source: 'uxContentDesigner', target: 'designStrategist', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e8', source: 'analyticalThinking', target: 'sql', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e9', source: 'sql', target: 'dataViz', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e10', source: 'dataViz', target: 'storyMapping', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e11', source: 'storyMapping', target: 'dataAnalyst', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e12', source: 'dataViz', target: 'behavioralResearcher', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e13', source: 'publicSpeaking', target: 'storyMapping', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e14', source: 'storyMapping', target: 'userPsychology', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e15', source: 'userPsychology', target: 'productEvangelist', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e16', source: 'userPsychology', target: 'workshopFacilitator', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e17', source: 'productEvangelist', target: 'policyAdvisor', markerEnd: { type: MarkerType.ArrowClosed } },
];

const CareerGrowthTree = () => {
  const [nodes, setNodes] = useState(initialNodes);
  const [currentEdges, setEdges] = useState(edges);

  return (
    <div className="h-[1000px] w-full">
      <ReactFlow
        nodes={nodes}
        edges={currentEdges}
        fitView
        proOptions={{ hideAttribution: true }}
        nodesDraggable
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default CareerGrowthTree;