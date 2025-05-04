'use client';
import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import XPProgress from '../ui/XPProgress';

export default function MainLayout({ 
    children, 
    showNav = true 
}: { 
    children: React.ReactNode, 
    showNav?: boolean 
}) {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [moreMenuOpen, setMoreMenuOpen] = useState(false);
    const [careerMenuOpen, setCareerMenuOpen] = useState(false);
    const [workspaceMenuOpen, setWorkspaceMenuOpen] = useState(false);
    const moreMenuRef = useRef<HTMLDivElement>(null);
    const careerMenuRef = useRef<HTMLDivElement>(null);
    const workspaceMenuRef = useRef<HTMLDivElement>(null);
    const router = useRouter();
    const pathname = usePathname();

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/register', '/test-page'];
    const isPublicRoute = pathname ? publicRoutes.includes(pathname) : false;

    useEffect(() => {
        // Check if user is logged in
        const token = localStorage.getItem('access_token') || '';
        console.log('Auth check - Token:', token ? 'Found' : 'Not found', 'Pathname:', pathname);
        
        if (!token && !isPublicRoute && showNav) {
            console.log('No token found, redirecting to login');
            router.push('/login');
            return;
        }
        
        const loggedIn = !!token;
        console.log('Setting isLoggedIn to:', loggedIn);
        setIsLoggedIn(loggedIn);
        setIsLoading(false);
    }, [router, isPublicRoute, showNav, pathname]);

    // Close menus when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (moreMenuRef.current && !moreMenuRef.current.contains(event.target as Node)) {
                setMoreMenuOpen(false);
            }
            if (careerMenuRef.current && !careerMenuRef.current.contains(event.target as Node)) {
                setCareerMenuOpen(false);
            }
            if (workspaceMenuRef.current && !workspaceMenuRef.current.contains(event.target as Node)) {
                setWorkspaceMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    // Close mobile menus when route changes
    useEffect(() => {
        console.log('Route changed to:', pathname);
        setMoreMenuOpen(false);
        setCareerMenuOpen(false);
        setWorkspaceMenuOpen(false);
    }, [pathname]);

    const handleLogout = () => {
        console.log('Logging out user');
        localStorage.removeItem('access_token');
        router.push('/login');
    };

    const toggleCareerDropdown = () => {
        console.log('Toggling career dropdown');
        setCareerMenuOpen(!careerMenuOpen);
        if (workspaceMenuOpen) setWorkspaceMenuOpen(false);
    };

    const toggleWorkspaceDropdown = () => {
        console.log('Toggling workspace dropdown, current state:', workspaceMenuOpen);
        setWorkspaceMenuOpen(!workspaceMenuOpen);
        if (careerMenuOpen) setCareerMenuOpen(false);
    };

    // For public routes, render immediately without checking auth
    if (isPublicRoute) {
        return (
            <div className="min-h-screen flex flex-col">
                <main className="flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    {children}
                </main>
            </div>
        );
    }

    // Show loading state while checking authentication
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    // Check if current path is in career path section
    const isCareerPath = ['/vector-search', '/find-your-way', '/cv', '/tree'].includes(pathname || '');

    console.log('Rendering layout with isLoggedIn:', isLoggedIn);

    return (
        <div className="min-h-screen flex flex-col">
            {/* Desktop Navigation Bar - Only visible on larger screens */}
            {isLoggedIn && (
                <header className="fixed top-0 left-0 right-0 w-full z-50 bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm hidden md:block">
                    <div className="max-w-7xl mx-auto px-8">
                        <div className="flex justify-between h-16">
                            {/* Left Side - Logo and Primary Navigation */}
                            <div className="flex items-center space-x-8">
                                {/* Logo */}
                                <Link href="/" className="flex-shrink-0 flex items-center">
                                    <span className="text-xl font-semibold tracking-tight text-gray-900">
                                        Navigo
                                    </span>
                                </Link>
                                
                                {/* Primary Navigation */}
                                <div className="flex items-center space-x-1">
                                    <Link 
                                        href="/chat" 
                                        className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out
                                            ${pathname === '/chat' 
                                                ? 'text-blue-700 bg-blue-50' 
                                                : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                            }`}
                                    >
                                        Mentor
                                    </Link>
                                    
                                    <Link 
                                        href="/peers" 
                                        className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out
                                            ${pathname === '/peers' 
                                                ? 'text-blue-700 bg-blue-50' 
                                                : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                            }`}
                                    >
                                        Network
                                    </Link>


                                    {/* Career Path Dropdown */}
                                    <div className="relative" ref={careerMenuRef}>
                                        <button 
                                            onClick={toggleCareerDropdown}
                                            className={`group px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out flex items-center
                                                ${isCareerPath
                                                    ? 'text-blue-700 bg-blue-50' 
                                                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                                }`}
                                        >
                                            Career Growth
                                            <svg className={`ml-1 h-4 w-4 transition-transform duration-200 ${careerMenuOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                            </svg>
                                        </button>
                                        
                                        {careerMenuOpen && (
                                            <div className="absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-40">
                                                <div className="py-1" role="menu" aria-orientation="vertical">
                                                    <Link
                                                        href="/vector-search"
                                                        className={`block px-4 py-2 text-sm ${pathname === '/vector-search' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'}`}
                                                        role="menuitem"
                                                    >
                                                        Career Insights
                                                    </Link>
                                                    <Link
                                                        href="/find-your-way"
                                                        className={`block px-4 py-2 text-sm ${pathname === '/find-your-way' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'}`}
                                                        role="menuitem"
                                                    >
                                                        Pathway Explorer
                                                    </Link>
                                                    <Link
                                                        href="/career"
                                                        className={`block px-4 py-2 text-sm ${pathname === '/career' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'}`}
                                                        role="menuitem"
                                                    >
                                                        Career Explorer
                                                    </Link>
                                                    <Link
                                                        href="/enhanced-skills"
                                                        className={`block px-4 py-2 text-sm ${pathname === '/enhanced-skills' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'}`}
                                                        role="menuitem"
                                                    >
                                                        Enhanced Skills Path
                                                    </Link>
                                                    <Link
                                                        href="/cv"
                                                        className={`block px-4 py-2 text-sm ${pathname === '/cv' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'}`}
                                                        role="menuitem"
                                                    >
                                                        Resume Studio
                                                    </Link>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                    {/* <Link 
                                        href="/space" 
                                        className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out
                                            ${pathname === '/space' 
                                                ? 'text-blue-700 bg-blue-50' 
                                                : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                            }`}
                                    >
                                        Workspace
                                    </Link>

                                    <Link 
                                        href="/tree-path" 
                                        className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out
                                            ${pathname === '/tree-path' 
                                                ? 'text-blue-700 bg-blue-50' 
                                                : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                            }`}
                                    >
                                        Tree Path
                                    </Link> */}

                                    {/* Workspace Dropdown */}
                                    <div className="relative inline-block text-left" ref={workspaceMenuRef}>
                                        <button
                                            type="button"
                                            onClick={() => setWorkspaceMenuOpen(!workspaceMenuOpen)}
                                            className="inline-flex justify-center w-full px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 rounded-md transition-colors duration-150 ease-in-out"
                                        >
                                            Workspace
                                            <svg
                                            className={`ml-2 h-4 w-4 transition-transform duration-200 ${workspaceMenuOpen ? 'rotate-180' : ''}`}
                                            xmlns="http://www.w3.org/2000/svg"
                                            viewBox="0 0 20 20"
                                            fill="currentColor"
                                            aria-hidden="true"
                                            >
                                            <path
                                                fillRule="evenodd"
                                                d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.25 4.25a.75.75 0 01-1.06 0L5.21 8.27a.75.75 0 01.02-1.06z"
                                                clipRule="evenodd"
                                            />
                                            </svg>
                                        </button>

                                        <div className={`absolute z-10 mt-2 w-44 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none ${workspaceMenuOpen ? 'block' : 'hidden'}`}>
                                            <div className="py-1">
                                            <Link
                                                href="/space"
                                                className={`block px-4 py-2 text-sm rounded-md transition-colors duration-150 ease-in-out
                                                ${pathname === '/space'
                                                    ? 'text-blue-700 bg-blue-50'
                                                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                                }`}
                                            >
                                                Space
                                            </Link>
                                            <Link
                                                href="/tree-path"
                                                className={`block px-4 py-2 text-sm rounded-md transition-colors duration-150 ease-in-out
                                                ${pathname === '/tree-path'
                                                    ? 'text-blue-700 bg-blue-50'
                                                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                                }`}
                                            >
                                                Tree Path
                                            </Link>
                                            </div>
                                        </div>
                                        </div>
                                </div>
                            </div>
                            
                            {/* Right Side - XP Progress, User Profile & Logout */}
                            <div className="flex items-center space-x-4">
                                {/* XP Progress Bar */}
                                <XPProgress className="mr-2" />
                                
                                <Link 
                                    href="/profile"
                                    className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out
                                        ${pathname === '/profile' 
                                            ? 'text-blue-700 bg-blue-50' 
                                            : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                                        }`}
                                >
                                    Profile
                                </Link>
                                
                                <button 
                                    onClick={handleLogout}
                                    className="px-4 py-2 text-sm font-medium rounded-md text-gray-700 hover:text-red-600 hover:bg-red-50 transition-colors duration-150 ease-in-out"
                                >
                                    Sign Out
                                </button>
                            </div>
                        </div>
                    </div>
                </header>
            )}

            {/* Main content area */}
            <main className={`flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 ${isLoggedIn ? 'pt-0 md:pt-20 pb-16 md:pb-8' : 'py-8'}`}>
                {children}
            </main>

            {/* Mobile Bottom Navigation (only visible on smaller screens) */}
            {isLoggedIn && (
                <div className="fixed bottom-0 left-0 right-0 w-full bg-white border-t border-gray-200 md:hidden z-50">
                    <div className="grid grid-cols-5 py-2">
                        <Link 
                            href="/chat" 
                            className={`flex flex-col items-center text-xs ${pathname === '/chat' ? 'text-blue-600' : 'text-gray-600'}`}
                        >
                            <span className="material-icons-outlined">chat</span>
                            <span>Chat</span>
                        </Link>
                        <Link 
                            href="/peers" 
                            className={`flex flex-col items-center text-xs ${pathname === '/peers' ? 'text-blue-600' : 'text-gray-600'}`}
                        >
                            <span className="material-icons-outlined">people</span>
                            <span>Peers</span>
                        </Link>
                        
                        {/* More menu button */}
                        <div className="relative">
                            <button 
                                className="flex flex-col items-center w-full text-xs text-gray-600"
                                onClick={() => setMoreMenuOpen(!moreMenuOpen)}
                                aria-label="More options"
                            >
                                <span className="material-icons-outlined">more_horiz</span>
                                <span>More</span>
                            </button>
                            
                            {/* More dropdown menu */}
                            {moreMenuOpen && (
                                <div 
                                    ref={moreMenuRef}
                                    className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-56 mb-2 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden"
                                >
                                    <div className="py-1">
                                        <Link 
                                            href="/vector-search" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/vector-search' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-gray-500">trending_up</span>
                                            Career Recommendation
                                        </Link>
                                        <Link 
                                            href="/find-your-way" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/find-your-way' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-gray-500">explore</span>
                                            Pathway Explorer
                                        </Link>
                                        <Link 
                                            href="/career" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/career' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-gray-500">business</span>
                                            Career Explorer
                                        </Link>
                                        <Link 
                                            href="/enhanced-skills" 
                                            className={`flex items-center px-4 py-3 text-sm ${
                                                pathname === '/enhanced-skills' 
                                                    ? 'text-gray-900 font-medium' 
                                                    : 'text-gray-700 hover:text-gray-900'
                                            }`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-gray-500">school</span>
                                            Enhanced Skills Path
                                        </Link>
                                        <Link 
                                            href="/cv" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/cv' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-gray-500">description</span>
                                            Resume Builder
                                        </Link>
                                        <div className="border-t border-gray-200 mt-1"></div>
                                        <button 
                                            onClick={handleLogout}
                                            className="flex items-center w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50"
                                        >
                                            <span className="material-icons-outlined mr-2">logout</span>
                                            Logout
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        <div className="relative">
                            <button 
                                className={`flex flex-col items-center w-full text-xs ${
                                    pathname === '/space' || pathname === '/tree-paths' ? 'text-blue-600' : 'text-gray-600'
                                }`}
                                // onClick={toggleWorkspaceDropdown}
                                aria-label="Workspace options"
                            >
                                <span className="material-icons-outlined">folder</span>
                                <span>Workspace</span>
                            </button>
                            
                            {/* Mobile workspace dropdown menu */}
                            {/* {workspaceMenuOpen && (
                                <div 
                                    ref={workspaceMenuRef}
                                    className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-40 mb-2 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden"
                                >
                                    <div className="py-1">
                                        <Link 
                                            href="/space" 
                                            onClick={(e) => {
                                                e.preventDefault();
                                                console.log('Mobile: Navigating to /space');
                                                try {
                                                    router.push('/space');
                                                    // Fallback in case router.push doesn't trigger navigation
                                                    setTimeout(() => {
                                                        if (pathname !== '/space') {
                                                            console.log('Mobile Fallback: direct navigation to /space');
                                                            window.location.href = '/space';
                                                        }
                                                    }, 500);
                                                } catch (err) {
                                                    console.error('Mobile navigation error:', err);
                                                    window.location.href = '/space';
                                                }
                                            }}
                                            className={`flex items-center px-4 py-2 text-sm ${pathname === '/space' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-gray-500">folder</span>
                                            Workspace
                                        </Link>
                                        <Link 
                                            href="/tree-paths" 
                                            onClick={(e) => {
                                                e.preventDefault();
                                                console.log('Mobile: Navigating to /tree-paths');
                                                try {
                                                    router.push('/tree-paths');
                                                    // Fallback in case router.push doesn't trigger navigation
                                                    setTimeout(() => {
                                                        if (pathname !== '/tree-paths') {
                                                            console.log('Mobile Fallback: direct navigation to /tree-paths');
                                                            window.location.href = '/tree-paths';
                                                        }
                                                    }, 500);
                                                } catch (err) {
                                                    console.error('Mobile navigation error:', err);
                                                    window.location.href = '/tree-paths';
                                                }
                                            }}
                                            className={`flex items-center px-4 py-2 text-sm ${pathname === '/tree-paths' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-gray-500">account_tree</span>
                                            Tree Path
                                        </Link>
                                    </div>
                                </div>
                            )} */}
                        </div>
                        <Link 
                            href="/profile" 
                            className={`flex flex-col items-center text-xs ${pathname === '/profile' ? 'text-blue-600' : 'text-gray-600'}`}
                        >
                            <span className="material-icons-outlined">person</span>
                            <span>Profile</span>
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
}