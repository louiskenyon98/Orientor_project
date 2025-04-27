'use client';
import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';

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
    const moreMenuRef = useRef<HTMLDivElement>(null);
    const router = useRouter();
    const pathname = usePathname();

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/register'];
    const isPublicRoute = pathname ? publicRoutes.includes(pathname) : false;

    useEffect(() => {
        // Check if user is logged in
        const token = localStorage.getItem('access_token') || '';
        console.log('Token from localStorage:', token ? 'Found' : 'Not found');
        console.log('Current pathname:', pathname);
        console.log('Is public route:', isPublicRoute);
        console.log('Show nav:', showNav);
        
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

    // Close more menu when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (moreMenuRef.current && !moreMenuRef.current.contains(event.target as Node)) {
                setMoreMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    // Close mobile menus when route changes
    useEffect(() => {
        setMoreMenuOpen(false);
    }, [pathname]);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        router.push('/login');
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
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-teal"></div>
            </div>
        );
    }

    console.log('Rendering layout with isLoggedIn:', isLoggedIn);

    return (
        <div className="min-h-screen flex flex-col">
            {/* Desktop Navigation Bar - Only visible on larger screens */}
            {isLoggedIn && (
                <header className="fixed top-0 left-0 right-0 w-full z-50 bg-white/10 backdrop-blur-md border-b border-white/10 hidden md:block">
                    <nav className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                        <Link href="/" className="text-xl font-light tracking-wide text-neutral-800">
                            Navigo
                        </Link>
                        
                        <div className="flex gap-8">
                            <Link href="/chat" className="nav-link">Chat</Link>
                            <Link href="/peers" className="nav-link">Suggested Peers</Link>
                            <Link href="/vector-search" className="nav-link">Career recommendation</Link>
                            <Link href="/find-your-way" className="nav-link">Swipe Your Way</Link>
                            <Link href="/cv" className="nav-link">Resume Builder</Link>
                            <Link href="/space" className="nav-link">My Space</Link>
                            <Link href="/profile" className="nav-link">Profile</Link>
                            <button onClick={handleLogout} className="nav-link">Logout</button>
                        </div>
                    </nav>
                </header>
            )}

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
                                            Swipe Your Way
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
                        
                        <Link 
                            href="/space" 
                            className={`flex flex-col items-center text-xs ${pathname === '/space' ? 'text-blue-600' : 'text-gray-600'}`}
                        >
                            <span className="material-icons-outlined">folder</span>
                            <span>Space</span>
                        </Link>
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

            {/* Main content area */}
            <main className={`flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 ${isLoggedIn ? 'pt-0 md:pt-20 pb-16 md:pb-8' : 'py-8'}`}>
                {children}
            </main>
        </div>
    );
}