import { Recommendation } from '@/services/spaceService';

interface SidebarProps {
  items: Recommendation[];
  selectedId?: number;
  onSelect: (item: Recommendation) => void;
  onDelete: (id: number) => void;
  loading: boolean;
  error: string | null;
}

export default function Sidebar({ items, selectedId, onSelect, onDelete, loading, error }: SidebarProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">{error}</div>;
  }

  if (items.length === 0) {
    return <div className="text-center text-gray-600 p-4">No saved recommendations yet.</div>;
  }

  return (
    <div className="p-4 space-y-3">
      {items.map((item) => (
        <div
          key={item.id}
          className={`p-4 rounded-lg cursor-pointer ${
            selectedId === item.id
              ? 'bg-blue-50 border border-blue-200'
              : 'bg-white border border-gray-200 hover:border-blue-300'
          }`}
        >
          <div onClick={() => onSelect(item)}>
            <h3 className="font-medium text-gray-900 text-sm">{item.label}</h3>
            <p className="text-xs text-gray-500">{item.oasis_code}</p>
          </div>
          <button
            onClick={() => item.id && onDelete(item.id)}
            className="mt-2 text-gray-500 hover:text-red-500 text-xs font-medium"
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
} 