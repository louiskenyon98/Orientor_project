// src/components/SkillTreeVisualizer.tsx
import { SkillNode } from "@/components/branches/career_growth";

export default function SkillTreeVisualizer({ root }: { root: SkillNode }) {
  return (
    <div className="max-w-4xl mx-auto p-4">
      <ul className="space-y-4">
        <TreeNode node={root} depth={0} />
      </ul>
    </div>
  );
}

function TreeNode({ node, depth }: { node: SkillNode; depth: number }) {
  const hasChildren = node.nextSkills && node.nextSkills.length > 0;

  return (
    <li>
      <div
        className={`p-4 bg-white border rounded-md shadow-sm transition-all ${
          depth > 0 ? 'ml-6 border-l-4 border-blue-300' : ''
        }`}
      >
        <div className="font-semibold text-gray-800">{node.skillDescription}</div>
        {node.improvementSuggestion && (
          <div className="text-sm text-gray-500 italic">{node.improvementSuggestion}</div>
        )}

        {node.reachableJobs && node.reachableJobs.length > 0 && (
          <div className="mt-2 text-sm text-blue-700">
            <strong>→ Possible Career:</strong>{' '}
            {node.reachableJobs.map((job, i) => (
              <span key={i}>
                {job.jobTitle} in {job.jobDomain}
                {i < node.reachableJobs.length - 1 && ', '}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Recursively render children */}
      {hasChildren && (
        <ul className="mt-2 space-y-2 pl-4 border-l-2 border-gray-200">
          {node.nextSkills!.map((child) => (
            <TreeNode key={child.id} node={child} depth={depth + 1} />
          ))}
        </ul>
      )}
    </li>
  );
}
