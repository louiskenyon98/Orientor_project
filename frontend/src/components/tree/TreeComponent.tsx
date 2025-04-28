import 'reactflow/dist/style.css';
import './treestyles.css'; // Add custom styles
import { convertToFlowGraph } from '../../utils/convertToFlowGraph';
import { useRef } from 'react';

const TreeComponent = () => {
    const wrapperRef = useRef<HTMLDivElement>(null);
    const [nodes, setNodes] = useState<Node[]>([]);
    const [edges, setEdges] = useState<Edge[]>([]);
    const [nodeTypes, setNodeTypes] = useState<NodeTypes>({});

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }} ref={wrapperRef}>
      <ReactFlow
        className="tree-flow-container"
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        fitViewOptions={{ padding: 1.5 }}
        nodesDraggable={false}
        panOnDrag
        zoomOnScroll
        zoomOnPinch
        attributionPosition="bottom-right"
      >
        <Background color="#f1f5f9" gap={24} size={1} />
        <Controls position="bottom-right" showInteractive={false} />
        <Panel position="top-right">
          <div className="bg-blue-50 border border-blue-200 rounded-md shadow-sm p-3 text-sm text-blue-800">
            <p><strong>Tip:</strong> Click on any skill node to see recommended action steps.</p>
          </div>
        </Panel>
        <MiniMap
          nodeColor={(node) => {
            switch (node.type) {
              case 'root':
                return '#2563eb';
              case 'skill':
                return '#0ea5e9';
              case 'outcome':
                return '#e2e8f0';
              case 'career':
                return '#f59e0b';
              default:
                return '#cbd5e1';
            }
          }}
          style={{
            backgroundColor: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
          }}
        />
      </ReactFlow>
    </div>
  ); 