'use client';
import React from 'react';
import Image from 'next/image';
import { motion } from 'framer-motion';

interface UserCardProps {
  name: string;
  role?: string;
  avatarUrl?: string;
  skills?: string[];
  domain?: 'builder' | 'communicator' | undefined;
  className?: string;
  onClick?: () => void;
}

export default function UserCard({
  name,
  role,
  avatarUrl = '/images/default-avatar.png',
  skills = [],
  domain,
  className = '',
  onClick
}: UserCardProps) {
  // Déterminer les couleurs en fonction du domaine
  const domainColor = domain === 'builder' 
    ? 'border-domain-builder' 
    : domain === 'communicator' 
      ? 'border-domain-communicator' 
      : 'border-accent';

  return (
    <motion.div 
      className={`flex flex-col items-center gap-4 ${className}`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      {/* Avatar Container */}
      <div className="flex-shrink-0">
        <div className={`relative w-32 h-32 rounded-full overflow-hidden border-2`}
             style={{ borderColor: domain === 'builder'
                      ? 'var(--domain-builder-color)'
                      : domain === 'communicator'
                        ? 'var(--domain-communicator-color)'
                        : 'var(--accent-color)' }}>
          <Image 
            src={avatarUrl} 
            alt={`${name}'s avatar`} 
            fill
            sizes="128px"
            className="object-cover"
            priority
          />
        </div>
      </div>

      {/* User Info */}
      <div className="flex flex-col items-center text-center">
        <h3 className="text-xl font-bold font-departure mb-1" style={{ color: 'var(--accent-color)' }}>{name}</h3>
        {role && <p className="text-base mb-3" style={{ color: 'var(--text-color)' }}>{role}</p>}
        
        {/* Skills Tags */}
        {skills.length > 0 && (
          <div className="flex flex-wrap justify-center gap-2">
            {skills.slice(0, 3).map((skill, index) => (
              <span 
                key={index} 
                className="text-sm px-3 py-1 border rounded-full"
                style={{
                  backgroundColor: 'var(--primary-color)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-color)'
                }}
              >
                {skill}
              </span>
            ))}
            {skills.length > 3 && (
              <span className="text-sm px-3 py-1 border rounded-full"
                    style={{
                      backgroundColor: 'var(--primary-color)',
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-color)'
                    }}>
                +{skills.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}