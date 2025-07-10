'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { endpoint, logApiDetails } from '@/utils/api';
import styles from './login-black.module.css';

interface LoginResponse {
    access_token: string;
    token_type: string;
    user_id: number;
}

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('access_token');
        if (token) {
            router.push('/dashboard');
        }
        
        // Log API details for debugging
        logApiDetails();
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        
        try {
            console.log('Attempting to login with:', { email });
            
            const loginUrl = endpoint('/auth/login');
            console.log('Full login URL:', loginUrl);
            
            const response = await axios.post<LoginResponse>(
                loginUrl,
                { email, password },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    timeout: 10000
                }
            );
            
            console.log('Login successful, token received');
            
            // Store the token and user ID in localStorage
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('user_id', response.data.user_id.toString());
            
            // Check if user needs onboarding
            try {
                const { onboardingService } = await import('../../services/onboardingService');
                const needsOnboarding = await onboardingService.needsOnboarding();
                
                if (needsOnboarding) {
                    router.push('/onboarding');
                } else {
                    router.push('/dashboard');
                }
            } catch (onboardingError) {
                console.log('Could not check onboarding status, redirecting to dashboard');
                router.push('/dashboard');
            }
        } catch (err: any) {
            console.error('Login error details:', {
                message: err.message,
                status: err.response?.status,
                statusText: err.response?.statusText,
                data: err.response?.data
            });
            
            // Handle different error cases
            if (err.code === 'ECONNABORTED') {
                setError('Connection timeout. The server took too long to respond.');
            } else if (err.message.includes('Network Error')) {
                setError('Network error. Please check your connection or the server might be down.');
            } else if (err.response?.status === 401) {
                setError('Invalid email or password');
            } else if (err.response?.status === 403) {
                setError('Access forbidden. You may not have permission to log in.');
            } else if (err.response?.status === 404) {
                setError('Login endpoint not found. Please contact support.');
            } else if (err.response?.status === 500) {
                setError('Server error. Please try again later.');
            } else {
                setError(err.response?.data?.detail || 'Login failed. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.loginForm}>
                <div className={styles.header}>
                    <h1 className={styles.title}>Navigo</h1>
                    <p className={styles.subtitle}>Welcome back</p>
                </div>
                
                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <div className={styles.inputWrapper}>
                            <svg className={styles.inputIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                            </svg>
                            <input
                                type="email"
                                className={styles.input}
                                placeholder="Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                disabled={isLoading}
                            />
                        </div>
                    </div>

                    <div className={styles.inputGroup}>
                        <div className={styles.inputWrapper}>
                            <svg className={styles.inputIcon} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                            <input
                                type="password"
                                className={styles.input}
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                disabled={isLoading}
                            />
                        </div>
                    </div>

                    {error && (
                        <div className={styles.error}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <div className={styles.spinner}>
                                <div className={styles.spinnerInner}></div>
                            </div>
                        ) : (
                            'Sign In'
                        )}
                    </button>
                </form>

                <div className={styles.links}>
                    <p className={styles.linkText}>
                        Don't have an account?{' '}
                        <Link href="/register" className={styles.link}>
                            Create account
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}