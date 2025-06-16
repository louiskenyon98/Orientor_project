import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import { 
  Home, 
  Brain, 
  Target, 
  GraduationCap, 
  Users, 
  TreePine,
  Menu,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/',
    icon: Home,
    description: 'Your personal overview'
  },
  {
    name: 'Assessments',
    href: '/assessments',
    icon: Brain,
    description: 'Personality and skill tests'
  },
  {
    name: 'Recommendations',
    href: '/recommendations',
    icon: Target,
    description: 'Career recommendations'
  },
  {
    name: 'Education',
    href: '/education',
    icon: GraduationCap,
    description: 'School programs & pathways',
    highlight: true // New feature
  },
  {
    name: 'Skill Trees',
    href: '/competence-tree',
    icon: TreePine,
    description: 'Learning paths'
  },
  {
    name: 'Peers',
    href: '/peers',
    icon: Users,
    description: 'Connect with others'
  }
];

export function Navigation() {
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === '/') {
      return router.pathname === '/';
    }
    return router.pathname.startsWith(href);
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-lg">O</span>
              </div>
              <span className="text-xl font-bold text-gray-900">Orientor</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navigationItems.map((item) => (
              <Link key={item.name} href={item.href}>
                <div
                  className={`
                    relative px-3 py-2 rounded-md text-sm font-medium transition-all duration-200
                    ${isActive(item.href)
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }
                  `}
                >
                  <div className="flex items-center">
                    <item.icon className="w-4 h-4 mr-2" />
                    <span>{item.name}</span>
                    {item.highlight && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="ml-2"
                      >
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          New
                        </span>
                      </motion.div>
                    )}
                  </div>
                  
                  {isActive(item.href) && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"
                      initial={false}
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                </div>
              </Link>
            ))}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2"
            >
              {isMobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden py-2 border-t border-gray-200"
          >
            <div className="grid grid-cols-1 gap-1">
              {navigationItems.map((item) => (
                <Link key={item.name} href={item.href}>
                  <div
                    className={`
                      px-3 py-3 rounded-md text-sm font-medium flex items-center justify-between
                      ${isActive(item.href)
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }
                    `}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <div className="flex items-center">
                      <item.icon className="w-4 h-4 mr-3" />
                      <div>
                        <div className="font-medium">{item.name}</div>
                        <div className="text-xs text-gray-500">{item.description}</div>
                      </div>
                    </div>
                    {item.highlight && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        New
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </nav>
  );
}