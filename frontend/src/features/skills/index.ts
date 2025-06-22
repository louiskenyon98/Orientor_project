// Skills feature exports with lazy loading support
import dynamic from 'next/dynamic';

// Regular exports for types and utilities
export * from './types/competence.types';
export * from './utils/treeLayout';

// Component exports
export { TreeNode } from './components/TreeNode';

// Lazy loaded components for code splitting
export const CompetenceTreeView = dynamic(
  () => import('./components/CompetenceTreeView').then(mod => mod.CompetenceTreeView),
  {
    loading: () => <div>Loading Competence Tree...</div>,
    ssr: false
  }
);

// Export individual lazy components if needed elsewhere
export const LazyCompetenceTreeView = dynamic(
  () => import('./components/CompetenceTreeView'),
  { ssr: false }
);