'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import ChatInterface from '@/components/chat/ChatInterface';

export default function ChatPage() {
    const router = useRouter();
    const [currentUserId, setCurrentUserId] = useState<number | null>(null);
    const [authError, setAuthError] = useState<string | null>(null);

    // Check authentication on mount
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            router.push('/login');
            return;
        }

        // Get user ID from token or local storage
        const userId = localStorage.getItem('user_id');
        if (userId) {
            setCurrentUserId(parseInt(userId));
        } else {
            // If no user ID, redirect to login
            console.error('No user ID found in localStorage');
            router.push('/login');
            return;
        }
    }, [router]);

    if (!currentUserId) {
        return (
            <MainLayout>
                <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            {authError && (
                <div className="absolute top-6 left-6 right-6 z-20">
                    <div className="bg-red-900/80 border border-red-500 text-red-200 px-4 py-3 rounded-lg backdrop-blur-sm shadow-lg">
                        {authError}
                    </div>
                </div>
            )}
            <ChatInterface currentUserId={currentUserId} />
        </MainLayout>
    );
} 
