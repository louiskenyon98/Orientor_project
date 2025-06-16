'use client';

import React from 'react';
import Link from 'next/link';
import { BookOpen, Clock, Users } from 'lucide-react';

interface Course {
  id: string;
  name: string;
  instructor: string;
  time: string;
  color: string;
  icon: string;
  progress?: number;
}

interface ClassesCardProps {
  style?: React.CSSProperties;
  className?: string;
}

const ClassesCard: React.FC<ClassesCardProps> = ({ style, className = '' }) => {
  // Mock course data - showing only 2 featured courses
  const courses: Course[] = [
    {
      id: '1',
      name: 'Data Science Fundamentals',
      instructor: 'Dr. Sarah Chen',
      time: '10:00 AM',
      color: 'bg-gradient-to-br from-purple-500 to-purple-600',
      icon: '📊',
      progress: 85
    },
    {
      id: '2',
      name: 'Machine Learning',
      instructor: 'Prof. Alex Kumar',
      time: '2:00 PM',
      color: 'bg-gradient-to-br from-teal-500 to-teal-600',
      icon: '🤖',
      progress: 72
    }
  ];

  return (
    <div className={`bg-white rounded-3xl p-3 shadow-lg border border-gray-100 ${className}`} style={style}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
            <BookOpen className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-900">My Classes</h3>
            <p className="text-xs text-gray-500">Today</p>
          </div>
        </div>
      </div>

      {/* Courses List */}
      <div className="space-y-2">
        {courses.map((course, index) => (
          <div key={course.id} className="group hover:bg-gray-50 rounded-xl p-2 transition-all duration-200 cursor-pointer">
            <div className="flex items-center gap-2">
              {/* Course Icon */}
              <div className={`w-8 h-8 ${course.color} rounded-lg flex items-center justify-center text-white shadow-sm flex-shrink-0`}>
                <span className="text-sm">{course.icon}</span>
              </div>
              
              {/* Course Info */}
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-sm text-gray-900 truncate mb-1">
                  {course.name}
                </h4>
                <div className="flex items-center gap-1 mb-1">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <span className="text-xs text-gray-600">{course.time}</span>
                </div>
                
                {/* Compact Progress */}
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-1">
                    <div 
                      className={`h-1 rounded-full ${
                        course.color.replace('bg-gradient-to-br', 'bg-gradient-to-r')
                      }`}
                      style={{ width: `${course.progress}%` }}
                    ></div>
                  </div>
                  <span className="text-xs font-medium text-gray-700">{course.progress}%</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-3 pt-2 border-t border-gray-100">
        <Link 
          href="/classes"
          className="w-full text-center text-xs text-purple-600 hover:text-purple-700 font-medium transition-colors flex items-center justify-center gap-1 py-2 hover:bg-purple-50 rounded-lg"
        >
          <span>View All Classes</span>
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
          </svg>
        </Link>
      </div>
    </div>
  );
};

export default ClassesCard;