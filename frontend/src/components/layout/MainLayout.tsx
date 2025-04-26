'use client';
import { useEffect, useState } from 'react';
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
    const router = useRouter();
    const pathname = usePathname();

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/register'];
    const isPublicRoute = publicRoutes.includes(pathname);

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
            {/* Navigation Bar - Only show when logged in */}
            {isLoggedIn && (
                <header className="fixed top-0 left-0 right-0 w-full z-50 bg-white/10 backdrop-blur-md border-b border-white/10">
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

            {/* Mobile Navigation (only visible on smaller screens) */}
            {isLoggedIn && (
                <div className="fixed bottom-0 left-0 right-0 w-full bg-white border-t border-gray-200 md:hidden z-50">
                    <div className="grid grid-cols-5 py-2">
                        <Link href="/chat" className="flex flex-col items-center text-xs text-gray-600">
                            <span className="material-icons-outlined">chat</span>
                            <span>Chat</span>
                        </Link>
                        <Link href="/peers" className="flex flex-col items-center text-xs text-gray-600">
                            <span className="material-icons-outlined">people</span>
                            <span>Peers</span>
                        </Link>
                        <Link href="/find-your-way" className="flex flex-col items-center text-xs text-gray-600">
                            <span className="material-icons-outlined">explore</span>
                            <span>Find Way</span>
                        </Link>
                        <Link href="/space" className="flex flex-col items-center text-xs text-gray-600">
                            <span className="material-icons-outlined">folder</span>
                            <span>My Space</span>
                        </Link>
                        <Link href="/profile" className="flex flex-col items-center text-xs text-gray-600">
                            <span className="material-icons-outlined">person</span>
                            <span>Profile</span>
                        </Link>
                    </div>
                </div>
            )}

            {/* Main content area */}
            <main className={`flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 ${isLoggedIn ? 'pt-20 pb-16 md:pb-8' : 'py-8'}`}>
                {children}
            </main>
        </div>
    );
}