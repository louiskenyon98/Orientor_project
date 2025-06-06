// Updated Landing Page Flow: Clear structure of problem, solution, and feature purpose

'use client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Player } from '@lottiefiles/react-lottie-player';
import { motion } from 'framer-motion';
import Link from 'next/link';
import SkillTreeFlow from '@/components/branches/career_growth';
import CareerTechTree from '@/components/branches/Career_evolution';
import DemoChat from '@/components/chat/DemoChat';
import JobSwipeCard from '@/components/chat/swipe_recommendation';
import SkillSpiderChart from './SkillSpiderChart';
import { useState } from 'react';
import './landing-page.css';

// Données fictives pour le constructeur de CV
const resumeTemplates = [
  { id: 1, name: "Professionnel", color: "#2c3e50" },
  { id: 2, name: "Créatif", color: "#8e44ad" },
  { id: 3, name: "Minimaliste", color: "#7f8c8d" },
];


export default function LandingPage() {
  const router = useRouter();
  const [selectedTest, setSelectedTest] = useState<string | null>(null);

  const handleTestSelect = (testId: string) => {
    setSelectedTest(testId);
  };

  return (
    <div className="landing-container">
      {/* Header avec Logo */}
      <header className="landing-header">
        <h1 className="text-4xl md:text-6xl font-bold gradient-text">
          Welcome to Navigo
        </h1>
        <div className="light-button">
          <button className="bt">
            <div className="light-holder">
              <div className="dot"></div>
              <div className="light"></div>
            </div>
            <div className="button-holder">
              <Image
                src="/Logo.png"
                alt="Navigo Logo"
                width={80}
                height={80}
                className="object-contain"
              />
            </div>
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="section">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <p className="text-xl text-neutral-500 leading-relaxed">
              Your personal guide to discovering who you are—and who you could become. Navigo helps you reflect, plan, and progress with purpose, backed by intelligent guidance and skill tracking.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/login" className="btn btn-primary">Log In</Link>
              <Link href="/register" className="btn btn-outline">Sign Up</Link>
            </div>
          </div>
        </div>
      </section>
      {/* Problem Section */}
      <section className="section mt-1">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 gradient-text">The Problem We're Tackling</h2>
        <div className="diagnostic-grid">

          {/* Problem 1: Unclear Direction */}
          <div className="card card-problem-1">
            <div className="content">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m0 14v1m8-8h1M4 12H3m15.36 6.36l.71.71M6.34 6.34l-.71-.71m12.02 0l.71-.71M6.34 17.66l-.71.71" />
              </svg>
              <h3 className="para">Unclear Direction</h3>
              <p className="para">
                Many students don't know what they're good at, what excites them, or where to even begin exploring. Traditional guidance is shallow and generic.
              </p>
            </div>
          </div>

          {/* Problem 2: Digital Overload */}
          <div className="card card-problem-2">
            <div className="content">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V4a2 2 0 10-4 0v1.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <h3 className="para">It's easier to type than to talk</h3>
              <p className="para">
               Students often turn to screens instead of seeking help face-to-face.
              </p>
            </div>
          </div>

          {/* Problem 3: Fragmented and Passive Tools */}
          <div className="card card-problem-1">
            <div className="content">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.97-4.03 9-9 9S3 16.97 3 12 7.03 3 12 3s9 4.03 9 9z" />
              </svg>
              <h3 className="para">Fragmented and Passive Tools</h3>
              <p className="para">
                Advice is scattered and platforms like job boards or course lists don't engage users in self-reflection or adaptive learning.
              </p>
            </div>
          </div>

          {/* Problem 4: Fading Motivation */}
          <div className="card card-problem-2">
            <div className="content">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V4a2 2 0 10-4 0v1.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <h3 className="para">Fading Motivation</h3>
              <p className="para">
                Without meaningful feedback or visible progress, learners lose confidence and abandon their efforts prematurely.
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* Features Section */}
      <section className="section mt-1">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 gradient-text">How Navigo Helps</h2>
        <div className="diagnostic-grid">

          {/* Feature 1: Career Guidance */}
          <div className="card card-solution-1">
            <div className="content">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <h3 className="para">Skill-Based Career Mapping</h3>
              <p className="para">
                We go beyond job titles. Navigo builds a graph of your skills to suggest personalized next steps—based on what you know, what you're building, and where you want to go.
              </p>
            </div>
          </div>

          {/* Feature 2: Deep Personalization */}
          <div className="card card-solution-2">
            <div className="content">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 20l9-5-9-5-9 5 9 5z" />
              </svg>
              <h3 className="para">Built Around You</h3>
              <p className="para">
                Every interaction is personal. From career paths to reflection prompts, the platform adapts to who you are—your strengths, values, goals, and even your hesitations—creating a space where growth feels natural, relevant, and entirely yours.
              </p>
            </div>
          </div>

          {/* Feature 3: Personal Growth */}
          <div className="card card-solution-1">
            <div className="content">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <h3 className="para">Space: Your Personal Mission Hub</h3>
              <p className="para">
                Track your chosen career goals, compare your current skills with what's needed, reflect on daily progress, and receive reflections on how to advance.
              </p>
            </div>
          </div>

          {/* Feature 4: Future Path Prediction */}
          <div className="card card-solution-2">
            <div className="content">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0v7" />
              </svg>
              <h3 className="para">Engaging, not dreading</h3>
              <p className="para">
              Youth doesn't want to fill out a questionnaire for 1 hour and get a static answer of what to become. Instead, they engage with the platform interactively, and the platform indirectly learn about them and recommends them.
              </p>
            </div>
          </div>

        </div>
      </section>
      
      {/* Demo Chat Section avec Typewriter */}
      <main className="min-h-screen bg-gradient-to-b from-gray-0 to-white">
        <div className="container mx-auto px-2 py-4">
          <div className="talk-to-navigo-section">
            {/* Animation Typewriter */}
            <div className="typewriter">
              <div className="slide"><i></i></div>
              <div className="paper"></div>
              <div className="keyboard"></div>
            </div>
            
            {/* Titre */}
            <h1 className="talk-to-navigo-title">
              Talk to Navigo, and get him to know yourself
            </h1>
          </div>
          
          <p className="text-center text-neutral-600 max-w-xl mx-auto mb-6">
            The chat isn't just a bot—it's a reflection partner. It helps you dig deeper into your interests, reflect on experiences, and receive tailored guidance, in a calm and exploratory tone.
          </p>
          <div className="max-w-2xl mx-auto">
            <DemoChat />
          </div>
        </div>
      </main>

      <div className="max-w-1xl mx-auto bg-transparent">
        <JobSwipeCard />
      </div>
      
      {/* Career Tree Visual */}
      <section className="section">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-3 gradient-text">Career Growth Tree</h2>
        <div className="text-center text-neutral-600 max-w-xl mx-auto mb-6">
          <p>
            The tree is the intelligence of the platform, an AI recommendation engine, following the latest trends in the job market. It represents your evolving skillset and helps you see how different behaviors or experiences open new paths. Each branch is a future that grows from who you are now. 
          </p>
        </div>
        <SkillTreeFlow />
      </section>

      {/* Skills Tree Visual */}
            <section className="section">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-3 gradient-text">Technical Skills Growth Tree</h2>
        <div className="text-center text-neutral-600 max-w-xl mx-auto mb-6">
          <p>
          From spreadsheets to Python, from dashboards to dealmaking, it tracks your technical evolution and reveals the real roles these skills can lead to. Each branch connects what you're building now to what you could become—guided by what the market needs, and grounded in what you've already mastered.
          </p>
        </div>
        <CareerTechTree />
      </section>

      <section className="section mt-16 mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-6 gradient-text">
          Bridge Your Skills Gap
        </h2>
        <p className="text-center text-neutral-600 max-w-2xl mx-auto mb-12 text-lg">
          See how your current skills stack up—and what steps will take you closer to your dream role.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          {/* Left Column - Steps */}
          <div className="space-y-8">
            <h3 className="text-2xl font-bold text-primary-teal">How It Works</h3>
            <ul className="space-y-6">
              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Pick Your Goals</h4>
                  <p className="text-gray-600 mt-1 text-sm">Save the careers you're aiming for.</p>
                </div>
              </li>

              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-green-100 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">See Where You Stand</h4>
                  <p className="text-gray-600 mt-1 text-sm">Compare your skills with real-world expectations.</p>
                </div>
              </li>

              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-purple-100 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-purple-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Track the Gap</h4>
                  <p className="text-gray-600 mt-1 text-sm">Get a clear view of what's missing—and what's next.</p>
                </div>
              </li>

              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-yellow-100 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-yellow-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Get Next Steps</h4>
                  <p className="text-gray-600 mt-1 text-sm">Receive tailored challenges and learning paths.</p>
                </div>
              </li>
            </ul>
          </div>

          {/* Right Column - Chart */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Skills Gap Analysis</h3>
            <SkillSpiderChart />
          </div>
        </div>
      </section>

      {/* Psychological Tests Section */}
      <section className="section mt-16 mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-6 gradient-text">
          Discover Yourself Through Psychological Tests
        </h2>
        <p className="text-center text-neutral-600 max-w-2xl mx-auto mb-12 text-lg">
          Take our scientifically validated psychological assessments to better understand your personality, interests, and career preferences.
        </p>

        <div className="max-w-3xl mx-auto">
          <div className="radiogroup" onClick={(e) => e.preventDefault()}>
            <div className="wrapper">
              <input 
                type="radio" 
                name="test" 
                id="hexaco" 
                className="state" 
                checked={selectedTest === 'hexaco'}
                onChange={() => handleTestSelect('hexaco')}
              />
              <label htmlFor="hexaco" className="label">
                <div className="indicator"></div>
                <div className="text">
                  <span className="font-medium text-gray-900">HEXACO Personality Test</span>
                  <p className="text-gray-600 mt-1 text-sm">A comprehensive personality assessment measuring six major dimensions of personality: Honesty-Humility, Emotionality, Extraversion, Agreeableness, Conscientiousness, and Openness to Experience.</p>
                </div>
              </label>
            </div>
            <div className="wrapper">
              <input 
                type="radio" 
                name="test" 
                id="riasec" 
                className="state"
                checked={selectedTest === 'riasec'}
                onChange={() => handleTestSelect('riasec')}
              />
              <label htmlFor="riasec" className="label">
                <div className="indicator"></div>
                <div className="text">
                  <span className="font-medium text-gray-900">RIASEC Career Interest Test</span>
                  <p className="text-gray-600 mt-1 text-sm">Discover your career interests across six types: Realistic, Investigative, Artistic, Social, Enterprising, and Conventional.</p>
                </div>
              </label>
            </div>
            <div className="wrapper">
              <input 
                type="radio" 
                name="test" 
                id="longform" 
                className="state"
                checked={selectedTest === 'longform'}
                onChange={() => handleTestSelect('longform')}
              />
              <label htmlFor="longform" className="label">
                <div className="indicator"></div>
                <div className="text">
                  <span className="font-medium text-gray-900">Longform Questions</span>
                  <p className="text-gray-600 mt-1 text-sm">Deep dive into your values, motivations, and aspirations through thoughtful, open-ended questions.</p>
                </div>
              </label>
            </div>
          </div>
        </div>
      </section>

      {/* Section: Recommended School Programs */}
        <section className="section bg-white mt-12">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold gradient-text">Explore Programs That Match Your Growth</h2>
            <p className="text-neutral-600 mt-4 max-w-2xl mx-auto">
              As your skills grow, so do your options. Based on your aspirations, here are curated school programs designed to accelerate your journey. Each one builds on the strengths you're developing in Navigo.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-4">
            {[
              {
                id: 1,
                name: "Université de Montréal",
                program: "Informatique - Intelligence Artificielle",
                duration: "2 ans",
                cost: "8,500 € / an",
                skills: ["Machine Learning", "Deep Learning", "Python", "TensorFlow"],
                rating: 4.8,
              },
              {
                id: 2,
                name: "École Polytechnique",
                program: "Génie Logiciel",
                duration: "3 ans",
                cost: "7,800 € / an",
                skills: ["Développement Web", "Java", "Architecture Logicielle", "DevOps"],
                rating: 4.6,
              },
              {
                id: 3,
                name: "HEC Paris",
                program: "Management des Technologies",
                duration: "1 an",
                cost: "12,000 € / an",
                skills: ["Gestion de Projet", "Business Intelligence", "Leadership", "Innovation"],
                rating: 4.7,
              },
            ].map(program => (
              <div key={program.id} className="bg-gray-50 p-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-300">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">{program.name}</h3>
                    <p className="text-primary-purple mt-1 font-medium">{program.program}</p>
                  </div>
                  <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm font-medium">{program.rating}/5</span>
                </div>
                <hr className="my-4" />
                <div className="text-left space-y-2">
                  <p className="text-sm text-gray-600"><strong>Durée:</strong> {program.duration}</p>
                  <p className="text-sm text-gray-600"><strong>Coût:</strong> {program.cost}</p>
                  <div>
                    <p className="text-sm text-gray-600 font-medium">Compétences:</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {program.skills.map((skill, i) => (
                        <span key={i} className="bg-white border px-2 py-1 text-xs rounded-md text-gray-700">{skill}</span>
                      ))}
                    </div>
                  </div>
                </div>
                <button className="mt-4 w-full py-2 text-sm font-medium bg-primary-teal text-white rounded-md hover:bg-primary-teal/90 transition">En savoir plus</button>
              </div>
            ))}
          </div>
        </section>

      {/* Section: Resume Builder */}
      <section className="min-h-screen py-16 bg-gray-50">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-10 text-gray-800">
            Build your resume
          </h2>

          <div className="bg-white p-6 rounded-xl shadow-md">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Choose a model</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="rounded-md overflow-hidden border border-gray-200">
                <div className="h-32" style={{ backgroundColor: '#2c3e50' }} />
                <p className="text-center py-2 font-medium text-gray-700">Professional</p>
              </div>
              <div className="rounded-md overflow-hidden border border-gray-200">
                <div className="h-32" style={{ backgroundColor: '#8e44ad' }} />
                <p className="text-center py-2 font-medium text-gray-700">Creative</p>
              </div>
              <div className="rounded-md overflow-hidden border border-gray-200">
                <div className="h-32" style={{ backgroundColor: '#7f8c8d' }} />
                <p className="text-center py-2 font-medium text-gray-700">Minimaliste</p>
              </div>
            </div>

            <h3 className="text-xl font-semibold mb-2 text-gray-800">Your information is ready for integration</h3>
            <p className="text-sm text-gray-600 mb-4">
              Based on your background and skills, we've prepared a CV tailored to your profile.
            </p>

            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700 bg-gray-100 p-4 rounded-md mb-8">
              <li>Your technical and cross-disciplinary skills</li>
              <li>Your recommended training path</li>
              <li>Suggested projects to strengthen your profile</li>
              <li>Optimized keywords for ATS (application tracking systems)</li>
            </ul>

            <div className="text-center">
              <button className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 font-medium">
              Generate my CV
              </button>
            </div>
          </div>

          <div className="text-center mt-10">
            <button
              className="border border-gray-300 px-5 py-2 rounded-md text-gray-700 hover:bg-gray-100"
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            >
              Retour au début
            </button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section">
        <div className="bg-gradient-primary p-[1px] rounded-lg shadow-glow-purple">
          <div className="bg-neutral-600/90 backdrop-blur-md rounded-[calc(0.5rem-1px)] p-8 md:p-12">
            <div className="max-w-3xl mx-auto space-y-8">
              <h2 className="text-3xl md:text-4xl font-bold text-center text-neutral-50">
                Start Your Journey Today
              </h2>
              <p className="text-xl text-center text-neutral-100">
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

