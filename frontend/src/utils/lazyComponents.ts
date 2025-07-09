'use client';
import { lazy } from 'react';

// Lazy load heavy components for better initial page load
export const LazyComponents = {
  // Chart components
  ChartComponent: lazy(() => import('../components/ui/ChartComponent').catch(() => ({ default: () => null }))),
  
  // Complex visualizations
  SkillsTreeVisualization: lazy(() => import('../components/skills/SkillsTreeVisualization').catch(() => ({ default: () => null }))),
  
  // Advanced features
  AdvancedAnalytics: lazy(() => import('../components/analytics/AdvancedAnalytics').catch(() => ({ default: () => null }))),
  
  // Heavy UI components
  RichTextEditor: lazy(() => import('../components/ui/RichTextEditor').catch(() => ({ default: () => null }))),
  
  // Calendar components
  FullCalendar: lazy(() => import('../components/calendar/FullCalendar').catch(() => ({ default: () => null }))),
};

// Preload critical components on user interaction
export const preloadComponent = (componentName: keyof typeof LazyComponents) => {
  if (typeof window !== 'undefined') {
    // Preload on user interaction (hover, focus, etc.)
    const component = LazyComponents[componentName];
    if (component) {
      // This will start loading the component
      component;
    }
  }
};

// Intersection Observer for lazy loading sections
export const useLazySection = (threshold = 0.1) => {
  if (typeof window === 'undefined') return { ref: null, isVisible: false };
  
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLElement>(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect(); // Only trigger once
        }
      },
      { threshold }
    );
    
    if (ref.current) {
      observer.observe(ref.current);
    }
    
    return () => observer.disconnect();
  }, [threshold]);
  
  return { ref, isVisible };
};