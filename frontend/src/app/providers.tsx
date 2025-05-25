'use client';

import { ThemeProvider } from '@/contexts/ThemeContext';
import { TypographyProvider } from '@/contexts/TypographyContext';
import { ColorProvider } from '@/contexts/ColorContext';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <TypographyProvider>
        <ColorProvider>
          {children}
        </ColorProvider>
      </TypographyProvider>
    </ThemeProvider>
  );
}