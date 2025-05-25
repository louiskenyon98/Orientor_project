'use client';
import { useState, useRef, useEffect } from 'react';
import { useColor, ColorPalette } from '@/contexts/ColorContext';

interface ColorToggleProps {
  className?: string;
}

export default function ColorToggle({ className = '' }: ColorToggleProps) {
  const { currentTheme, setColorTheme, availableThemes } = useColor();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fermer le menu lorsqu'on clique en dehors
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-sm font-bold rounded-md transition-colors duration-150 ease-in-out"
        aria-label="Changer les couleurs"
        title="Changer les couleurs"
        style={{
          color: currentTheme.textColor,
          fontFamily: 'var(--heading-font)'
        }}
      >
        <span className="material-icons-outlined">palette</span>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg overflow-hidden z-50" style={{
          backgroundColor: currentTheme.primaryColor,
          borderWidth: '1px',
          borderStyle: 'solid',
          borderColor: currentTheme.borderColor
        }}>
          <div className="py-1">
            <div className="px-4 py-2 text-xs font-bold border-b" style={{
              color: currentTheme.textColor,
              borderColor: currentTheme.borderColor,
              fontFamily: 'var(--heading-font)'
            }}>
              Thème de couleurs
            </div>
            {availableThemes.map((theme) => (
              <button
                key={theme.id}
                onClick={() => {
                  setColorTheme(theme.id as ColorPalette);
                  setIsOpen(false);
                }}
                className="flex items-center w-full px-4 py-2 text-sm"
                style={{
                  backgroundColor: currentTheme.id === theme.id ? `${currentTheme.primaryColor}80` : 'transparent',
                  color: currentTheme.id === theme.id ? currentTheme.accentColor : currentTheme.textColor,
                  fontFamily: 'var(--body-font)'
                }}
              >
                <span className="material-icons-outlined mr-2" style={{ color: currentTheme.textColor }}>
                  {currentTheme.id === theme.id ? 'check_circle' : 'circle'}
                </span>
                <span>{theme.name}</span>
                <div
                  className="ml-auto w-4 h-4 rounded-full"
                  style={{
                    backgroundColor: theme.primaryColor
                  }}
                ></div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}