'use client';
import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import XPProgress from '../ui/XPProgress';
import DarkModeToggle from '../ui/DarkModeToggle';
import ThemeToggle from '../ui/ThemeToggle';
import styles from '@/styles/patterns.module.css';
import LoadingScreen from '@/components/ui/LoadingScreen';
import NewSidebar from './NewSidebar';

// Composants pour les menus déroulants
const ProfileDropdown = ({ pathname }: { pathname: string | null }) => {
    const [profileMenuOpen, setProfileMenuOpen] = useState(false);
    const profileMenuRef = useRef<HTMLDivElement>(null);

    // Fermer le menu lorsqu'on clique en dehors
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
                setProfileMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <div className="relative inline-block text-left" ref={profileMenuRef}>
            <button
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out flex items-center
                    ${pathname === '/profile' || pathname?.startsWith('/profile/')
                        ? 'text-blue-700 bg-blue-50 dark:text-blue-400 dark:bg-gray-800'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-gray-100 dark:hover:bg-gray-800'
                    }`}
            >
                Profile
                <svg
                    className={`ml-1 h-4 w-4 transition-transform duration-200 ${profileMenuOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            
            {profileMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-light-background dark:bg-dark-background ring-1 ring-black ring-opacity-5 z-40">
                    <div className="py-1" role="menu" aria-orientation="vertical">
                        <Link
                            href="/profile"
                            onClick={() => setProfileMenuOpen(false)}
                            className={`block px-4 py-2 text-sm ${pathname === '/profile' ? 'bg-blue-50 text-blue-700 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-gray-100'}`}
                            role="menuitem"
                        >
                            Informations générales
                        </Link>
                        <Link
                            href="/profile/holland-results"
                            onClick={() => setProfileMenuOpen(false)}
                            className={`block px-4 py-2 text-sm ${pathname === '/profile/holland-results' ? 'bg-blue-50 text-blue-700 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-gray-100'}`}
                            role="menuitem"
                        >
                            Résultats RIASEC
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
};

// Composant pour le menu déroulant du profil mobile
const MobileProfileMenu = ({
    pathname,
    setMoreMenuOpen,
    setCareerMenuOpen,
    setWorkspaceMenuOpen
}: {
    pathname: string | null;
    setMoreMenuOpen: (open: boolean) => void;
    setCareerMenuOpen: (open: boolean) => void;
    setWorkspaceMenuOpen: (open: boolean) => void;
}) => {
    const [profileMobileMenuOpen, setProfileMobileMenuOpen] = useState(false);
    const profileMobileMenuRef = useRef<HTMLDivElement>(null);
    const router = useRouter();
    
    // Fermer le menu lorsqu'on clique en dehors
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (profileMobileMenuRef.current && !profileMobileMenuRef.current.contains(event.target as Node)) {
                setProfileMobileMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);
    
    return (
        <div className="relative" ref={profileMobileMenuRef}>
            <button
                className={`flex flex-col items-center text-xs w-full ${pathname === '/profile' || pathname?.startsWith('/profile/') ? 'text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400'}`}
                onClick={() => {
                    setMoreMenuOpen(false);
                    setCareerMenuOpen(false);
                    setWorkspaceMenuOpen(false);
                    setProfileMobileMenuOpen(!profileMobileMenuOpen);
                }}
            >
                <span className="material-icons-outlined">person</span>
                <span>Profile</span>
            </button>
            
            {/* Menu du profil pour mobile */}
            {profileMobileMenuOpen && (
                <div className="absolute bottom-full right-0 mb-2 w-48 bg-light-background dark:bg-dark-background rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                    <div className="py-1">
                        <Link
                            href="/profile"
                            onClick={() => setProfileMobileMenuOpen(false)}
                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/profile' ? 'bg-blue-50 text-blue-600 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}`}
                        >
                            <span className="material-icons-outlined mr-2 text-gray-500 dark:text-gray-400">account_circle</span>
                            Informations générales
                        </Link>
                        <Link
                            href="/profile/holland-results"
                            onClick={() => setProfileMobileMenuOpen(false)}
                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/profile/holland-results' ? 'bg-blue-50 text-blue-600 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}`}
                        >
                            <span className="material-icons-outlined mr-2 text-gray-500 dark:text-gray-400">psychology</span>
                            Résultats RIASEC
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
};

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

    // Navigation items for the sidebar
    const navItems = [
        { name: 'Dashboard', icon: 'Dashboard', path: '/' },
        { name: 'Education', icon: 'Education', path: '/education' },
        { name: 'Chat', icon: 'Chat', path: '/chat' },
        { name: 'Peers', icon: 'Peers', path: '/peers' },
        { name: 'Swipe', icon: 'Swipe', path: '/find-your-way' },
        { name: 'Saved', icon: 'Bookmark', path: '/space' },
        { name: 'Challenges', icon: 'Trophy', path: '/challenges' },
        { name: 'Notes', icon: 'Note', path: '/notes' },
        { name: 'Case Study', icon: 'Case Study', path: '/case-study-journey' },
        { name: 'Competence Tree', icon: 'Tree', path: '/competence-tree' },
    ];

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/register', '/test-page'];
    const isPublicRoute = pathname ? publicRoutes.includes(pathname) : false;

    useEffect(() => {
        // Check if user is logged in
        const token = localStorage.getItem('access_token') || '';
        console.log('Auth check - Token:', token ? 'Found' : 'Not found', 'Pathname:', pathname);
        
        // Désactivé temporairement pour le développement
        // if (!token && !isPublicRoute && showNav) {
        //     console.log('No token found, redirecting to login');
        //     router.push('/login');
        //     return;
        // }
        
        // Pour le développement, considérer l'utilisateur comme connecté
        const loggedIn = true; // !!token;
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
        return <LoadingScreen message="Loading..." />;
    }

    // Check if current path is in career path section
    const isCareerPath = ['/vector-search', '/find-your-way', '/cv', '/tree'].includes(pathname || '');

    console.log('Rendering layout with isLoggedIn:', isLoggedIn);

    return (
        <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#ffffff' }}>
            {/* Desktop Navigation Bar - Only visible on larger screens */}
            {isLoggedIn && (
            //             <div className="min-h-screen bg-light-background dark:bg-dark-background">
            // {showNav && (
                <header className="fixed top-0 left-0 right-0 w-full z-50 px-4 py-3 hidden md:block font-departure header" style={{ backgroundColor: '#ffffff' }}>
                    <div className="w-full px-4">
                        <div className="flex justify-between items-center w-full">
                            {/* Left Side - Logo and Greeting side by side - positioned at far left */}
                            <div className="flex items-center gap-4">
                                {/* Logo */}
                                <Link href="/landing" className="flex-shrink-0 flex items-center">
                                    <span className="text-xl font-bold tracking-tight text-stitch-accent font-departure">
                                        Navigo
                                    </span>
                                </Link>
                                
                                {/* User Greeting - directly to the right */}
                                <div className="flex flex-col">
                                    <h1 className="text-2xl font-bold" style={{ color: '#000000' }}>
                                        Hey Phil
                                    </h1>
                                    <p className="text-sm" style={{ color: '#666666' }}>
                                        It's sunny today and it's time to explore 🌞
                                    </p>
                                </div>
                            </div>

                            {/* Right Side - Chat, XP Progress, Dark Mode Toggle */}
                            <div className="flex items-center space-x-4">
                                {/* Chat Icon */}
                                <Link 
                                    href="/chat" 
                                    className={`p-2 text-sm font-bold rounded-md transition-colors duration-150 ease-in-out font-departure
                                        ${pathname === '/chat'
                                            ? 'text-stitch-accent bg-stitch-primary/50'
                                            : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                        }`}
                                >
                                    <span className="material-icons-outlined">chat</span>
                                </Link>
                                
                                {/* XP Progress Bar */}
                                <div className="relative group">
                                    <XPProgress className="mr-2" />
                                    <div className="absolute inset-0 bg-stitch-accent/10 blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full"></div>
                                </div>
                                
                                {/* Theme Toggle */}
                                <ThemeToggle />
                                
                                {/* Logout Button */}
                                <button
                                    onClick={handleLogout}
                                    className="p-2 text-sm font-bold rounded-md text-stitch-sage hover:text-red-500 hover:bg-stitch-primary/30 transition-colors duration-150 ease-in-out"
                                >
                                    <span className="material-icons-outlined">logout</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </header>
            )}

            {/* Main content area with sidebar */}
            <div className="flex w-full h-full grow relative z-10">
                {/* Sidebar - visible on desktop only */}
                {isLoggedIn && showNav && (
                    <div className="hidden md:block">
                        <NewSidebar navItems={navItems} />
                    </div>
                )}
                
                {/* Main content */}
                <main className={`flex-1 w-full ${isLoggedIn && showNav ? 'md:ml-20' : ''} ${isLoggedIn ? 'pt-0 md:pt-20 pb-50 md:pb-20' : 'py-20'}`} style={{ backgroundColor: '#ffffff' }}>
                    <div className="w-full">
                        {children}
                    </div>
                </main>
            </div>

            {/* Mobile Bottom Navigation (only visible on smaller screens) */}
            {isLoggedIn && (
                <div className="fixed bottom-0 left-0 right-0 w-full bg-stitch-primary border-t border-stitch-border md:hidden z-50 font-departure">
                    <div className="grid grid-cols-5 py-2">
                        <Link 
                            href="/education" 
                            className={`flex flex-col items-center text-xs font-departure relative ${pathname === '/education' ? 'text-stitch-accent' : 'text-stitch-sage'}`}
                        >
                            <span className="material-icons-outlined">school</span>
                            <span>Education</span>
                            <span className="absolute -top-1 right-2 bg-stitch-accent text-white text-xs rounded-full px-1">New</span>
                        </Link>
                        <Link 
                            href="/chat" 
                            className={`flex flex-col items-center text-xs font-departure ${pathname === '/chat' ? 'text-stitch-accent' : 'text-stitch-sage'}`}
                        >
                            <span className="material-icons-outlined">chat</span>
                            <span>Chat</span>
                        </Link>
                        <Link 
                            href="/peers" 
                            className={`flex flex-col items-center text-xs font-departure ${pathname === '/peers' ? 'text-stitch-accent' : 'text-stitch-sage'}`}
                        >
                            <span className="material-icons-outlined">people</span>
                            <span>Peers</span>
                        </Link>
                        
                        {/* More menu button */}
                        <div className="relative">
                            <button 
                                className="flex flex-col items-center w-full text-xs text-stitch-sage font-departure"
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
                                    className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-56 mb-2 bg-stitch-primary rounded-lg shadow-lg border border-stitch-border overflow-hidden"
                                >
                                    <div className="py-1">
                                        {/* Dropdown menu items with dark mode styles */}
                                        <Link 
                                            href="/vector-search" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/vector-search' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">trending_up</span>
                                            Career Recommendation
                                        </Link>
                                        <Link 
                                            href="/find-your-way" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/find-your-way' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">explore</span>
                                            Pathway Explorer
                                        </Link>
                                        <Link 
                                            href="/career" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/career' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">business</span>
                                            Career Explorer
                                        </Link>
                                        <Link 
                                            href="/enhanced-skills" 
                                            className={`flex items-center px-4 py-3 text-sm ${
                                                pathname === '/enhanced-skills'
                                                    ? 'bg-stitch-primary/50 text-stitch-accent font-bold'
                                                    : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'
                                            }`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">school</span>
                                            Enhanced Skills Path
                                        </Link>
                                        <Link
                                            href="/holland-test"
                                            className={`flex items-center px-4 py-3 text-sm ${
                                                pathname === '/holland-test'
                                                    ? 'bg-stitch-primary/50 text-stitch-accent font-bold'
                                                    : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'
                                            }`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">psychology</span>
                                            Test Holland (RIASEC)
                                        </Link>
                                        <Link
                                            href="/education"
                                            className={`flex items-center px-4 py-3 text-sm ${
                                                pathname === '/education'
                                                    ? 'bg-stitch-primary/50 text-stitch-accent font-bold'
                                                    : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'
                                            }`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">school</span>
                                            Education Programs
                                            <span className="ml-2 px-2 py-1 text-xs bg-stitch-accent text-white rounded-full">New</span>
                                        </Link>
                                        <div className="border-t border-stitch-border mt-1"></div>
                                        
                                        {/* Theme Toggle in mobile menu */}
                                        <div className="flex items-center px-4 py-3">
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">palette</span>
                                            <span className="text-sm text-stitch-sage mr-auto">Thème</span>
                                            <ThemeToggle />
                                        </div>
                                        
                                        <button 
                                            onClick={handleLogout}
                                            className="flex items-center w-full px-4 py-3 text-sm text-red-500 hover:bg-stitch-primary/30"
                                        >
                                            <span className="material-icons-outlined mr-2">logout</span>
                                            Logout
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        <div className="relative">
                            <Link
                                href="/space"
                                className={`flex flex-col items-center w-full text-xs ${
                                    pathname === '/space' || pathname === '/tree-path'
                                        ? 'text-stitch-accent'
                                        : 'text-stitch-sage'
                                }`}
                                onClick={(e) => {
                                    e.preventDefault();
                                    setWorkspaceMenuOpen(!workspaceMenuOpen);
                                }}
                            >
                                <span className="material-icons-outlined">folder</span>
                                <span>Workspace</span>
                            </Link>
                            
                        {/* Mobile Workspace Dropdown Menu */}
                        {workspaceMenuOpen && (
                            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-56 mb-2 bg-stitch-primary rounded-lg shadow-lg border border-stitch-border overflow-hidden">
                                <div className="py-1">
                                    <Link 
                                        href="/space"
                                        onClick={() => setWorkspaceMenuOpen(false)}
                                        className={`block px-4 py-2 text-sm rounded-md transition-colors duration-150 ease-in-out
                                            ${pathname === '/space'
                                                ? 'text-stitch-accent bg-stitch-primary/50'
                                                : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                            }`}
                                    >
                                        <span className="material-icons-outlined mr-2 text-stitch-sage">space_dashboard</span>
                                        Space
                                    </Link>
                                    <Link 
                                        href="/tree-path"
                                        onClick={() => setWorkspaceMenuOpen(false)}
                                        className={`block px-4 py-2 text-sm rounded-md transition-colors duration-150 ease-in-out
                                            ${pathname === '/tree-path'
                                                ? 'text-stitch-accent bg-stitch-primary/50'
                                                : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                            }`}
                                    >
                                        <span className="material-icons-outlined mr-2 text-stitch-sage">account_tree</span>
                                        Tree Path
                                    </Link>
                                </div>
                            </div>
                        )}
                        </div>
                        <MobileProfileMenu
                            pathname={pathname}
                            setMoreMenuOpen={setMoreMenuOpen}
                            setCareerMenuOpen={setCareerMenuOpen}
                            setWorkspaceMenuOpen={setWorkspaceMenuOpen}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}