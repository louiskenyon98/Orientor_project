'use client';
import { createContext, useContext, useEffect, useState } from 'react';

type ThemeContextType = {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
};

const ThemeContext = createContext<ThemeContextType>({
  isDarkMode: false,
  toggleDarkMode: () => {},
});

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
      //   // Check if user has a theme preference in localStorage
      //   const storedTheme = localStorage.getItem('theme');
    
      //   // Check if user has a system preference
      //   const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
      //   // Set initial theme based on stored preference or system preference
      //   setIsDarkMode(storedTheme === 'dark' || (!storedTheme && systemPreference));
        
      //   // Apply the theme to the document
      //   if (isDarkMode) {
      //     document.documentElement.classList.add('dark');
      //   } else {
      //     document.documentElement.classList.remove('dark');
      //   }
      // }, [isDarkMode]);
    // Force light mode
    setIsDarkMode(false);
    document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  }, []);

  const toggleDarkMode = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('theme', newMode ? 'dark' : 'light');
    
    if (newMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext); 