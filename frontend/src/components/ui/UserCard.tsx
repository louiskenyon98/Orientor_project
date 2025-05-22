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
      : 'border-stitch-accent';

  return (
    <motion.div 
      className={`user-card ${className}`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      {/* Avatar */}
      <div className={`avatar h-16 w-16 ${domainColor}`}>
        <Image 
          src={avatarUrl} 
          alt={`${name}'s avatar`} 
          width={64} 
          height={64}
          className="w-full h-full object-cover"
        />
      </div>

      {/* User Info */}
      <div className="flex flex-col">
        <h3 className="text-lg font-bold font-departure text-stitch-accent mb-0">{name}</h3>
        {role && <p className="text-sm text-stitch-sage mb-2">{role}</p>}
        
        {/* Skills Tags */}
        {skills.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {skills.slice(0, 3).map((skill, index) => (
              <span 
                key={index} 
                className="text-xs px-2 py-0.5 bg-stitch-primary border border-stitch-border rounded-full"
              >
                {skill}
              </span>
            ))}
            {skills.length > 3 && (
              <span className="text-xs px-2 py-0.5 bg-stitch-primary border border-stitch-border rounded-full">
                +{skills.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}