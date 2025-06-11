'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { endpoint, logApiDetails } from '@/utils/api';
import styles from './loginForm.module.css';

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
            router.push('/chat');
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
            
            // Redirect to chat page after successful login
            router.push('/chat');
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
            <input type="checkbox" id={styles.signup_toggle} />
            <div className={styles.form}>
                <div className={styles.form_front}>
                    <div className={styles.form_details}>Sign In To Navigo</div>
                    <form onSubmit={handleSubmit}>
                        <input
                            type="email"
                            className={styles.input}
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                        <input
                            type="password"
                            className={styles.input}
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <button type="submit" className={styles.btn} disabled={isLoading}>
                            {isLoading ? 'Signing in...' : 'Sign In'}
                        </button>
                        {error && <div className={styles.error}>{error}</div>}
                    </form>
                    <div className={styles.switch}>
                        Don't have an account?{' '}
                        <label htmlFor={styles.signup_toggle} className={styles.signup_tog}>
                            Sign Up
                        </label>
                    </div>
                </div>

                <div className={styles.form_back}>
                    <div className={styles.form_details}>Sign Up</div>
                    <form>
                        <input
                            type="email"
                            className={styles.input}
                            placeholder="Email"
                            required
                        />
                        <input
                            type="password"
                            className={styles.input}
                            placeholder="Password"
                            required
                        />
                        <input
                            type="password"
                            className={styles.input}
                            placeholder="Confirm Password"
                            required
                        />
                        <Link href="/register" className={styles.btn}>
                            Sign Up
                        </Link>
                    </form>
                    <div className={styles.switch}>
                        Already have an account?{' '}
                        <label htmlFor={styles.signup_toggle} className={styles.signup_tog}>
                            Sign In
                        </label>
                    </div>
                </div>
            </div>
        </div>
    );
}