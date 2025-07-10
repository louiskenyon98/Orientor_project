// Updated Landing Page Flow: Clear structure of problem, solution, and feature purpose

'use client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';
import './landing-page.css';



export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Header */}
      <header className="w-full px-6 lg:px-12 py-6">
        <nav className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-2">
            <Image
              src="/Logo.png"
              alt="Navigo"
              width={32}
              height={32}
              className="object-contain"
            />
            <span className="text-xl font-semibold text-gray-900">Navigo</span>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</Link>
            <Link href="/pricing" className="text-gray-600 hover:text-gray-900 transition-colors">Pricing</Link>
            <Link href="/about" className="text-gray-600 hover:text-gray-900 transition-colors">About</Link>
          </div>
          <div className="flex items-center space-x-4">
            <Link href="/login" className="text-gray-600 hover:text-gray-900 transition-colors">Sign In</Link>
            <Link href="/register" className="bg-black text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition-colors">
              Get Started
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="px-6 lg:px-12 py-16 lg:py-24">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Your personal guide to discovering who you are—and who you could become
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Navigo helps you reflect, plan, and progress with purpose, backed by intelligent guidance and adaptive learning.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Link href="/register" className="bg-black text-white px-8 py-3 rounded-lg hover:bg-gray-800 transition-colors font-medium">
                Start Learning Today
              </Link>
              <Link href="/demo" className="text-gray-600 hover:text-gray-900 transition-colors px-8 py-3 font-medium">
                View Demo
              </Link>
            </div>
            
            {/* Simple illustration placeholder */}
            <div className="relative mx-auto max-w-2xl">
              <div className="aspect-video bg-gray-50 rounded-2xl border border-gray-200 flex items-center justify-center">
                <div className="text-center space-y-4">
                  <div className="text-6xl">🎯</div>
                  <p className="text-gray-500 font-medium">Interactive AI Career Guide</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      {/* Features Section */}
      <section className="px-6 lg:px-12 py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              How Navigo helps you learn
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our adaptive learning toolkit grows with you, helping you discover your path through reflection and personalized guidance.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-8 rounded-2xl border border-gray-200">
              <div className="text-4xl mb-4">🤔</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Self-Discovery Through Reflection</h3>
              <p className="text-gray-600">
                Engage with thoughtful questions and exercises that help you understand your strengths, interests, and values.
              </p>
            </div>
            
            {/* Feature 2 */}
            <div className="bg-white p-8 rounded-2xl border border-gray-200">
              <div className="text-4xl mb-4">🎨</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Personalized Learning Paths</h3>
              <p className="text-gray-600">
                Get recommendations tailored to your unique profile, goals, and learning style.
              </p>
            </div>
            
            {/* Feature 3 */}
            <div className="bg-white p-8 rounded-2xl border border-gray-200">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Track Your Growth</h3>
              <p className="text-gray-600">
                Visualize your progress and see how your skills and interests evolve over time.
              </p>
            </div>
          </div>
        </div>
      </section>
      {/* Interactive Demo Section */}
      <section className="px-6 lg:px-12 py-16">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Your AI Learning Companion
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Chat with Navigo to explore your interests, reflect on experiences, and get personalized guidance that adapts to your learning style.
            </p>
          </div>
          
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
              <div className="text-center space-y-6">
                <div className="text-6xl">🤖</div>
                <h3 className="text-2xl font-semibold text-gray-900">Interactive Chat Experience</h3>
                <p className="text-gray-600 max-w-lg mx-auto">
                  Discover your strengths and interests through conversational AI that learns about you as you explore.
                </p>
                <Link href="/chat" className="inline-block bg-black text-white px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors font-medium">
                  Try Demo Chat
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
      {/* Skill Development Section */}
      <section className="px-6 lg:px-12 py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Visualize Your Growth Path
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              See how your skills connect and discover new opportunities through our intelligent career mapping system.
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="aspect-square bg-white rounded-2xl border border-gray-200 flex items-center justify-center">
                <div className="text-center space-y-4">
                  <div className="text-6xl">🌳</div>
                  <p className="text-gray-500 font-medium">Interactive Skill Tree</p>
                </div>
              </div>
            </div>
            <div className="space-y-6">
              <h3 className="text-2xl font-bold text-gray-900">Track Your Development</h3>
              <p className="text-gray-600 text-lg">
                From foundational skills to advanced expertise, visualize your learning journey and discover new paths based on market trends and your interests.
              </p>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Personalized skill recommendations</span>
                </li>
                <li className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Market-driven career insights</span>
                </li>
                <li className="flex items-start space-x-3">
                  <div className="text-green-500 mt-1">✓</div>
                  <span className="text-gray-700">Progress tracking and milestones</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>


      {/* Assessment Section */}
      <section className="px-6 lg:px-12 py-16">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Understand Yourself Better
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Take scientifically-backed assessments to discover your personality, interests, and ideal learning approach.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-gray-200 text-center">
              <div className="text-3xl mb-4">🧠</div>
              <h3 className="font-semibold text-gray-900 mb-2">Personality Assessment</h3>
              <p className="text-gray-600 text-sm mb-4">Discover your core traits and working style</p>
              <Link href="/hexaco-test" className="text-sm text-blue-600 hover:text-blue-800 font-medium">Take Assessment</Link>
            </div>
            
            <div className="bg-white p-6 rounded-2xl border border-gray-200 text-center">
              <div className="text-3xl mb-4">🎨</div>
              <h3 className="font-semibold text-gray-900 mb-2">Interest Explorer</h3>
              <p className="text-gray-600 text-sm mb-4">Find careers that match your interests</p>
              <Link href="/holland-test" className="text-sm text-blue-600 hover:text-blue-800 font-medium">Explore Interests</Link>
            </div>
            
            <div className="bg-white p-6 rounded-2xl border border-gray-200 text-center">
              <div className="text-3xl mb-4">📝</div>
              <h3 className="font-semibold text-gray-900 mb-2">Reflection Journal</h3>
              <p className="text-gray-600 text-sm mb-4">Deep dive into your values and goals</p>
              <Link href="/self-reflection" className="text-sm text-blue-600 hover:text-blue-800 font-medium">Start Reflecting</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="px-6 lg:px-12 py-20 bg-black">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl lg:text-5xl font-bold text-white mb-6">
            Ready to discover your path?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of students who are already using Navigo to unlock their potential and build meaningful careers.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register" className="bg-white text-black px-8 py-4 rounded-lg hover:bg-gray-100 transition-colors font-semibold text-lg">
              Start Learning Today
            </Link>
            <Link href="/demo" className="border border-gray-600 text-white px-8 py-4 rounded-lg hover:border-gray-400 transition-colors font-medium text-lg">
              Try Demo First
            </Link>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="px-6 lg:px-12 py-12 bg-gray-50 border-t border-gray-200">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-6 md:space-y-0">
            <div className="flex items-center space-x-2">
              <Image
                src="/Logo.png"
                alt="Navigo"
                width={24}
                height={24}
                className="object-contain"
              />
              <span className="font-semibold text-gray-900">Navigo</span>
            </div>
            <div className="flex flex-wrap gap-8">
              <Link href="/privacy" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">Privacy</Link>
              <Link href="/terms" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">Terms</Link>
              <Link href="/support" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">Support</Link>
              <Link href="/about" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">About</Link>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-200 text-center">
            <p className="text-gray-500 text-sm">
              © 2025 Navigo. All rights reserved. Empowering students to discover their potential.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

