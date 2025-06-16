'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import MainLayout from '@/components/layout/MainLayout';
import { 
  GraduationCap, 
  Clock, 
  TrendingUp, 
  Search, 
  Filter, 
  BookOpen,
  MapPin,
  DollarSign,
  Users,
  Calendar,
  Star,
  ArrowRight,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

// Mock user data based on UI screenshot
const mockUserData = {
  name: "Alex",
  completedPrograms: 204,
  totalPrograms: 300,
  completionPercentage: 68,
  greeting: "It's a great day to explore your future! 🌟"
};

// Mock progress data similar to the screenshot
const mockProgressData = [
  {
    id: 1,
    subject: "Computer Science",
    icon: "💻",
    lessonNumber: "#13",
    progress: 65,
    color: "bg-teal-100",
    progressColor: "text-teal-600",
    borderColor: "border-teal-200"
  },
  {
    id: 2,
    subject: "Business Admin",
    icon: "📊",
    lessonNumber: "#79",
    progress: 80,
    color: "bg-purple-100",
    progressColor: "text-purple-600",
    borderColor: "border-purple-200"
  },
  {
    id: 3,
    subject: "Engineering",
    icon: "⚙️",
    lessonNumber: "#101",
    progress: 45,
    color: "bg-yellow-100",
    progressColor: "text-yellow-600",
    borderColor: "border-yellow-200"
  }
];

// Mock activity feed data
const mockActivityData = [
  {
    id: 1,
    user: "Sia Lubich",
    subject: "Computer Science, Topic 1",
    action: "Added new assignment",
    time: "Jan 2, 12:30",
    avatar: "👩‍💼"
  },
  {
    id: 2,
    user: "Christian Driss",
    subject: "Mathematics, Topic 2",
    action: "Deadline approaching",
    time: "Jan 2, 12:25",
    avatar: "👨‍🎓"
  },
  {
    id: 3,
    user: "Ann Golden",
    subject: "History, Topic 1,2",
    action: "New date of exam posted",
    time: "Jan 2, 12:04",
    avatar: "👩‍🏫"
  },
  {
    id: 4,
    user: "Victory Hurt",
    subject: "English, Topic 3",
    action: "Deadline approaching",
    time: "Jan 2, 12:01",
    avatar: "👨‍💻"
  }
];

// Mock programs data
const mockProgramsData = [
  {
    id: 1,
    title: "Introduction to Computer Science",
    instructor: "Sara Goldman",
    image: "🧬",
    section: "Section 9A • 9B",
    students: [
      { avatar: "👨‍💼", name: "John" },
      { avatar: "👩‍💻", name: "Emma" },
      { avatar: "👨‍🎓", name: "Mike" },
      { avatar: "👩‍🔬", name: "Sarah" }
    ]
  },
  {
    id: 2,
    title: "Master of Business Administration",
    instructor: "Jonathan Weston",
    image: "🗂️",
    section: "Section 10A",
    students: [
      { avatar: "👨‍💼", name: "David" },
      { avatar: "👩‍💼", name: "Lisa" },
      { avatar: "👨‍🔬", name: "Alex" },
      { avatar: "👩‍🎯", name: "Maria" }
    ]
  },
  {
    id: 3,
    title: "Software Engineering Fundamentals",
    instructor: "Jonathan Weston",
    image: "🧮",
    section: "Section 9A • 9B",
    students: [
      { avatar: "👨‍💻", name: "Tom" },
      { avatar: "👩‍💻", name: "Anna" },
      { avatar: "👨‍🎓", name: "Chris" },
      { avatar: "👩‍🔬", name: "Helen" }
    ]
  }
];

// Mock upcoming schedule
const mockUpcomingSchedule = [
  {
    time: "09:00",
    title: "Course Name: Lesson",
    subtitle: "Jan 2, 12:31pm",
    type: "lesson",
    color: "bg-teal-500"
  },
  {
    time: "10:00",
    title: "Course Name: Test",
    subtitle: "Jan 2, 12:31pm",
    type: "test",
    color: "bg-pink-500"
  },
  {
    time: "11:00",
    title: "Extracurricular activities",
    subtitle: "Jan 2, 12:31pm",
    type: "activity",
    color: "bg-yellow-500"
  }
];

const ProgressCircle = ({ percentage, size = 60 }: { percentage: number; size?: number }) => {
  const circumference = 2 * Math.PI * (size / 2 - 4);
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={size / 2 - 4}
          stroke="#e5e7eb"
          strokeWidth="8"
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={size / 2 - 4}
          stroke="currentColor"
          strokeWidth="8"
          fill="transparent"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          className="text-current transition-all duration-300"
        />
      </svg>
    </div>
  );
};

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date(2022, 5, 11)); // June 2022
  
  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  
  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];
  
  const dayNames = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
  
  const today = 11; // Highlighted day from the screenshot
  
  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1);
      } else {
        newDate.setMonth(prev.getMonth() + 1);
      }
      return newDate;
    });
  };
  
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-gray-900">
          {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
        </h3>
        <div className="flex gap-1">
          <button 
            onClick={() => navigateMonth('prev')}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          </button>
          <button 
            onClick={() => navigateMonth('next')}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <ChevronRight className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-7 gap-1 mb-2">
        {dayNames.map(day => (
          <div key={day} className="text-xs font-medium text-gray-500 text-center py-1">
            {day}
          </div>
        ))}
      </div>
      
      <div className="grid grid-cols-7 gap-1">
        {/* Empty cells for days before month starts */}
        {Array.from({ length: firstDayOfMonth }, (_, i) => (
          <div key={`empty-${i}`} className="h-8"></div>
        ))}
        
        {/* Days of the month */}
        {Array.from({ length: daysInMonth }, (_, i) => {
          const day = i + 1;
          const isToday = day === today;
          
          return (
            <div
              key={day}
              className={`h-8 flex items-center justify-center text-sm rounded cursor-pointer transition-colors ${
                isToday 
                  ? 'bg-purple-500 text-white font-medium' 
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              {day}
            </div>
          );
        })}
      </div>
      
      {/* Legend */}
      <div className="mt-4 space-y-2">
        <div className="flex items-center gap-2 text-xs">
          <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
          <span className="text-gray-600">Extracurricular</span>
          <div className="w-2 h-2 bg-pink-500 rounded-full ml-4"></div>
          <span className="text-gray-600">Test</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <div className="w-2 h-2 bg-teal-500 rounded-full"></div>
          <span className="text-gray-600">Online lesson</span>
        </div>
      </div>
    </div>
  );
};

// Main Education Page Component
export default function EducationPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [courseSearchQuery, setCourseSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  return (
    <MainLayout>
      <div className="min-h-screen bg-gray-50">
        {/* Sidebar Navigation - Left Side */}
        <div className="fixed left-0 top-0 h-full w-16 bg-white border-r border-gray-200 flex flex-col items-center py-6 space-y-6 z-10">
          <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          
          <div className="flex flex-col space-y-4">
            <div className="w-8 h-8 bg-purple-100 rounded flex items-center justify-center">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            </div>
            <div className="w-8 h-8 hover:bg-gray-100 rounded flex items-center justify-center cursor-pointer">
              <BookOpen className="w-4 h-4 text-gray-600" />
            </div>
            <div className="w-8 h-8 hover:bg-gray-100 rounded flex items-center justify-center cursor-pointer">
              <Users className="w-4 h-4 text-gray-600" />
            </div>
            <div className="w-8 h-8 hover:bg-gray-100 rounded flex items-center justify-center cursor-pointer">
              <TrendingUp className="w-4 h-4 text-gray-600" />
            </div>
            <div className="w-8 h-8 hover:bg-gray-100 rounded flex items-center justify-center cursor-pointer">
              <Calendar className="w-4 h-4 text-gray-600" />
            </div>
          </div>
          
          <div className="mt-auto">
            <div className="w-8 h-8 bg-gray-700 rounded-full overflow-hidden">
              <div className="w-full h-full bg-gradient-to-r from-purple-400 to-pink-400"></div>
            </div>
          </div>
        </div>
        
        {/* Main Content */}
        <div className="ml-16 p-6">
          <div className="max-w-7xl mx-auto">
            {/* Header Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <div className="flex items-center justify-between mb-2">
                <h1 className="text-3xl font-bold text-gray-900">
                  Hey {mockUserData.name},
                </h1>
                <div className="flex items-center space-x-3">
                  <div className="bg-purple-100 text-purple-600 px-3 py-1 rounded-full text-sm font-medium flex items-center">
                    <Star className="w-4 h-4 mr-1" />
                    15
                  </div>
                  <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
                  <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
                </div>
              </div>
              <p className="text-gray-600">{mockUserData.greeting}</p>
            </motion.div>
            
            {/* Main Grid Layout */}
            <div className="grid grid-cols-12 gap-6">
              {/* Left Column - Progress & Activity */}
              <div className="col-span-8 space-y-6">
                {/* My Progress Section */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="bg-white rounded-xl border border-gray-200 p-6"
                >
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-purple-100 rounded flex items-center justify-center mr-3">
                        <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      </div>
                      <h2 className="text-xl font-bold text-gray-900">My Progress</h2>
                      <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-1 rounded text-sm font-medium">
                        {mockProgressData.length}
                      </span>
                    </div>
                    <div className="flex space-x-1">
                      <button className="p-2 hover:bg-gray-100 rounded">
                        <ChevronLeft className="w-4 h-4 text-gray-600" />
                      </button>
                      <button className="p-2 hover:bg-gray-100 rounded">
                        <ChevronRight className="w-4 h-4 text-gray-600" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Progress Stats */}
                  <div className="grid grid-cols-3 gap-6 mb-6">
                    <div>
                      <div className="text-3xl font-bold text-gray-900 mb-1">
                        {mockUserData.completedPrograms}/{mockUserData.totalPrograms}
                      </div>
                      <div className="text-sm text-gray-500">Completed lessons</div>
                      
                      <div className="mt-3">
                        <div className="text-2xl font-bold text-gray-900 mb-1">
                          {mockUserData.completionPercentage}
                        </div>
                        <div className="text-sm text-gray-500 flex items-center">
                          % Completed
                          <span className="ml-2">🤓</span>
                        </div>
                        
                        {/* Progress Bar */}
                        <div className="mt-2 w-24 h-2 bg-gray-200 rounded-full">
                          <div 
                            className="h-full bg-yellow-400 rounded-full transition-all duration-300"
                            style={{ width: `${mockUserData.completionPercentage}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Subject Progress Cards */}
                    {mockProgressData.map((subject, index) => (
                      <motion.div
                        key={subject.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 + index * 0.1 }}
                        className={`${subject.color} ${subject.borderColor} border rounded-xl p-4 text-center`}
                      >
                        <div className="text-2xl mb-2">{subject.icon}</div>
                        <div className="text-sm font-medium text-gray-600 mb-1">
                          {subject.lessonNumber}
                        </div>
                        <div className="font-bold text-gray-900 mb-3">
                          {subject.subject}
                        </div>
                        
                        <div className={`flex justify-center ${subject.progressColor}`}>
                          <ProgressCircle percentage={subject.progress} size={50} />
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
                
                {/* Activity and Courses Row */}
                <div className="grid grid-cols-2 gap-6">
                  {/* Activity Section */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white rounded-xl border border-gray-200 p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-gray-900 flex items-center">
                        Activity
                        <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-1 rounded text-sm font-medium">
                          {mockActivityData.length}
                        </span>
                      </h3>
                      <Filter className="w-4 h-4 text-gray-400" />
                    </div>
                    
                    {/* Search Bar */}
                    <div className="mb-4">
                      <div className="relative">
                        <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                        <input
                          type="text"
                          placeholder="Find update"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    
                    {/* Activity List */}
                    <div className="space-y-3">
                      {mockActivityData.map((activity, index) => (
                        <motion.div
                          key={activity.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.4 + index * 0.1 }}
                          className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer"
                        >
                          <div className="flex items-center">
                            <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mr-3 text-sm">
                              {activity.avatar}
                            </div>
                            <div>
                              <div className="font-medium text-gray-900 text-sm">
                                {activity.user}
                              </div>
                              <div className="text-xs text-gray-500">
                                {activity.subject}
                              </div>
                              <div className="text-xs text-gray-400">
                                {activity.action}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center">
                            <span className="text-xs text-gray-400 mr-2">
                              {activity.time}
                            </span>
                            <ArrowRight className="w-3 h-3 text-gray-400" />
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                  
                  {/* Courses Section */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="bg-white rounded-xl border border-gray-200 p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-gray-900 flex items-center">
                        Courses
                        <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-1 rounded text-sm font-medium">
                          {mockProgramsData.length}
                        </span>
                      </h3>
                      <Filter className="w-4 h-4 text-gray-400" />
                    </div>
                    
                    {/* Search Bar */}
                    <div className="mb-4">
                      <div className="relative">
                        <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                        <input
                          type="text"
                          placeholder="Find course"
                          value={courseSearchQuery}
                          onChange={(e) => setCourseSearchQuery(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    
                    {/* Courses List */}
                    <div className="space-y-4">
                      {mockProgramsData.map((program, index) => (
                        <motion.div
                          key={program.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.5 + index * 0.1 }}
                          className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer"
                        >
                          <div className="flex items-center">
                            <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-pink-400 rounded-lg flex items-center justify-center mr-3 text-lg">
                              {program.image}
                            </div>
                            <div>
                              <div className="font-medium text-gray-900 text-sm">
                                {program.title}
                              </div>
                              <div className="text-xs text-gray-500">
                                by {program.instructor}
                              </div>
                              <div className="text-xs text-gray-400">
                                {program.section}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center">
                            <div className="flex -space-x-1 mr-2">
                              {program.students.map((student, idx) => (
                                <div
                                  key={idx}
                                  className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center text-xs border border-white"
                                >
                                  {student.avatar}
                                </div>
                              ))}
                              <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-xs border border-white">
                                +
                              </div>
                            </div>
                            <ArrowRight className="w-3 h-3 text-gray-400" />
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                </div>
              </div>
              
              {/* Right Column - Calendar & Schedule */}
              <div className="col-span-4 space-y-6">
                {/* Scheduled Section */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="bg-white rounded-xl border border-gray-200 p-6"
                >
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Scheduled</h3>
                  <Calendar />
                </motion.div>
                
                {/* Upcoming Section */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="bg-white rounded-xl border border-gray-200 p-6"
                >
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Upcoming</h3>
                  
                  <div className="space-y-4">
                    {mockUpcomingSchedule.map((item, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 + index * 0.1 }}
                        className="flex items-center"
                      >
                        <div className="text-sm text-gray-500 w-12">
                          {item.time}
                        </div>
                        <div className="flex items-center ml-4">
                          <div className={`w-3 h-3 ${item.color} rounded-full mr-3`}></div>
                          <div>
                            <div className="font-medium text-gray-900 text-sm">
                              {item.title}
                            </div>
                            <div className="text-xs text-gray-500">
                              {item.subtitle}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}