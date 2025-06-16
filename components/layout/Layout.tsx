import React from 'react';
import { Navigation } from './Navigation';

interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function Layout({ children, className = '' }: LayoutProps) {
  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      <Navigation />
      <main>{children}</main>
    </div>
  );
}