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
            
            // Store the token in localStorage
            localStorage.setItem('access_token', response.data.access_token);
            
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
            
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-12">
            <div className="w-full max-w-md">
                <form className={styles.form} onSubmit={handleSubmit}>
                    <div id="heading" className={styles.heading}>Sign In</div>
                    <div className={styles.field}>
                        <span className={styles['input-icon']}>@</span>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            required
                            className={styles['input-field']}
                            placeholder="Adresse e-mail"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div className={styles.field}>
                        <span className={styles['input-icon']}>🔒</span>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            required
                            className={styles['input-field']}
                            placeholder="Mot de passe"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <div className={`${styles.form} ${styles.btn}`}>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className={styles.button1}
                        >
                            {isLoading ? 'Connexion...' : 'Se connecter'}
                        </button>
                        <Link href="/register" className={styles.button2}>S'inscrire</Link>
                    </div>
                    <button type="button" className={styles.button3} onClick={() => router.push('/')}>Back to Home</button>
                    {error && (
                        <div className="text-accent-coral text-sm text-center py-3 px-4 bg-accent-coral/10 border border-accent-coral/20 rounded-lg">
                            {error}
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
}