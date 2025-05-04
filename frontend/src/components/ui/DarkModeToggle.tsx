'use client';
import { useTheme } from '@/contexts/ThemeContext';

type DarkModeToggleProps = {
  className?: string;
};

export default function DarkModeToggle({ className = '' }: DarkModeToggleProps) {
  const { isDarkMode, toggleDarkMode } = useTheme();

  return (
    <button
      onClick={toggleDarkMode}
      className={`p-2 rounded-md transition-colors ${
        isDarkMode
          ? 'text-gray-200 hover:text-white hover:bg-gray-700'
          : 'text-gray-600 hover:text-gray-800 hover:bg-gray-200'
      } ${className}`}
      aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDarkMode ? (
        <span className="material-icons-outlined">light_mode</span>
      ) : (
        <span className="material-icons-outlined">dark_mode</span>
      )}
    </button>
  );
} 