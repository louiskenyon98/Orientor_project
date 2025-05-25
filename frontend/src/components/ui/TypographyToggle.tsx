'use client';
import { useState, useRef, useEffect } from 'react';
import { useTypography, FontFamily } from '@/contexts/TypographyContext';
import { useColor } from '@/contexts/ColorContext';

interface TypographyToggleProps {
  className?: string;
}

export default function TypographyToggle({ className = '' }: TypographyToggleProps) {
  const { currentTheme, setTypographyTheme, availableThemes } = useTypography();
  const { currentTheme: colorTheme } = useColor();
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
        aria-label="Changer la typographie"
        title="Changer la typographie"
        style={{
          color: colorTheme.textColor,
          fontFamily: 'var(--heading-font)'
        }}
      >
        <span className="material-icons-outlined">text_format</span>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg overflow-hidden z-50" style={{
          backgroundColor: colorTheme.primaryColor,
          borderWidth: '1px',
          borderStyle: 'solid',
          borderColor: colorTheme.borderColor
        }}>
          <div className="py-1">
            <div className="px-4 py-2 text-xs font-bold border-b" style={{
              color: colorTheme.textColor,
              borderColor: colorTheme.borderColor,
              fontFamily: 'var(--heading-font)'
            }}>
              Typographie
            </div>
            {availableThemes.map((theme) => (
              <button
                key={theme.id}
                onClick={() => {
                  setTypographyTheme(theme.id as FontFamily);
                  setIsOpen(false);
                }}
                className="flex items-center w-full px-4 py-2 text-sm"
                style={{
                  backgroundColor: currentTheme.id === theme.id ? `${colorTheme.primaryColor}80` : 'transparent',
                  color: currentTheme.id === theme.id ? colorTheme.accentColor : colorTheme.textColor,
                  fontFamily: theme.headingFont
                }}
              >
                <span className="material-icons-outlined mr-2" style={{ color: colorTheme.textColor }}>
                  {currentTheme.id === theme.id ? 'check_circle' : 'circle'}
                </span>
                <span style={{ fontFamily: theme.headingFont }}>{theme.name}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}