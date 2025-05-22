'use client';
import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import axios from 'axios';

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

interface ApiError {
    response?: {
        data?: {
            detail?: string;
        };
        status?: number;
    };
    message?: string;
}

interface Profile {
    user_id: number;
    name: string | null;
    age: number | null;
    sex: string | null;
    major: string | null;
    year: number | null;
    gpa: number | null;
    hobbies: string | null;
    country: string | null;
    state_province: string | null;
    unique_quality: string | null;
    story: string | null;
    favorite_movie: string | null;
    favorite_book: string | null;
    favorite_celebrities: string | null;
    learning_style: string | null;
    interests: string[] | null;
    // Career fields
    job_title: string | null;
    industry: string | null;
    years_experience: number | null;
    education_level: string | null;
    career_goals: string | null;
    skills: string[] | null;
    // Skill scores
    creativity: number | null;
    leadership: number | null;
    digital_literacy: number | null;
    critical_thinking: number | null;
    problem_solving: number | null;
    // Cognitive traits
    analytical_thinking: number | null;
    attention_to_detail: number | null;
    collaboration: number | null;
    adaptability: number | null;
    independence: number | null;
    evaluation: number | null;
    decision_making: number | null;
    stress_tolerance: number | null;
}

export default function ProfilePage() {
    const [activeTab, setActiveTab] = useState('basic');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [rawInputs, setRawInputs] = useState({
        skills: '',
        interests: ''
    });
    const [profile, setProfile] = useState<Profile>({
        user_id: 0,
        name: null,
        age: null,
        sex: null,
        major: null,
        year: null,
        gpa: null,
        hobbies: null,
        country: null,
        state_province: null,
        unique_quality: null,
        story: null,
        favorite_movie: null,
        favorite_book: null,
        favorite_celebrities: null,
        learning_style: null,
        interests: null,
        job_title: null,
        industry: null,
        years_experience: null,
        education_level: null,
        career_goals: null,
        skills: null,
        creativity: null,
        leadership: null,
        digital_literacy: null,
        critical_thinking: null,
        problem_solving: null,
        analytical_thinking: null,
        attention_to_detail: null,
        collaboration: null,
        adaptability: null,
        independence: null,
        evaluation: null,
        decision_making: null,
        stress_tolerance: null
    });
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    // Fetch existing profile data when component mounts
    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    console.error('No access token found');
                    return;
                }
                
                const response = await axios.get<Profile>(`${cleanApiUrl}/profiles/me`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                console.log('Profile data received:', response.data);
                
                // First set the profile data
                setProfile(response.data);
                
                // Then properly format and set the raw inputs
                const formattedSkills = Array.isArray(response.data.skills) 
                    ? response.data.skills.join(', ')
                    : '';
                    
                const formattedinterests = Array.isArray(response.data.interests)
                    ? response.data.interests.join(', ')
                    : '';
                
                setRawInputs({
                    skills: formattedSkills,
                    interests: formattedinterests
                });
                setProfile(prev => ({
                    ...prev,
                    skills: response.data.skills || [],
                    interests: response.data.interests || []
                }));
            } catch (err) {
                const error = err as ApiError;
                console.error('Error fetching profile:', error.response?.data || error.message);
                setError(error.response?.data?.detail || 'Failed to fetch profile');
            }
        };
        fetchProfile();
    }, []);

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('access_token');
            
            // Process arrays and skill scores before sending
            const processedProfile = {
                ...profile,
                skills: rawInputs.skills
                    .split(',')
                    .map(item => item.trim())
                    .filter(item => item !== ''),
                interests: rawInputs.interests
                    .split(',')
                    .map(item => item.trim())
                    .filter(item => item !== ''),
                // Convert skill scores to numbers or null
                creativity: profile.creativity === null || profile.creativity === undefined ? null : Number(profile.creativity),
                leadership: profile.leadership === null || profile.leadership === undefined ? null : Number(profile.leadership),
                digital_literacy: profile.digital_literacy === null || profile.digital_literacy === undefined ? null : Number(profile.digital_literacy),
                critical_thinking: profile.critical_thinking === null || profile.critical_thinking === undefined ? null : Number(profile.critical_thinking),
                problem_solving: profile.problem_solving === null || profile.problem_solving === undefined ? null : Number(profile.problem_solving),
                // Convert cognitive traits to numbers
                analytical_thinking: profile.analytical_thinking === null || profile.analytical_thinking === undefined ? null : Number(profile.analytical_thinking),
                attention_to_detail: profile.attention_to_detail === null || profile.attention_to_detail === undefined ? null : Number(profile.attention_to_detail),
                collaboration: profile.collaboration === null || profile.collaboration === undefined ? null : Number(profile.collaboration),
                adaptability: profile.adaptability === null || profile.adaptability === undefined ? null : Number(profile.adaptability),
                independence: profile.independence === null || profile.independence === undefined ? null : Number(profile.independence),
                evaluation: profile.evaluation === null || profile.evaluation === undefined ? null : Number(profile.evaluation),
                decision_making: profile.decision_making === null || profile.decision_making === undefined ? null : Number(profile.decision_making),
                stress_tolerance: profile.stress_tolerance === null || profile.stress_tolerance === undefined ? null : Number(profile.stress_tolerance)
            };

            // Create a clean profile object with all fields
            const cleanProfile = {
                user_id: processedProfile.user_id,
                // Basic Info
                name: processedProfile.name || null,
                age: processedProfile.age || null,
                sex: processedProfile.sex || null,
                country: processedProfile.country || null,
                state_province: processedProfile.state_province || null,
                
                // Academic Info
                major: processedProfile.major || null,
                year: processedProfile.year || null,
                gpa: processedProfile.gpa || null,
                learning_style: processedProfile.learning_style || null,
                
                // Personal Info
                hobbies: processedProfile.hobbies || null,
                unique_quality: processedProfile.unique_quality || null,
                story: processedProfile.story || null,
                favorite_movie: processedProfile.favorite_movie || null,
                favorite_book: processedProfile.favorite_book || null,
                favorite_celebrities: processedProfile.favorite_celebrities || null,
                
                // Career Info
                job_title: processedProfile.job_title || null,
                industry: processedProfile.industry || null,
                years_experience: processedProfile.years_experience || null,
                education_level: processedProfile.education_level || null,
                career_goals: processedProfile.career_goals || null,
                skills: processedProfile.skills,
                interests: processedProfile.interests,
                
                // Skill scores
                creativity: processedProfile.creativity,
                leadership: processedProfile.leadership,
                digital_literacy: processedProfile.digital_literacy,
                critical_thinking: processedProfile.critical_thinking,
                problem_solving: processedProfile.problem_solving,
                
                // Cognitive traits
                analytical_thinking: processedProfile.analytical_thinking,
                attention_to_detail: processedProfile.attention_to_detail,
                collaboration: processedProfile.collaboration,
                adaptability: processedProfile.adaptability,
                independence: processedProfile.independence,
                evaluation: processedProfile.evaluation,
                decision_making: processedProfile.decision_making,
                stress_tolerance: processedProfile.stress_tolerance
            };

            // Update user info
            if (email || password) {
                await axios.put(
                    `${cleanApiUrl}/users/update`,
                    { email, password },
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                            'Content-Type': 'application/json',
                        },
                    }
                );
            }

            // Update profile info
            const response = await axios.put(
                `${cleanApiUrl}/profiles/update`,
                cleanProfile,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                }
            );
            
            setMessage('Profile updated successfully!');
            setError(null);
        } catch (err) {
            const error = err as ApiError;
            console.error('Profile update error:', error.response?.data);
            setError(error.response?.data?.detail || 'Update failed');
            setMessage(null);
        }
    };

    const handleProfileChange = (field: keyof Profile) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        let value: string | number | string[] | null = e.target.value;
        
        // Convert numeric fields
        if (['age', 'year', 'years_experience'].includes(field) && value !== '') {
            value = parseInt(value) || null;
        } else if (field === 'gpa' && value !== '') {
            value = parseFloat(value) || null;
        } else if (value === '') {
            value = null;
        }
        
        setProfile(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleArrayChange = (field: 'interests' | 'skills') => (e: React.ChangeEvent<HTMLInputElement>) => {
        e.stopPropagation();
        const value = e.target.value;
        setRawInputs(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleArrayBlur = (field: 'interests' | 'skills') => () => {
        const value = rawInputs[field];
        // Split by comma, trim each item, and filter out empty strings
        const array = value
            .split(',')
            .map(item => item.trim())
            .filter(item => item !== '');
        
        // Update the profile with the processed array
        setProfile(prev => ({
            ...prev,
            [field]: array
        }));
    };

    return (
        <MainLayout>
            <div className="max-w-4xl mx-auto space-y-6">
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-neutral-lightgray">Your Profile</h2>
                    <div className="text-sm text-neutral-lightgray opacity-70">
                        Help us personalize your experience
                    </div>
                </div>
                
                <div className="card">
                    <form onSubmit={handleUpdate} className="space-y-6">
                        {/* Tabs */}
                        <div className="border-b border-gray-200">
                            <nav className="-mb-px flex space-x-8">
                                <button
                                    type="button"
                                    onClick={() => setActiveTab('basic')}
                                    className={`${
                                        activeTab === 'basic'
                                            ? 'border-secondary-teal text-secondary-teal'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                                >
                                    Basic Info
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setActiveTab('academic')}
                                    className={`${
                                        activeTab === 'academic'
                                            ? 'border-secondary-teal text-secondary-teal'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                                >
                                    Academic
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setActiveTab('career')}
                                    className={`${
                                        activeTab === 'career'
                                            ? 'border-secondary-teal text-secondary-teal'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                                >
                                    Career
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setActiveTab('personal')}
                                    className={`${
                                        activeTab === 'personal'
                                            ? 'border-secondary-teal text-secondary-teal'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                                >
                                    Personal
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setActiveTab('account')}
                                    className={`${
                                        activeTab === 'account'
                                            ? 'border-secondary-teal text-secondary-teal'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                                >
                                    Account
                                </button>
                            </nav>
                        </div>

                        {/* Tab Content */}
                        <div className="mt-6">
                            {activeTab === 'basic' && (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Full Name
                                            </label>
                                            <input
                                                type="text"
                                                value={profile.name || ''}
                                                onChange={handleProfileChange('name')}
                                                className="input"
                                                placeholder="Your full name"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Age
                                            </label>
                                            <input
                                                type="number"
                                                value={profile.age || ''}
                                                onChange={handleProfileChange('age')}
                                                className="input"
                                                placeholder="Your age"
                                                min="0"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Sex
                                            </label>
                                            <select
                                                value={profile.sex || ''}
                                                onChange={handleProfileChange('sex')}
                                                className="input bg-gray-100"
                                            >
                                                <option value="">Select your sex</option>
                                                <option value="Male">Male</option>
                                                <option value="Female">Female</option>
                                                <option value="Other">Other</option>
                                                <option value="Prefer not to say">Prefer not to say</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Country
                                            </label>
                                            <input
                                                type="text"
                                                value={profile.country || ''}
                                                onChange={handleProfileChange('country')}
                                                className="input"
                                                placeholder="Your country"
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'academic' && (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Major
                                            </label>
                                            <input
                                                type="text"
                                                value={profile.major || ''}
                                                onChange={handleProfileChange('major')}
                                                className="input"
                                                placeholder="Your major"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Year
                                            </label>
                                            <input
                                                type="number"
                                                value={profile.year || ''}
                                                onChange={handleProfileChange('year')}
                                                className="input"
                                                placeholder="Your year"
                                                min="1"
                                                max="4"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                GPA
                                            </label>
                                            <input
                                                type="number"
                                                value={profile.gpa || ''}
                                                onChange={handleProfileChange('gpa')}
                                                className="input"
                                                placeholder="Your GPA"
                                                step="0.01"
                                                min="0"
                                                max="4"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Learning Style
                                            </label>
                                            <select
                                                value={profile.learning_style || ''}
                                                onChange={handleProfileChange('learning_style')}
                                                className="input bg-gray-100"
                                            >
                                                <option value="">Select your learning style</option>
                                                <option value="Visual">Visual</option>
                                                <option value="Auditory">Auditory</option>
                                                <option value="Reading/Writing">Reading/Writing</option>
                                                <option value="Kinesthetic">Kinesthetic</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'career' && (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Job Title
                                            </label>
                                            <input
                                                type="text"
                                                value={profile.job_title || ''}
                                                onChange={handleProfileChange('job_title')}
                                                className="input"
                                                placeholder="Your current or desired job title"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Industry
                                            </label>
                                            <input
                                                type="text"
                                                value={profile.industry || ''}
                                                onChange={handleProfileChange('industry')}
                                                className="input"
                                                placeholder="Your industry"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Years of Experience
                                            </label>
                                            <input
                                                type="number"
                                                value={profile.years_experience || ''}
                                                onChange={handleProfileChange('years_experience')}
                                                className="input"
                                                placeholder="Years of experience"
                                                min="0"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Education Level
                                            </label>
                                            <select
                                                value={profile.education_level || ''}
                                                onChange={handleProfileChange('education_level')}
                                                className="input bg-gray-100"
                                            >
                                                <option value="">Select your education level</option>
                                                <option value="High School">High School</option>
                                                <option value="Associate's Degree">Associate's Degree</option>
                                                <option value="Bachelor's Degree">Bachelor's Degree</option>
                                                <option value="Master's Degree">Master's Degree</option>
                                                <option value="Doctorate">Doctorate</option>
                                            </select>
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Career Goals
                                            </label>
                                            <textarea
                                                value={profile.career_goals || ''}
                                                onChange={handleProfileChange('career_goals')}
                                                className="input"
                                                placeholder="Describe your career goals"
                                                rows={3}
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Skills (comma-separated)
                                            </label>
                                            <input
                                                type="text"
                                                value={rawInputs.skills}
                                                onChange={handleArrayChange('skills')}
                                                onBlur={handleArrayBlur('skills')}
                                                placeholder="e.g., Python, Data Analysis, Machine Learning"
                                                className="input"
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                interests
                                            </label>
                                            <input
                                                type="text"
                                                value={rawInputs.interests}
                                                onChange={handleArrayChange('interests')}
                                                onBlur={handleArrayBlur('interests')}
                                                placeholder="e.g., AI, Web Development, Design"
                                                className="input"
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <h3 className="text-lg font-medium text-neutral-lightgray mb-4">Skill Scores</h3>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Creativity: {profile.creativity || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.creativity || 0}
                                                        onChange={handleProfileChange('creativity')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Leadership: {profile.leadership || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.leadership || 0}
                                                        onChange={handleProfileChange('leadership')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Digital Literacy: {profile.digital_literacy || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.digital_literacy || 0}
                                                        onChange={handleProfileChange('digital_literacy')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Critical Thinking: {profile.critical_thinking || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.critical_thinking || 0}
                                                        onChange={handleProfileChange('critical_thinking')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Problem Solving: {profile.problem_solving || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.problem_solving || 0}
                                                        onChange={handleProfileChange('problem_solving')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                        <div className="md:col-span-2">
                                            <h3 className="text-lg font-medium text-neutral-lightgray mb-4">Cognitive Traits</h3>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Analytical Thinking: {profile.analytical_thinking || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.analytical_thinking || 0}
                                                        onChange={handleProfileChange('analytical_thinking')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Attention to Detail: {profile.attention_to_detail || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.attention_to_detail || 0}
                                                        onChange={handleProfileChange('attention_to_detail')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Collaboration: {profile.collaboration || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.collaboration || 0}
                                                        onChange={handleProfileChange('collaboration')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Adaptability: {profile.adaptability || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.adaptability || 0}
                                                        onChange={handleProfileChange('adaptability')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Independence: {profile.independence || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.independence || 0}
                                                        onChange={handleProfileChange('independence')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Evaluation: {profile.evaluation || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.evaluation || 0}
                                                        onChange={handleProfileChange('evaluation')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Decision Making: {profile.decision_making || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.decision_making || 0}
                                                        onChange={handleProfileChange('decision_making')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                        Stress Tolerance: {profile.stress_tolerance || 0}
                                                    </label>
                                                    <input
                                                        type="range"
                                                        value={profile.stress_tolerance || 0}
                                                        onChange={handleProfileChange('stress_tolerance')}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                        min="0"
                                                        max="5"
                                                        step="0.5"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'account' && (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Email Address
                                            </label>
                                            <input
                                                type="email"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                className="input"
                                                placeholder="your@email.com"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                New Password
                                            </label>
                                            <input
                                                type="password"
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                className="input"
                                                placeholder="Leave blank to keep current password"
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'personal' && (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Hobbies
                                            </label>
                                            <textarea
                                                value={profile.hobbies || ''}
                                                onChange={handleProfileChange('hobbies')}
                                                className="input"
                                                placeholder="Your hobbies"
                                                rows={3}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Unique Quality
                                            </label>
                                            <textarea
                                                value={profile.unique_quality || ''}
                                                onChange={handleProfileChange('unique_quality')}
                                                className="input"
                                                placeholder="What makes you unique?"
                                                rows={3}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Your Story
                                            </label>
                                            <textarea
                                                value={profile.story || ''}
                                                onChange={handleProfileChange('story')}
                                                className="input"
                                                placeholder="Tell us your story"
                                                rows={3}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Favorite Movie
                                            </label>
                                            <input
                                                type="text"
                                                value={profile.favorite_movie || ''}
                                                onChange={handleProfileChange('favorite_movie')}
                                                className="input"
                                                placeholder="Your favorite movie"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Favorite Book
                                            </label>
                                            <input
                                                type="text"
                                                value={profile.favorite_book || ''}
                                                onChange={handleProfileChange('favorite_book')}
                                                className="input"
                                                placeholder="Your favorite book"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Role Model
                                            </label>
                                            <input
                                                type="text"
                                                value={profile.favorite_celebrities || ''}
                                                onChange={handleProfileChange('favorite_celebrities')}
                                                className="input"
                                                placeholder="Your role model or favorite celebrity"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                Learning Style
                                            </label>
                                            <select
                                                value={profile.learning_style || ''}
                                                onChange={handleProfileChange('learning_style')}
                                                className="input bg-gray-100"
                                            >
                                                <option value="">Select your learning style</option>
                                                <option value="Visual">Visual</option>
                                                <option value="Auditory">Auditory</option>
                                                <option value="Reading/Writing">Reading/Writing</option>
                                                <option value="Kinesthetic">Kinesthetic</option>
                                            </select>
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                interests
                                            </label>
                                            <input
                                                type="text"
                                                value={rawInputs.interests}
                                                onChange={handleArrayChange('interests')}
                                                onBlur={handleArrayBlur('interests')}
                                                placeholder="e.g., AI, Web Development, Design"
                                                className="input"
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Error and Success Messages */}
                        {error && (
                            <div className="text-red-500 text-sm mt-4 p-3 bg-red-900/20 border border-red-500 rounded-lg">
                                {typeof error === 'string' ? error : 'An error occurred'}
                            </div>
                        )}
                        {message && (
                            <div className="text-green-500 text-sm mt-4 p-3 bg-green-900/20 border border-green-500 rounded-lg">
                                {message}
                            </div>
                        )}

                        {/* Submit Button */}
                        <div className="flex justify-end">
                            <button
                                type="submit"
                                className="btn-primary"
                            >
                                Save Changes
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </MainLayout>
    );
}
