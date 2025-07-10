// Updated Landing Page Flow: Clear structure of problem, solution, and feature purpose

'use client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';
import './landing-page.css';



export default function LandingPage() {
  const router = useRouter();
  const [isVisible, setIsVisible] = useState<Record<string, boolean>>({});
  const observerRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const elementId = entry.target.id;
            setIsVisible(prev => ({
              ...prev,
              [elementId]: true
            }));
            // Add visible class for CSS animations
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1, rootMargin: '50px' }
    );

    // Observe sections with slight delay to ensure DOM is ready
    setTimeout(() => {
      const sections = document.querySelectorAll('.animate-on-scroll');
      sections.forEach(section => {
        if (section) {
          observer.observe(section);
        }
      });
    }, 100);

    return () => observer.disconnect();
  }, []);

  return (
    <div className="min-h-screen bg-white">

      {/* Blank Paper Section - "Everything Yet to Be Written" */}
      <section className="relative min-h-screen flex items-center justify-center px-6 lg:px-12 py-20 overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 opacity-30">
          <div className="floating-dots"></div>
        </div>
        
        {/* Large Paper Sheet */}
        <div className="paper-container relative">
          <div className="paper-sheet animate-on-scroll" id="paper-sheet">
            {/* Paper lines */}
            <div className="paper-lines"></div>
            
            {/* Content on the paper */}
            <div className={`paper-content ${isVisible['paper-sheet'] ? 'fade-in-up' : ''}`}>
              <div className="text-center space-y-8">
                <div className="space-y-4">
                  <h1 className="handwritten-title text-4xl lg:text-6xl font-bold text-gray-800 mb-6">
                    Your story starts here
                  </h1>
                  <div className="ink-pen-line"></div>
                </div>
                
                <p className="handwritten-text text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
                  Every career journey begins with a blank page. Let's discover what you'll write on yours.
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center mt-12">
                  <Link href="/register" className="ink-button bg-black text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 hover:bg-gray-800 hover:scale-105 hover:shadow-lg">
                    Begin Your Story
                  </Link>
                  <Link href="/demo" className="text-gray-600 hover:text-gray-900 transition-colors px-8 py-4 font-medium text-lg border border-gray-300 rounded-lg hover:border-gray-400 hover:shadow-md">
                    Explore First
                  </Link>
                </div>
              </div>
            </div>
            
            {/* Floating writing elements */}
            <div className="writing-elements">
              <div className="pencil floating"></div>
              <div className="eraser floating-slow"></div>
              <div className="pen floating-reverse"></div>
            </div>
          </div>
        </div>
      </section>
      {/* Features Section */}
      <section className="px-6 lg:px-12 py-20 bg-gradient-to-b from-white to-gray-50 animate-on-scroll" id="features-section">
        <div className="max-w-7xl mx-auto">
          <div className={`text-center mb-16 transition-all duration-1000 delay-300 ${isVisible['features-section'] ? 'fade-in-up' : 'opacity-0 translate-y-12'}`}>
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              How your story unfolds
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Every great story has chapters. Here's how we help you write yours, one discovery at a time.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className={`feature-card bg-white p-8 rounded-2xl border border-gray-200 transition-all duration-700 delay-500 ${isVisible['features-section'] ? 'fade-in-up' : 'opacity-0 translate-y-8'}`}>
              <div className="feature-icon text-4xl mb-4">🤔</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Chapter 1: Self-Discovery</h3>
              <p className="text-gray-600">
                Start with deep reflection. Understand your strengths, values, and what truly motivates you.
              </p>
              <div className="progress-dots mt-4">
                <span className="dot active"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
            
            {/* Feature 2 */}
            <div className={`feature-card bg-white p-8 rounded-2xl border border-gray-200 transition-all duration-700 delay-700 ${isVisible['features-section'] ? 'fade-in-up' : 'opacity-0 translate-y-8'}`}>
              <div className="feature-icon text-4xl mb-4">🎨</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Chapter 2: Path Creation</h3>
              <p className="text-gray-600">
                Build your unique journey with personalized recommendations that adapt to your evolving interests.
              </p>
              <div className="progress-dots mt-4">
                <span className="dot active"></span>
                <span className="dot active"></span>
                <span className="dot"></span>
              </div>
            </div>
            
            {/* Feature 3 */}
            <div className={`feature-card bg-white p-8 rounded-2xl border border-gray-200 transition-all duration-700 delay-900 ${isVisible['features-section'] ? 'fade-in-up' : 'opacity-0 translate-y-8'}`}>
              <div className="feature-icon text-4xl mb-4">📈</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Chapter 3: Growth & Evolution</h3>
              <p className="text-gray-600">
                Watch your story unfold as you track progress, celebrate milestones, and write new chapters.
              </p>
              <div className="progress-dots mt-4">
                <span className="dot active"></span>
                <span className="dot active"></span>
                <span className="dot active"></span>
              </div>
            </div>
          </div>
        </div>
      </section>
      {/* Interactive Demo Section */}
      <section className="px-6 lg:px-12 py-20 animate-on-scroll" id="demo-section">
        <div className="max-w-7xl mx-auto">
          <div className={`text-center mb-12 transition-all duration-1000 delay-200 ${isVisible['demo-section'] ? 'fade-in-up' : 'opacity-0 translate-y-12'}`}>
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Meet your writing companion
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Like having a thoughtful friend who asks the right questions, Navigo helps you discover what you want to write on your career page.
            </p>
          </div>
          
          <div className="max-w-4xl mx-auto">
            <div className={`chat-container bg-white rounded-2xl border border-gray-200 p-8 shadow-lg transition-all duration-1000 delay-400 ${isVisible['demo-section'] ? 'fade-in-scale' : 'opacity-0 scale-95'}`}>
              <div className="text-center space-y-6">
                <div className="chat-avatar text-6xl animate-bounce-slow">🤖</div>
                <h3 className="text-2xl font-semibold text-gray-900">Start a conversation</h3>
                <p className="text-gray-600 max-w-lg mx-auto">
                  "What excites you most about your future?" - Begin with questions that matter.
                </p>
                <div className="chat-bubbles space-y-3 max-w-sm mx-auto">
                  <div className="chat-bubble left animate-slide-in-left delay-1000">
                    <p className="text-sm">What energizes you?</p>
                  </div>
                  <div className="chat-bubble right animate-slide-in-right delay-1200">
                    <p className="text-sm">I love solving problems...</p>
                  </div>
                </div>
                <Link href="/chat" className="inline-block bg-black text-white px-8 py-4 rounded-lg hover:bg-gray-800 transition-all duration-300 font-semibold hover:scale-105 hover:shadow-lg">
                  Start Your Conversation
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
      <section className="px-6 lg:px-12 py-20 bg-gray-50 animate-on-scroll" id="assessment-section">
        <div className="max-w-7xl mx-auto">
          <div className={`text-center mb-12 transition-all duration-1000 delay-200 ${isVisible['assessment-section'] ? 'fade-in-up' : 'opacity-0 translate-y-12'}`}>
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Tools to understand your story
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Like a good editor, these tools help you understand your unique voice, style, and what makes your story worth telling.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className={`assessment-card bg-white p-8 rounded-2xl border border-gray-200 text-center transition-all duration-700 delay-400 hover:shadow-lg hover:scale-105 ${isVisible['assessment-section'] ? 'fade-in-up' : 'opacity-0 translate-y-8'}`}>
              <div className="assessment-icon text-4xl mb-6 animate-pulse-slow">🧠</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Your Character Profile</h3>
              <p className="text-gray-600 mb-6">Discover your core traits and what makes you uniquely you</p>
              <Link href="/hexaco-test" className="assessment-btn inline-block bg-blue-50 text-blue-700 px-6 py-3 rounded-lg hover:bg-blue-100 transition-all font-medium">Discover Your Profile</Link>
            </div>
            
            <div className={`assessment-card bg-white p-8 rounded-2xl border border-gray-200 text-center transition-all duration-700 delay-600 hover:shadow-lg hover:scale-105 ${isVisible['assessment-section'] ? 'fade-in-up' : 'opacity-0 translate-y-8'}`}>
              <div className="assessment-icon text-4xl mb-6 animate-pulse-slow">🎨</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Your Passion Compass</h3>
              <p className="text-gray-600 mb-6">Find what genuinely excites and motivates you</p>
              <Link href="/holland-test" className="assessment-btn inline-block bg-green-50 text-green-700 px-6 py-3 rounded-lg hover:bg-green-100 transition-all font-medium">Find Your Passions</Link>
            </div>
            
            <div className={`assessment-card bg-white p-8 rounded-2xl border border-gray-200 text-center transition-all duration-700 delay-800 hover:shadow-lg hover:scale-105 ${isVisible['assessment-section'] ? 'fade-in-up' : 'opacity-0 translate-y-8'}`}>
              <div className="assessment-icon text-4xl mb-6 animate-pulse-slow">📝</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Your Reflection Space</h3>
              <p className="text-gray-600 mb-6">A quiet place to think deeply about your aspirations</p>
              <Link href="/self-reflection" className="assessment-btn inline-block bg-purple-50 text-purple-700 px-6 py-3 rounded-lg hover:bg-purple-100 transition-all font-medium">Start Reflecting</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="px-6 lg:px-12 py-24 bg-gradient-to-br from-gray-900 via-black to-gray-800 animate-on-scroll relative overflow-hidden" id="cta-section">
        {/* Animated background stars */}
        <div className="stars-container absolute inset-0">
          <div className="star star-1"></div>
          <div className="star star-2"></div>
          <div className="star star-3"></div>
          <div className="star star-4"></div>
          <div className="star star-5"></div>
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className={`transition-all duration-1000 delay-200 ${isVisible['cta-section'] ? 'fade-in-up' : 'opacity-0 translate-y-12'}`}>
            <h2 className="text-3xl lg:text-5xl font-bold text-white mb-6 leading-tight">
              Your story is waiting
            </h2>
            <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto leading-relaxed">
              The blank page isn't empty—it's full of possibilities. Let's start writing your next chapter together.
            </p>
          </div>
          
          <div className={`flex flex-col sm:flex-row gap-6 justify-center transition-all duration-1000 delay-500 ${isVisible['cta-section'] ? 'fade-in-up' : 'opacity-0 translate-y-8'}`}>
            <Link href="/register" className="cta-primary bg-white text-black px-10 py-4 rounded-lg hover:bg-gray-100 transition-all duration-300 font-bold text-lg hover:scale-105 hover:shadow-2xl">
              Begin Writing Today
            </Link>
            <Link href="/demo" className="cta-secondary border-2 border-gray-400 text-white px-10 py-4 rounded-lg hover:border-white hover:bg-white hover:text-black transition-all duration-300 font-medium text-lg hover:scale-105">
              Preview the Journey
            </Link>
          </div>
          
          {/* Floating elements */}
          <div className={`mt-16 transition-all duration-1500 delay-1000 ${isVisible['cta-section'] ? 'fade-in' : 'opacity-0'}`}>
            <p className="text-sm text-gray-400">
              Join 10,000+ students already writing their stories
            </p>
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

