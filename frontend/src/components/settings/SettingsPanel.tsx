'use client';
import { useState } from 'react';
import { useTypography } from '@/contexts/TypographyContext';
import { useColor } from '@/contexts/ColorContext';
import TypographyToggle from '../ui/TypographyToggle';
import ColorToggle from '../ui/ColorToggle';

interface SettingsPanelProps {
  className?: string;
}

export default function SettingsPanel({ className = '' }: SettingsPanelProps) {
  const [activeTab, setActiveTab] = useState<'typography' | 'colors'>('typography');
  const { currentTheme: currentTypographyTheme } = useTypography();
  const { currentTheme: currentColorTheme } = useColor();

  return (
    <div className={`rounded-lg shadow-lg overflow-hidden ${className}`} style={{
      backgroundColor: currentColorTheme.primaryColor,
      borderWidth: '1px',
      borderStyle: 'solid',
      borderColor: currentColorTheme.borderColor,
      color: currentColorTheme.textColor,
      fontFamily: 'var(--body-font)'
    }}>
      {/* Tabs */}
      <div className="flex" style={{ borderBottom: `1px solid ${currentColorTheme.borderColor}` }}>
        <button
          onClick={() => setActiveTab('typography')}
          className="flex-1 py-3 text-sm font-bold transition-colors duration-150 ease-in-out"
          style={{
            color: activeTab === 'typography' ? currentColorTheme.accentColor : currentColorTheme.textColor,
            borderBottom: activeTab === 'typography' ? `2px solid ${currentColorTheme.accentColor}` : 'none',
            fontFamily: 'var(--heading-font)'
          }}
        >
          <span className="material-icons-outlined mr-2 align-middle">text_format</span>
          Typographie
        </button>
        <button
          onClick={() => setActiveTab('colors')}
          className="flex-1 py-3 text-sm font-bold transition-colors duration-150 ease-in-out"
          style={{
            color: activeTab === 'colors' ? currentColorTheme.accentColor : currentColorTheme.textColor,
            borderBottom: activeTab === 'colors' ? `2px solid ${currentColorTheme.accentColor}` : 'none',
            fontFamily: 'var(--heading-font)'
          }}
        >
          <span className="material-icons-outlined mr-2 align-middle">palette</span>
          Couleurs
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        {activeTab === 'typography' && (
          <div>
            <h3 className="text-lg font-bold mb-4" style={{
              color: currentColorTheme.textColor,
              fontFamily: 'var(--heading-font)'
            }}>Paramètres de typographie</h3>
            <div className="mb-4">
              <p className="text-sm mb-2" style={{
                color: currentColorTheme.textColor,
                fontFamily: 'var(--body-font)'
              }}>
                Thème actuel: <span className="font-bold">{currentTypographyTheme.name}</span>
              </p>
              <div className="flex flex-wrap gap-2 mt-4">
                <TypographyToggle className="w-full" />
              </div>
            </div>
            <div className="mt-6">
              <h4 className="text-md font-bold mb-2" style={{
                color: currentColorTheme.textColor,
                fontFamily: 'var(--heading-font)'
              }}>Aperçu</h4>
              <div className="p-4 rounded-lg" style={{
                backgroundColor: `${currentColorTheme.primaryColor}30`,
                border: `1px solid ${currentColorTheme.borderColor}`,
                color: currentColorTheme.textColor
              }}>
                <h1 className="text-2xl font-bold mb-2" style={{ fontFamily: currentTypographyTheme.headingFont }}>Titre de niveau 1</h1>
                <h2 className="text-xl font-bold mb-2" style={{ fontFamily: currentTypographyTheme.headingFont }}>Titre de niveau 2</h2>
                <p className="mb-2" style={{ fontFamily: currentTypographyTheme.bodyFont }}>Texte normal avec la police {currentTypographyTheme.name}.</p>
                <code className="font-mono text-sm p-1 rounded" style={{
                  fontFamily: currentTypographyTheme.monoFont,
                  backgroundColor: `${currentColorTheme.primaryColor}50`
                }}>Code avec police mono</code>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'colors' && (
          <div>
            <h3 className="text-lg font-bold mb-4" style={{
              color: currentColorTheme.textColor,
              fontFamily: 'var(--heading-font)'
            }}>Paramètres de couleurs</h3>
            <div className="mb-4">
              <p className="text-sm mb-2" style={{
                color: currentColorTheme.textColor,
                fontFamily: 'var(--body-font)'
              }}>
                Thème actuel: <span className="font-bold">{currentColorTheme.name}</span>
              </p>
              <div className="flex flex-wrap gap-2 mt-4">
                <ColorToggle className="w-full" />
              </div>
            </div>
            <div className="mt-6">
              <h4 className="text-md font-bold mb-2" style={{
                color: currentColorTheme.textColor,
                fontFamily: 'var(--heading-font)'
              }}>Aperçu</h4>
              <div className="p-4 rounded-lg" style={{
                backgroundColor: `${currentColorTheme.primaryColor}30`,
                border: `1px solid ${currentColorTheme.borderColor}`,
                color: currentColorTheme.textColor
              }}>
                <div className="flex flex-col gap-3">
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full mr-2" style={{ backgroundColor: currentColorTheme.primaryColor }}></div>
                    <span className="text-sm" style={{ color: currentColorTheme.textColor }}>Couleur primaire</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full mr-2" style={{ backgroundColor: currentColorTheme.accentColor }}></div>
                    <span className="text-sm" style={{ color: currentColorTheme.textColor }}>Couleur d'accent</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full mr-2" style={{ backgroundColor: currentColorTheme.borderColor }}></div>
                    <span className="text-sm" style={{ color: currentColorTheme.textColor }}>Couleur de bordure</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full mr-2" style={{ backgroundColor: currentColorTheme.textColor }}></div>
                    <span className="text-sm" style={{ color: currentColorTheme.textColor }}>Couleur de texte</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full mr-2" style={{ backgroundColor: currentColorTheme.textColorLight }}></div>
                    <span className="text-sm" style={{ color: currentColorTheme.textColor }}>Couleur de texte claire</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full mr-2" style={{ backgroundColor: currentColorTheme.linkColor }}></div>
                    <span className="text-sm" style={{ color: currentColorTheme.textColor }}>Couleur de lien</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 rounded-full mr-2" style={{ backgroundColor: currentColorTheme.linkHoverColor }}></div>
                    <span className="text-sm" style={{ color: currentColorTheme.textColor }}>Couleur de survol de lien</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}