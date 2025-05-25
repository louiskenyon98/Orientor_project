'use client';
import React from 'react';
import Image from 'next/image';
import { motion } from 'framer-motion';

interface UserCardProps {
  name: string;
  role: string;
  avatarUrl: string;
  skills: string[];
  className?: string;
}

const UserCard: React.FC<UserCardProps> = ({ name, role, avatarUrl, skills, className }) => {
  return (
    <div className={`card ${className || ''}`}>
      <div className="card__img">
        <svg viewBox="0 0 300 192" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="300" height="192" fill="#F5F5F5"/>
        </svg>
      </div>
      <div className="card__avatar">
        <Image
          src={avatarUrl}
          alt={name}
          width={100}
          height={100}
          className="rounded-full"
        />
      </div>
      <h2 className="card__title">{name}</h2>
      <p className="card__subtitle">{role}</p>
      <button className="card__btn">Profile</button>
    </div>
  );
};

export default UserCard;