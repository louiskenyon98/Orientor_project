'use client';

import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  Position,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { SkillNode } from '@/components/career_growth';
import { motion } from 'framer-motion';

function getNodeStyle(type: string) {
  switch (type) {
    case 'root':
      return 'bg-gradient-to-r from-amber-600 to-yellow-400 text-white shadow-lg';
    case 'outcome':
      return 'bg-white text-gray-800 border border-gray-300 shadow-md';
    default:
      return 'bg-gradient-to-r from-gray-700 to-gray-900 text-white shadow-md group relative';
  }
}

function convertToFlowGraph(root: SkillNode): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  let yGap = 250;
  let xGap = 300;
  let queue: { node: SkillNode; depth: number; column: number; parentId?: string; type?: string }[] = [
    { node: root, depth: 0, column: 2, type: 'root' },
  ];

  while (queue.length > 0) {
    const { node, depth, column, parentId, type = 'skill' } = queue.shift()!;
    const id = node.id;
    const position = { x: column * xGap, y: depth * yGap };

    nodes.push({
      id,
      type: 'default',
      position,
      data: {
        label: (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className={`text-sm font-medium text-center rounded-xl px-4 py-3 ${getNodeStyle(type)}`}
          >
            {node.skillDescription}
            {node.improvementSuggestion && (
              <div className="text-xs italic mt-2 text-white/80">
                {node.improvementSuggestion}
              </div>
            )}
            {node.taskSuggestion && (
              <div className="absolute hidden group-hover:block text-[11px] bg-black/90 text-white px-2 py-1 rounded bottom-full left-1/2 -translate-x-1/2 mb-2 whitespace-nowrap z-50">
                💡 {node.taskSuggestion}
              </div>
            )}
          </motion.div>
        ),
      },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
    });

    if (parentId) {
      edges.push({
        id: `${parentId}-${id}`,
        source: parentId,
        target: id,
        animated: true,
        type: 'smoothstep',
        style: { stroke: '#6b7280' },
        markerEnd: {
          type: 'arrowclosed',
        },
      });
    }

    node.nextSkills?.forEach((child, index) => {
      queue.push({
        node: child,
        depth: depth + 1,
        column: column + index - Math.floor((node.nextSkills?.length ?? 1) / 2),
        parentId: id,
      });
    });

    if (node.reachableJobs && node.reachableJobs.length > 0) {
      node.reachableJobs.forEach((job, jobIndex) => {
        const jobId = `${id}-outcome-${jobIndex}`;
        const skillAId = `${jobId}-skillA`;
        const skillBId = `${jobId}-skillB`;
        const nextJobId = `${jobId}-next-job`;

        const baseY = position.y + 150 + jobIndex * 500;

        nodes.push({
          id: jobId,
          type: 'default',
          position: { x: position.x, y: baseY },
          data: {
            label: (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className={`rounded-xl px-4 py-3 text-sm text-center ${getNodeStyle('outcome')}`}
              >
                <strong className="text-md font-semibold">{job.jobTitle}</strong>
                <div className="text-xs text-gray-600">in {job.jobDomain}</div>
              </motion.div>
            ),
          },
          sourcePosition: Position.Top,
          targetPosition: Position.Bottom,
        });

        edges.push({
          id: `${id}-${jobId}`,
          source: id,
          target: jobId,
          type: 'smoothstep',
          markerEnd: { type: 'arrowclosed' },
        });

        nodes.push({
          id: skillAId,
          type: 'default',
          position: { x: position.x - 100, y: baseY + 150 },
          data: {
            label: (
              <div className="text-xs font-medium text-center rounded-xl px-4 py-2 bg-slate-200 text-gray-800 border border-gray-300 shadow-sm">
                Maintain Composure Under Pressure
                <div className="text-[10px] mt-1 text-gray-600 italic">💡 Simulate time-bound decisions</div>
              </div>
            ),
          },
          sourcePosition: Position.Bottom,
          targetPosition: Position.Top,
        });

        nodes.push({
          id: skillBId,
          type: 'default',
          position: { x: position.x + 100, y: baseY + 150 },
          data: {
            label: (
              <div className="text-xs font-medium text-center rounded-xl px-4 py-2 bg-slate-200 text-gray-800 border border-gray-300 shadow-sm">
                Navigate Ethical Dilemmas
                <div className="text-[10px] mt-1 text-gray-600 italic">💡 Write a personal response plan</div>
              </div>
            ),
          },
          sourcePosition: Position.Bottom,
          targetPosition: Position.Top,
        });

        edges.push({ id: `${jobId}-${skillAId}`, source: jobId, target: skillAId, type: 'smoothstep', markerEnd: { type: 'arrowclosed' } });
        edges.push({ id: `${jobId}-${skillBId}`, source: jobId, target: skillBId, type: 'smoothstep', markerEnd: { type: 'arrowclosed' } });

        nodes.push({
          id: nextJobId,
          type: 'default',
          position: { x: position.x, y: baseY + 350 },
          data: {
            label: (
              <div className="text-xs font-semibold text-center rounded-xl px-4 py-3 bg-white border shadow">
                🧭 Risk Strategy Lead<br />in Emergency Governance
              </div>
            ),
          },
          targetPosition: Position.Bottom,
        });

        edges.push({ id: `${skillAId}-${nextJobId}`, source: skillAId, target: nextJobId, type: 'smoothstep', markerEnd: { type: 'arrowclosed' } });
        edges.push({ id: `${skillBId}-${nextJobId}`, source: skillBId, target: nextJobId, type: 'smoothstep', markerEnd: { type: 'arrowclosed' } });
      });
    }
  }
  return { nodes, edges };
}

// Root node config remains the same
const root: SkillNode = {
  id: 'root',
  skillDescription: 'Root, initial condition of the user',
  nextSkills: [
    {
      id: 's2',
      skillDescription: 'You thrive in fast-paced settings',
      improvementSuggestion: 'Improve your stress tolerance',
      taskSuggestion: 'Take a First Aid or CPR course',
      nextSkills: [
        {
          id: 's2-1',
          skillDescription: 'You act fast in emergencies',
          taskSuggestion: 'Join a local emergency preparedness drill',
          reachableJobs: [
            { jobTitle: 'Paramedic', jobDomain: 'Emergency Services', requiredSkills: [] },
            { jobTitle: 'Disaster Response Officer', jobDomain: 'Crisis Management', requiredSkills: [] },
          ],
        },
      ],
    },
  ],
};

export default function SkillTreeFlow() {
  const { nodes, edges } = convertToFlowGraph(root);

  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <ReactFlowProvider>
        <ReactFlow nodes={nodes} edges={edges} fitView panOnScroll zoomOnScroll>
          <MiniMap nodeStrokeWidth={3} zoomable pannable />
          <Background color="#f3f4f6" gap={24} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}