'use client';
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/react';
import { Providers } from './providers';
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
        <body className="min-h-screen bg-light-background dark:bg-dark-background text-neutral-700 dark:text-gray-200 antialiased">
          {/* Background patterns */}
          <div 
            className="fixed inset-0 -z-10 bg-[url('/patterns/branch.svg')] bg-repeat opacity-90 dark:opacity-300"
            style={{ backgroundSize: '200px 200px' }}
          ></div>
          <div 
            className="fixed inset-0 -z-10 bg-[url('/patterns/grid.svg')] bg-repeat opacity-90 dark:opacity-300"
            style={{ backgroundSize: '200px 200px' }}
          ></div>
          
          {/* Main content */}
          <main>
            {children}
          </main>

          <Analytics />
          <SpeedInsights />
        </body>
      </Providers>
    </html>
  );
}