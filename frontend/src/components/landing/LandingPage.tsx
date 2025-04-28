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
            {/* Hero Background Image
            <div className="absolute inset-0 -z-10">
              <Image
                src="/navigo-hero.png"
                alt="Navigo forest visual"
                layout="fill"
                objectFit="cover"
                className="opacity-40"
                priority
              />
            </div> */}
          </div>
        </div>
      </section>
      {/* Problem Section */}
      <section className="section mt-1">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 gradient-text">The Problem We're Tackling</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">

          {/* Problem 1: Unclear Direction */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-red-100 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m0 14v1m8-8h1M4 12H3m15.36 6.36l.71.71M6.34 6.34l-.71-.71m12.02 0l.71-.71M6.34 17.66l-.71.71" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-red-600 mb-4">Unclear Direction</h3>
            <p className="text-neutral-500">
              Many students don't know what they're good at, what excites them, or where to even begin exploring. Traditional guidance is shallow and generic.
            </p>
          </div>

          {/* Problem 2:  Digital Overload */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-blue-100 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V4a2 2 0 10-4 0v1.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-600 mb-4">It's easier to type than to talk</h3>
            <p className="text-neutral-500">
             Students often turn to screens instead of seeking help face-to-face.
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
              Advice is scattered and platforms like job boards or course lists don't engage users in self-reflection or adaptive learning.
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">

          {/* Feature 1: Career Guidance */}
          <div className="card hover-lift border-l-4 border-primary-teal bg-primary-purple/10">
            <div className="mb-6 p-3 bg-primary-purple/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-primary-teal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-primary-teal mb-4">Skill-Based Career Mapping</h3>
            <p className="text-neutral-600">
              We go beyond job titles. Navigo builds a graph of your skills to suggest personalized next steps—based on what you know, what you're building, and where you want to go.
            </p>
          </div>

          {/* Feature 2: Deep Personalization */}
          <div className="card hover-lift border-l-4 border-accent-teal bg-accent-teal/10">
            <div className="mb-6 p-3 bg-accent-teal/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-accent-teal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 20l9-5-9-5-9 5 9 5z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-accent-teal mb-4">Built Around You</h3>
            <p className="text-neutral-600">
              Every interaction is personal. From career paths to reflection prompts, the platform adapts to who you are—your strengths, values, goals, and even your hesitations—creating a space where growth feels natural, relevant, and entirely yours.
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
              Track your chosen career goals, compare your current skills with what's needed, reflect on daily progress, and receive reflections on how to advance.
            </p>
          </div>

          {/* Feature 4: Future Path Prediction */}
          <div className="card hover-lift border-l-4 border-primary-purple bg-primary-teal/10">
            <div className="mb-6 p-3 bg-primary-teal/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-primary-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0v7" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-primary-purple mb-4">Engaging, not dreading</h3>
            <p className="text-neutral-600">
            Youth doesn't want to fill out a questionnaire for 1 hour and get a static answer of what to become. Instead, they engage with the platform interactively, and the platform indirectly learn about them and recommends them.
            </p>
          </div>

        </div>
      </section>
      
      {/* Skills Gap Section */}
      <section className="section mt-16 mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-6 gradient-text">Understand Your Path, Bridge the Gap</h2>
        <div className="text-center text-neutral-600 max-w-2xl mx-auto mb-12">
          <p className="text-lg">
            Our AI compares your current skills against career profiles defined by over 100 variables — including skills, tasks, abilities, interests, and general requirements.
          </p>
          <p className="text-lg mt-4">
            Once you save the careers you aspire to, our AI analyzes how far you are from these roles. It doesn't just stop there — it recommends actionable steps, tailored learning paths, and personal challenges to help you close the gap between your current profile and your dream career.
          </p>
          <p className="text-lg mt-4">
            With every step, you're not just imagining your future — you're actively building it.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          {/* Left Column - Text */}
          <div className="space-y-8">
            <h3 className="text-2xl font-bold text-primary-teal">Your Journey, Made Visible</h3>
            <p className="text-neutral-600">
              Our AI doesn't just show you the dream — it shows you the work. It compares where you are today to where you want to be, and guides you step-by-step to bridge the gap.
            </p>
            
            <ul className="space-y-6">
              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Save Your Dream Careers</h4>
                  <p className="text-gray-600 mt-1">Identify the roles that inspire you and add them to your personal space.</p>
                </div>
              </li>
              
              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-green-100 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Compare Your Skills</h4>
                  <p className="text-gray-600 mt-1">See where you currently stand across 100+ skill and ability dimensions.</p>
                </div>
              </li>
              
              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-purple-100 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-purple-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Visualize the Gap</h4>
                  <p className="text-gray-600 mt-1">Discover how far you are from your goals — clearly, visually, and personalized.</p>
                </div>
              </li>
              
              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-yellow-100 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-yellow-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Get Actionable Guidance</h4>
                  <p className="text-gray-600 mt-1">Receive personalized recommendations and challenges to help you bridge the distance.</p>
                </div>
              </li>
            </ul>
            
            <Link href="/register" className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-teal hover:bg-primary-teal/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-teal">
              See How You Compare
            </Link>
          </div>
          
          {/* Right Column - Spider Chart */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Skills Gap Analysis</h3>
            <SkillSpiderChart />
          </div>
        </div>
      </section>

      {/* Resume Section */}
      <section className="section mt-16 mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-6 gradient-text">Turn Your Growth Into a Resume</h2>
        <div className="text-center text-neutral-600 max-w-2xl mx-auto mb-12">
          <p className="text-lg">
            As you explore careers, refine your skills, and grow through challenges, our AI quietly builds a resume for you — gathering everything you accomplish into a beautiful, professional document, ready to launch your future.
          </p>
          <p className="text-lg mt-4">
            Your story, your skills, your evolution — transformed into a resume that speaks for you.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          {/* Left Column - Text */}
          <div className="space-y-8 order-2 md:order-1">
            <h3 className="text-2xl font-bold text-primary-teal">Professionally Crafted, Automatically Updated</h3>
            <p className="text-neutral-600">
              No more stress over resume formatting or wondering what to highlight. As you interact with Navigo, we capture your growth journey and transform it into a compelling professional narrative.
            </p>
            
            <ul className="space-y-6">
              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-purple/20 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-primary-purple" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Automatic Updates</h4>
                  <p className="text-gray-600 mt-1">Your resume evolves as you do, reflecting new skills and accomplishments in real-time.</p>
                </div>
              </li>
              
              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-teal/20 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-primary-teal" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Professional Design</h4>
                  <p className="text-gray-600 mt-1">Beautiful templates that highlight your strengths and present you at your best.</p>
                </div>
              </li>
              
              <li className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-accent-amber/20 flex items-center justify-center mr-3 mt-1">
                  <svg className="h-4 w-4 text-accent-amber" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Export Ready</h4>
                  <p className="text-gray-600 mt-1">Download your resume in multiple formats whenever you need it for applications.</p>
                </div>
              </li>
            </ul>
            
            <Link href="/register" className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-purple hover:bg-primary-purple/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-purple">
              Start Building Your Resume
            </Link>
            <p className="text-sm text-gray-500 mt-2">No templates, no stress — just your journey, captured and elevated.</p>
          </div>
          
          {/* Right Column - Resume Image */}
          <motion.div 
            className="order-1 md:order-2"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-primary-purple/30 to-primary-teal/30 rounded-lg blur opacity-30 group-hover:opacity-60 transition duration-1000"></div>
              <div className="relative bg-white rounded-lg transform transition duration-500 group-hover:scale-[1.01] group-hover:-rotate-1">
                <Image
                  src="/images/resume.jpeg"
                  width={600}
                  height={800}
                  alt="Professional resume created automatically"
                  className="rounded-lg shadow-lg"
                />
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="bg-white/90 px-4 py-2 rounded-md shadow-md">
                    <p className="text-sm font-medium text-gray-700">Built Automatically. Updated Live as You Grow.</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

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

