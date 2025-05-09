// src/app/profile/page.tsx
import { useState } from 'react';
import axios from 'axios';
// import { AxiosError } from 'axios';

const ProfilePage = () => {
    const [activeTab, setActiveTab] = useState('basic');
    const [formData, setFormData] = useState({
        // Basic Info
        email: '',
        password: '',
        name: '',
        age: '',
        sex: '',
        country: '',
        state_province: '',
        
        // Academic Info
        major: '',
        year: '',
        gpa: '',
        learning_style: '',
        
        // Personal Info
        hobbies: '',
        unique_quality: '',
        story: '',
        favorite_movie: '',
        favorite_book: '',
        favorite_celebrities: '',
        
        // Career Info
        job_title: '',
        industry: '',
        years_experience: '',
        education_level: '',
        career_goals: '',
        skills: '',
        interests: ''
    });
    const [message, setMessage] = useState('');

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('access_token');
            await axios.put( 
                'http://localhost:8000/users/update',
                formData,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                }
            );
            setMessage('Profile updated successfully!');
        } catch (error) {
            const axiosError = error as { response?: { data?: { detail?: string } } };
            setMessage('Error updating profile: ' + (axiosError.response?.data?.detail || 'Unknown error'));
        }
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'basic':
    return (
                    <div className="space-y-4">
                <div className="space-y-2">
                    <label className="block text-sm font-medium">Email:</label>
                    <input
                        type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleInputChange}
                        className="w-full p-2 border rounded-md"
                    />
                </div>
                <div className="space-y-2">
                    <label className="block text-sm font-medium">New Password (optional):</label>
                    <input
                        type="password"
                                name="password"
                                value={formData.password}
                                onChange={handleInputChange}
                        className="w-full p-2 border rounded-md"
                        placeholder="Leave blank to keep current password"
                    />
                </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Name:</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">Age:</label>
                                <input
                                    type="number"
                                    name="age"
                                    value={formData.age}
                                    onChange={handleInputChange}
                                    className="w-full p-2 border rounded-md"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">Sex:</label>
                                <select
                                    name="sex"
                                    value={formData.sex}
                                    onChange={handleInputChange}
                                    className="w-full p-2 border rounded-md"
                                >
                                    <option value="">Select...</option>
                                    <option value="Male">Male</option>
                                    <option value="Female">Female</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">Country:</label>
                                <input
                                    type="text"
                                    name="country"
                                    value={formData.country}
                                    onChange={handleInputChange}
                                    className="w-full p-2 border rounded-md"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">State/Province:</label>
                                <input
                                    type="text"
                                    name="state_province"
                                    value={formData.state_province}
                                    onChange={handleInputChange}
                                    className="w-full p-2 border rounded-md"
                                />
                            </div>
                        </div>
                    </div>
                );
            case 'academic':
                return (
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Major:</label>
                            <input
                                type="text"
                                name="major"
                                value={formData.major}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">Year:</label>
                                <input
                                    type="number"
                                    name="year"
                                    value={formData.year}
                                    onChange={handleInputChange}
                                    className="w-full p-2 border rounded-md"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">GPA:</label>
                                <input
                                    type="number"
                                    name="gpa"
                                    value={formData.gpa}
                                    onChange={handleInputChange}
                                    step="0.01"
                                    min="0"
                                    max="4.0"
                                    className="w-full p-2 border rounded-md"
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Learning Style:</label>
                            <select
                                name="learning_style"
                                value={formData.learning_style}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                            >
                                <option value="">Select...</option>
                                <option value="Visual">Visual</option>
                                <option value="Auditory">Auditory</option>
                                <option value="Reading/Writing">Reading/Writing</option>
                                <option value="Kinesthetic">Kinesthetic</option>
                            </select>
                        </div>
                    </div>
                );
            case 'personal':
                return (
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Hobbies:</label>
                            <textarea
                                name="hobbies"
                                value={formData.hobbies}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                                rows={3}
                                placeholder="Enter your hobbies, separated by commas"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Unique Quality:</label>
                            <textarea
                                name="unique_quality"
                                value={formData.unique_quality}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                                rows={2}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Your Story:</label>
                            <textarea
                                name="story"
                                value={formData.story}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                                rows={4}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Favorite Movie:</label>
                            <input
                                type="text"
                                name="favorite_movie"
                                value={formData.favorite_movie}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Favorite Book:</label>
                            <input
                                type="text"
                                name="favorite_book"
                                value={formData.favorite_book}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Favorite Celebrities:</label>
                            <input
                                type="text"
                                name="favorite_celebrities"
                                value={formData.favorite_celebrities}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                                placeholder="Enter names, separated by commas"
                            />
                        </div>
                    </div>
                );
            case 'career':
                return (
                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">Job Title:</label>
                                <input
                                    type="text"
                                    name="job_title"
                                    value={formData.job_title}
                                    onChange={handleInputChange}
                                    className="w-full p-2 border rounded-md"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">Industry:</label>
                                <input
                                    type="text"
                                    name="industry"
                                    value={formData.industry}
                                    onChange={handleInputChange}
                                    className="w-full p-2 border rounded-md"
                                />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">Years Experience:</label>
                                <input
                                    type="number"
                                    name="years_experience"
                                    value={formData.years_experience}
                                    onChange={handleInputChange}
                                    className="w-full p-2 border rounded-md"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="block text-sm font-medium">Education Level:</label>
                                <select
                                    name="education_level"
                                    value={formData.education_level}
                                    onChange={handleInputChange}
                                    className="w-full p-2 border rounded-md"
                                >
                                    <option value="">Select...</option>
                                    <option value="High School">High School</option>
                                    <option value="Associate's Degree">Associate's Degree</option>
                                    <option value="Bachelor's Degree">Bachelor's Degree</option>
                                    <option value="Master's Degree">Master's Degree</option>
                                    <option value="Doctorate">Doctorate</option>
                                </select>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Career Goals:</label>
                            <textarea
                                name="career_goals"
                                value={formData.career_goals}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                                rows={3}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Skills:</label>
                            <textarea
                                name="skills"
                                value={formData.skills}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                                rows={3}
                                placeholder="Enter your skills, separated by commas"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="block text-sm font-medium">Interests:</label>
                            <textarea
                                name="interests"
                                value={formData.interests}
                                onChange={handleInputChange}
                                className="w-full p-2 border rounded-md"
                                rows={3}
                                placeholder="Enter your interests, separated by commas"
                            />
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="container mx-auto p-4 max-w-4xl">
            <h1 className="text-2xl font-bold mb-6">User Profile</h1>
            
            {/* Tabs */}
            <div className="flex space-x-4 mb-6 border-b">
                <button
                    onClick={() => setActiveTab('basic')}
                    className={`py-2 px-4 ${
                        activeTab === 'basic'
                            ? 'border-b-2 border-blue-500 text-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                    Basic Info
                </button>
                <button
                    onClick={() => setActiveTab('academic')}
                    className={`py-2 px-4 ${
                        activeTab === 'academic'
                            ? 'border-b-2 border-blue-500 text-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                    Academic Info
                </button>
                <button
                    onClick={() => setActiveTab('personal')}
                    className={`py-2 px-4 ${
                        activeTab === 'personal'
                            ? 'border-b-2 border-blue-500 text-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                    Personal Info
                </button>
                <button 
                    onClick={() => setActiveTab('career')}
                    className={`py-2 px-4 ${
                        activeTab === 'career'
                            ? 'border-b-2 border-blue-500 text-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                    Career Info
                </button>
            </div>

            <form onSubmit={handleUpdate} className="space-y-6">
                {renderTabContent()}
                
                <div className="flex justify-end">
                    <button 
                        type="submit" 
                        className="bg-blue-500 text-white py-2 px-6 rounded-md hover:bg-blue-600 transition-colors"
                    >
                        Save Changes
                    </button>
                </div>
            </form>

            {message && (
                <p className={`mt-4 p-3 rounded ${
                    message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                }`}>
                    {message}
                </p>
            )}
        </div>
    );
};

export default ProfilePage;