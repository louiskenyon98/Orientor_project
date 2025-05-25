import React from 'react';
import Link from 'next/link';
import styles from './NewSidebar.module.css';

interface NavItem {
  name: string;
  icon: string;
  path: string;
}

interface NewSidebarProps {
  navItems: NavItem[];
}

const NewSidebar: React.FC<NewSidebarProps> = ({ navItems }) => {
  return (
    <div className={styles.sidebar}>
      <div className={styles.navContainer}>
        {navItems.map((item, index) => (
          <Link href={item.path} key={index} className={styles.navItem}>
            <div className={styles.iconWrapper}>
              {item.icon === 'Chat' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M216,48H40A16,16,0,0,0,24,64V224a15.84,15.84,0,0,0,9.25,14.5A16.05,16.05,0,0,0,40,240a15.89,15.89,0,0,0,10.25-3.78.69.69,0,0,0,.13-.11L82.5,208H216a16,16,0,0,0,16-16V64A16,16,0,0,0,216,48ZM40,224V64H216V192H82.5a16,16,0,0,0-10.25,3.78L40,224Z"></path>
                </svg>
              )}
              {item.icon === 'Peers' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M128,120a48,48,0,1,0-48-48A48,48,0,0,0,128,120Zm0,16c-33.08,0-96,16.54-96,49.38V200a8,8,0,0,0,8,8H216a8,8,0,0,0,8-8v-14.62C224,152.54,161.08,136,128,136Z"></path>
                </svg>
              )}
              {item.icon === 'Personality' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M232,128a104,104,0,1,0-193.55,58.25C41.62,187.2,40,191.43,40,196v20a12,12,0,0,0,12,12H88a12,12,0,0,0,12-12V204h8a8,8,0,0,0,8-8V168a40.05,40.05,0,0,0,40-40v-8a8,8,0,0,0-8-8H139.75a40,40,0,0,0-75.5,0H56a8,8,0,0,0,0,16h80a24,24,0,0,1,24,24v8a8,8,0,0,0,8,8h8a12,12,0,0,0,12-12V196c0-4.57-1.62-8.8-4.45-12.25ZM128,24A88,88,0,1,1,40,112,88.1,88.1,0,0,1,128,24Z"></path>
                </svg>
              )}
              {item.icon === 'Bookmark' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Zm0,177.57-51.77-32.35a8,8,0,0,0-8.48,0L72,209.57V48H184Z"></path>
                </svg>
              )}
              {item.icon === 'Trophy' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M232,64H208V56a16,16,0,0,0-16-16H64A16,16,0,0,0,48,56v8H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-28.49,64.64-63.51,64.9H128a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"></path>
                </svg>
              )}
              {item.icon === 'Note' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM40,56H216v96H176a16,16,0,0,0-16,16v48H40Zm152,144V168h24v32Z"></path>
                </svg>
              )}
              {item.icon === 'Case Study' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M128,16A112,112,0,1,0,240,128,112.13,112.13,0,0,0,128,16Zm0,208a96,96,0,1,1,96-96A96.11,96.11,0,0,1,128,224Z"></path>
                </svg>
              )}
            </div>
            <span className={styles.tooltip}>{item.name}</span>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default NewSidebar; 