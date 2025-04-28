import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

// Navigation links configuration
const links = [
  { href: '/', label: 'Home' },
  // Remove standalone Skill Tree link as it will be in the dropdown
];

// Navigation with dropdown for Career Growth section
export default function Navigation() {
  const pathname = usePathname() || '';
  const [careerDropdownOpen, setCareerDropdownOpen] = useState(false);

  const toggleCareerDropdown = () => {
    setCareerDropdownOpen(!careerDropdownOpen);
  };

  return (
    <nav className="bg-white shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="font-bold text-xl text-blue-600">
              Navigo
            </Link>
          </div>
          
          {/* Main Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/" className="text-gray-600 hover:text-gray-900">
              Mentor
            </Link>
            
            <Link href="/" className="text-gray-600 hover:text-gray-900">
              Network
            </Link>
            
            {/* Career Growth Dropdown */}
            <div className="relative">
              <button 
                onClick={toggleCareerDropdown}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                  pathname.includes('/tree') || pathname.includes('/career')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                Career Growth
                <svg 
                  className={`ml-2 w-4 h-4 transition-transform ${careerDropdownOpen ? 'transform rotate-180' : ''}`} 
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
              
              {/* Dropdown Menu */}
              {careerDropdownOpen && (
                <div className="absolute mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
                  <div className="py-1" role="menu" aria-orientation="vertical">
                    <Link 
                      href="/career-insights" 
                      className={`block px-4 py-2 text-sm ${pathname === '/career-insights' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
                    >
                      Career Insights
                    </Link>
                    <Link 
                      href="/pathway-explorer" 
                      className={`block px-4 py-2 text-sm ${pathname === '/pathway-explorer' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
                    >
                      Pathway Explorer
                    </Link>
                    <Link 
                      href="/tree" 
                      className={`block px-4 py-2 text-sm ${pathname === '/tree' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
                    >
                      Skill Tree Explorer
                    </Link>
                    <Link 
                      href="/resume-studio" 
                      className={`block px-4 py-2 text-sm ${pathname === '/resume-studio' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
                    >
                      Resume Studio
                    </Link>
                  </div>
                </div>
              )}
            </div>
            
            <Link href="/" className="text-gray-600 hover:text-gray-900">
              Workspace
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
} 