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
              {item.icon === 'Dashboard' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M112,39.38V104a8,8,0,0,1-8,8H40a8,8,0,0,1-8-8V39.38a8,8,0,0,1,13.66-5.66l64,64A8,8,0,0,1,112,39.38ZM104,152a8,8,0,0,0-8-8H40a8,8,0,0,0-8,8v64.62a8,8,0,0,0,13.66,5.66l64-64A8,8,0,0,0,104,152Zm48-112a8,8,0,0,0-8,8V104a8,8,0,0,0,8,8h64.62a8,8,0,0,0,5.66-13.66l-64-64A8,8,0,0,0,152,40Zm64,104H160a8,8,0,0,0-8,8v64.62a8,8,0,0,0,13.66,5.66l64-64A8,8,0,0,0,224,152,8,8,0,0,0,216,144Z"></path>
                </svg>
              )}
              {item.icon === 'Education' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M208,24H72A32,32,0,0,0,40,56V224a8,8,0,0,0,8,8H192a8,8,0,0,0,0-16H56a16,16,0,0,1,16-16H208a8,8,0,0,0,8-8V32A8,8,0,0,0,208,24Zm-8,160H72a31.82,31.82,0,0,0-16,4.29V56A16,16,0,0,1,72,40H200Z"></path>
                </svg>
              )}
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
              {item.icon === 'Tree' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M198.1,62.6a76,76,0,0,0-140.2,0A72.27,72.27,0,0,0,16,127.8C15.89,166.62,47.36,199,86.14,200A71.68,71.68,0,0,0,120,192.49V232a8,8,0,0,0,16,0V192.49A71.45,71.45,0,0,0,168,200l1.86,0c38.78-1,70.25-33.36,70.14-72.18A72.26,72.26,0,0,0,198.1,62.6ZM169.45,184a55.61,55.61,0,0,1-32.52-9.4q-.47-.3-.93-.57V132.94l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94V174q-.47.27-.93.57A55.7,55.7,0,0,1,86.55,184a56,56,0,0,1-22-106.86,15.9,15.9,0,0,0,8.05-8.33,60,60,0,0,1,110.7,0,15.9,15.9,0,0,0,8.05,8.33,56,56,0,0,1-22,106.86Z"></path>
                </svg>
              )}
              {item.icon === 'Swipe' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M7.5 5.25a3 3 0 0 1 3-3h3a3 3 0 0 1 3 3v.205c.933.085 1.857.197 2.774.334 1.454.218 2.476 1.483 2.476 2.917v3.033c0 1.211-.734 2.352-1.936 2.752A24.726 24.726 0 0 1 12 15.75c-2.73 0-5.357-.442-7.814-1.259-1.202-.4-1.936-1.541-1.936-2.752V8.706c0-1.434 1.022-2.7 2.476-2.917A48.814 48.814 0 0 1 7.5 5.455V5.25Zm7.5 0v.09a49.488 49.488 0 0 0-6 0v-.09a1.5 1.5 0 0 1 1.5-1.5h3a1.5 1.5 0 0 1 1.5 1.5Zm-3 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" clipRule="evenodd" />
                  <path d="M3 18.4v-2.796a4.3 4.3 0 0 0 .713.31A26.226 26.226 0 0 0 12 17.25c2.892 0 5.68-.468 8.287-1.335.252-.084.49-.189.713-.311V18.4c0 1.452-1.047 2.728-2.523 2.923-2.12.282-4.282.427-6.477.427a49.19 49.19 0 0 1-6.477-.427C4.047 21.128 3 19.852 3 18.4Z" />
                </svg>
              )}
            </div>
            <span className={styles.tooltip}>{item.name}</span>
          </Link>
        ))}
      </div>
      
      {/* Profile Icon at Bottom */}
      <div className={styles.profileContainer}>
        <Link href="/profile" className={styles.navItem}>
          <div className={styles.iconWrapper}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
              <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24ZM74.08,197.5a64,64,0,0,1,107.84,0,87.83,87.83,0,0,1-107.84,0ZM96,120a32,32,0,1,1,32,32A32,32,0,0,1,96,120Zm97.76,66.41a79.66,79.66,0,0,0-36.06-28.75,48,48,0,1,0-59.4,0,79.66,79.66,0,0,0-36.06,28.75,88,88,0,1,1,131.52,0Z"></path>
            </svg>
          </div>
          <span className={styles.tooltip}>Profile</span>
        </Link>
      </div>
    </div>
  );
};

export default NewSidebar; 