'use client';
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/react';
import { Providers } from './providers';
import MainLayout from '@/components/layout/MainLayout';
import './globals.css';

// export const metadata = {
//   title: 'Navigo - Your Personal Guide',
//   description: 'Your personal guidance for growth and self-discovery',
// };

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet" />
      </head>
      <Providers>
        <body className="min-h-screen antialiased">
          {/* Main layout with navigation */}
          <MainLayout>
            {children}
          </MainLayout>

          <Analytics />
          <SpeedInsights />
        </body>
      </Providers>
    </html>
  );
}