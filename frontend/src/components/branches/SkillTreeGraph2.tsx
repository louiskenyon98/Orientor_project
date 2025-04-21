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
import { SkillNode } from '@/components/branches/career_growth';
import { motion } from 'framer-motion';

function getNodeStyle(type: string) {
  switch (type) {
    case 'root':
      return 'bg-orange-400 text-white';
    case 'outcome':
      return 'bg-gray-100 text-gray-800 border border-gray-300';
    default:
      return 'bg-blue-500 text-white';
  }
}

function convertToFlowGraph(root: SkillNode): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  let yGap = 200;
  let xGap = 250;
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
            className={`text-sm font-medium text-center rounded p-3 shadow ${getNodeStyle(type)}`}
          >
            {node.skillDescription}
            {node.improvementSuggestion && (
              <div className="text-xs italic mt-2 text-white/80">
                {node.improvementSuggestion}
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
        style: { stroke: '#999' },
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
      const jobId = `${id}-outcome`;
      nodes.push({
        id: jobId,
        type: 'default',
        position: { x: position.x, y: position.y - 100 },
        data: {
          label: (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className={`rounded p-2 text-sm text-center ${getNodeStyle('outcome')}`}
            >
              <strong>Outcome:</strong>
              <br />
              {node.reachableJobs.map((j) => `${j.jobTitle} in ${j.jobDomain}`).join(', ')}
            </motion.div>
          ),
        },
        targetPosition: Position.Bottom,
      });

      edges.push({
        id: `${id}-${jobId}`,
        source: id,
        target: jobId,
        type: 'smoothstep',
        style: { stroke: '#ccc', strokeDasharray: '4 2' },
      });
    }
  }

  return { nodes, edges };
}

const root: SkillNode = {
  id: 'root',
  skillDescription: 'Root, initial condition of the user',
  nextSkills: [
    {
      id: 's1',
      skillDescription: 'You listen and help',
      improvementSuggestion: 'Show some support to others',
      nextSkills: [
        {
          id: 's1-1',
          skillDescription: 'You step up when others need it',
          improvementSuggestion: 'Show some leadership',
          reachableJobs: [
            { jobTitle: 'Youth Counselor', jobDomain: 'Community Services', requiredSkills: [] },
            { jobTitle: 'Volunteer Program Coordinator', jobDomain: 'Non-profit Organizations', requiredSkills: [] },
          ],
        },
        {
          id: 's1-2',
          skillDescription: 'You care deeply about social equity',
          reachableJobs: [
            { jobTitle: 'Social Worker', jobDomain: 'Public Health', requiredSkills: [] },
            { jobTitle: 'Community Outreach Officer', jobDomain: 'Municipal Services', requiredSkills: [] },
          ],
        },
      ],
    },
    {
      id: 's2',
      skillDescription: 'You thrive in fast-paced settings',
      improvementSuggestion: 'Improve your stress tolerance',
      nextSkills: [
        {
          id: 's2-1',
          skillDescription: 'You act fast in emergencies',
          reachableJobs: [
            { jobTitle: 'Paramedic', jobDomain: 'Emergency Services', requiredSkills: [] },
            { jobTitle: 'Disaster Response Officer', jobDomain: 'Crisis Management', requiredSkills: [] },
          ],
        },
      ],
    },
    {
      id: 's3',
      skillDescription: 'You express ideas clearly',
      improvementSuggestion: 'Improve communication skills',
      nextSkills: [
        {
          id: 's3-1',
          skillDescription: 'You understand your audience deeply',
          reachableJobs: [
            { jobTitle: 'UX Designer', jobDomain: 'Tech & Accessibility', requiredSkills: [] },
            { jobTitle: 'Workshop Facilitator', jobDomain: 'Adult Learning & Training', requiredSkills: [] },
          ],
        },
      ],
    },
    {
      id: 's4',
      skillDescription: 'You write with clarity and voice',
      improvementSuggestion: 'Improve your writing skills',
      nextSkills: [
        {
          id: 's4-1',
          skillDescription: 'You shape ideas into structured arguments',
          reachableJobs: [
            { jobTitle: 'Content Creator', jobDomain: 'Digital Media', requiredSkills: [] },
            { jobTitle: 'Technical Writer', jobDomain: 'Software Documentation', requiredSkills: [] },
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
          <Background color="#f0f0f0" gap={16} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}