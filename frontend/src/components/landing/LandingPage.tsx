// Updated Landing Page Flow: Clear structure of problem, solution, and feature purpose

'use client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Player } from '@lottiefiles/react-lottie-player';
import { motion } from 'framer-motion';
import Link from 'next/link';
import SkillTreeFlow from '@/components/branches/career_growth';
import DemoChat from '@/components/chat/DemoChat';

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="section">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <h1 className="text-4xl md:text-6xl font-bold gradient-text">
              Welcome to Navigo
            </h1>
            <p className="text-xl text-neutral-500 leading-relaxed">
              Your personal guide to discovering who you are—and who you could become. Navigo helps you reflect, plan, and progress with purpose, backed by intelligent guidance and skill tracking.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/login" className="btn btn-primary">Log In</Link>
              <Link href="/register" className="btn btn-outline">Sign Up</Link>
            </div>
            <div className="absolute top-10 right-40 flex items-center justify-center p-4">
              <Image
                src="/navigo-hero.png"
                alt="Navigo splash"
                width={300}
                height={150}
                className="rounded-lg object-contain"
                priority
              />
            </div>
          </div>
        </div>
      </section>
      {/* Problem Section */}
      <section className="section mt-1">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 gradient-text">The Problem We're Tackling</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

          {/* Problem 1: Unclear Direction */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-red-100 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m0 14v1m8-8h1M4 12H3m15.36 6.36l.71.71M6.34 6.34l-.71-.71m12.02 0l.71-.71M6.34 17.66l-.71.71" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-red-600 mb-4">Unclear Direction</h3>
            <p className="text-neutral-500">
              Many students don’t know what they’re good at, what excites them, or where to even begin exploring. Traditional guidance is shallow and generic.
            </p>
          </div>

          {/* Problem 2: Fragmented and Passive Tools */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-yellow-100 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.97-4.03 9-9 9S3 16.97 3 12 7.03 3 12 3s9 4.03 9 9z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-yellow-600 mb-4">Fragmented and Passive Tools</h3>
            <p className="text-neutral-500">
              Advice is scattered and platforms like job boards or course lists don’t engage users in self-reflection or adaptive learning.
            </p>
          </div>

          {/* Problem 3: Fading Motivation */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-blue-100 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V4a2 2 0 10-4 0v1.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-blue-600 mb-4">Fading Motivation</h3>
            <p className="text-neutral-500">
              Without meaningful feedback or visible progress, learners lose confidence and abandon their efforts prematurely.
            </p>
          </div>

        </div>
      </section>

      {/* Features Section */}
      <section className="section mt-1">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 gradient-text">How Navigo Helps</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

          {/* Feature 1: Career Guidance */}
          <div className="card hover-lift border-l-4 border-primary-teal bg-primary-purple/10">
            <div className="mb-6 p-3 bg-primary-purple/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-primary-teal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-primary-teal mb-4">Skill-Based Career Mapping</h3>
            <p className="text-neutral-600">
              We go beyond job titles. Navigo builds a graph of your skills to suggest personalized next steps—based on what you know, what you’re building, and where you want to go.
            </p>
          </div>

          {/* Feature 2: Personal Growth */}
          <div className="card hover-lift border-l-4 border-accent-amber bg-accent-amber/10">
            <div className="mb-6 p-3 bg-accent-amber/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-accent-amber" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-accent-amber mb-4">Space: Your Personal Mission Hub</h3>
            <p className="text-neutral-600">
              Track your chosen career goals, compare your current skills with what’s needed, reflect on daily progress, and receive micro-recommendations on how to advance.
            </p>
          </div>

          {/* Feature 3: Future Path Prediction */}
          <div className="card hover-lift border-l-4 border-primary-purple bg-primary-teal/10">
            <div className="mb-6 p-3 bg-primary-teal/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-primary-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0v7" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-primary-purple mb-4">See Your Possible Futures</h3>
            <p className="text-neutral-600">
              Navigo predicts skill-based branches of what you could become. Think of it as a constellation of futures—mapped out based on your growth patterns and intentions.
            </p>
          </div>

        </div>
      </section>
      {/* Career Tree Visual */}
      <section className="section">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-3 gradient-text">Career Growth Tree</h2>
        <SkillTreeFlow />
        <div className="text-center text-neutral-600 max-w-xl mx-auto mb-6">
          <p>
            The tree is a visual metaphor and recommendation engine. It represents your evolving skillset and helps you see how different behaviors or experiences open new paths. Each branch is a future that grows from who you are now.
          </p>
        </div>
      </section>

      {/* Demo Chat Section */}
      <main className="min-h-screen bg-gradient-to-b from-gray-0 to-white">
        <div className="container mx-auto px-2 py-4">
          <h1 className="text-4xl font-bold text-center mb-4 text-gray-900">
            Talk to Navigo
          </h1>
          <p className="text-center text-neutral-600 max-w-xl mx-auto mb-6">
            The chat isn't just a bot—it's a reflection partner. It helps you dig deeper into your interests, reflect on experiences, and receive tailored guidance, in a calm and exploratory tone.
          </p>
          <div className="max-w-2xl mx-auto">
            <DemoChat />
          </div>
        </div>
      </main>


      {/* CTA Section */}
      <section className="section">
        <div className="bg-gradient-primary p-[1px] rounded-lg shadow-glow-purple">
          <div className="bg-neutral-800/90 backdrop-blur-md rounded-[calc(0.5rem-1px)] p-8 md:p-12">
            <div className="max-w-3xl mx-auto space-y-8">
              <h2 className="text-3xl md:text-4xl font-bold text-center text-neutral-50">
                Start Your Journey Today
              </h2>
              <p className="text-xl text-center text-neutral-500">
                Join Navigo and let your curiosity, discipline, and imagination build the future you're meant to explore.
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <Link href="/register" className="btn btn-primary">Create Account</Link>
                <Link href="/login" className="btn btn-outline">Log In</Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

