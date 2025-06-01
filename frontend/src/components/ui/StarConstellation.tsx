// 'use client';

// import React, { useEffect, useRef } from 'react';
// import { useTheme } from '@/hooks/useTheme';

// interface Star {
//   x: number;
//   y: number;
//   size: number;
//   opacity: number;
//   speed: number;
//   angle: number;
// }

// const StarConstellation: React.FC = () => {
//   const canvasRef = useRef<HTMLCanvasElement>(null);
//   const starsRef = useRef<Star[]>([]);
//   const animationRef = useRef<number>();
//   const { resolvedTheme } = useTheme();

//   useEffect(() => {
//     const canvas = canvasRef.current;
//     if (!canvas) return;

//     const ctx = canvas.getContext('2d');
//     if (!ctx) return;

//     const resizeCanvas = () => {
//       canvas.width = window.innerWidth;
//       canvas.height = window.innerHeight;
//     };

//     const createStars = () => {
//       const stars: Star[] = [];
//       const numStars = Math.floor((window.innerWidth * window.innerHeight) / 8000);
      
//       for (let i = 0; i < numStars; i++) {
//         stars.push({
//           x: Math.random() * canvas.width,
//           y: Math.random() * canvas.height,
//           size: Math.random() * 2 + 0.5,
//           opacity: Math.random() * 0.8 + 0.2,
//           speed: Math.random() * 0.5 + 0.1,
//           angle: Math.random() * Math.PI * 2,
//         });
//       }
      
//       starsRef.current = stars;
//     };

//     const drawStar = (star: Star) => {
//       ctx.save();
//       ctx.globalAlpha = star.opacity;
      
//       // Couleurs adaptées au thème
//       const starColor = resolvedTheme === 'dark' ? '#fdc500' : '#00296b';
//       const glowColor = resolvedTheme === 'dark' ? '#ffd500' : '#003f88';
      
//       ctx.fillStyle = starColor;
//       ctx.shadowColor = starColor;
//       ctx.shadowBlur = star.size * 2;
      
//       ctx.beginPath();
//       ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
//       ctx.fill();
      
//       // Ajouter un effet de scintillement
//       if (Math.random() > 0.98) {
//         ctx.shadowBlur = star.size * 4;
//         ctx.fillStyle = glowColor;
//         ctx.beginPath();
//         ctx.arc(star.x, star.y, star.size * 1.5, 0, Math.PI * 2);
//         ctx.fill();
//       }
      
//       ctx.restore();
//     };

//     const updateStars = () => {
//       starsRef.current.forEach(star => {
//         // Mouvement subtil
//         star.x += Math.cos(star.angle) * star.speed * 0.1;
//         star.y += Math.sin(star.angle) * star.speed * 0.1;
        
//         // Scintillement
//         star.opacity += (Math.random() - 0.5) * 0.02;
//         star.opacity = Math.max(0.1, Math.min(0.9, star.opacity));
        
//         // Rebond sur les bords
//         if (star.x < 0 || star.x > canvas.width) star.angle = Math.PI - star.angle;
//         if (star.y < 0 || star.y > canvas.height) star.angle = -star.angle;
        
//         // Garder dans les limites
//         star.x = Math.max(0, Math.min(canvas.width, star.x));
//         star.y = Math.max(0, Math.min(canvas.height, star.y));
//       });
//     };

//     const animate = () => {
//       ctx.clearRect(0, 0, canvas.width, canvas.height);
      
//       updateStars();
//       starsRef.current.forEach(drawStar);
      
//       animationRef.current = requestAnimationFrame(animate);
//     };

//     resizeCanvas();
//     createStars();
//     animate();

//     const handleResize = () => {
//       resizeCanvas();
//       createStars();
//     };

//     window.addEventListener('resize', handleResize);

//     return () => {
//       window.removeEventListener('resize', handleResize);
//       if (animationRef.current) {
//         cancelAnimationFrame(animationRef.current);
//       }
//     };
//   }, []);

//   return (
//     <canvas
//       ref={canvasRef}
//       className="fixed inset-0 w-full h-full pointer-events-none"
//       style={{ zIndex: 1 }}
//     />
//   );
// };

// export default StarConstellation;

'use client';

import React, { useEffect, useRef } from 'react';

interface Node {
  angle: number;
  distance: number;
  size: number;
  x: number;
  y: number;
  opacity: number;
}

const StarConstellation: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<Node[]>([]);
  const animationRef = useRef<number>();

  // Pan and zoom state
  const offset = useRef({ x: 0, y: 0 });
  const dragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const zoom = useRef(1);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const createNodes = () => {
      const nodes: Node[] = [];
      const numNodes = 300;
      const radiusRange = 1000;

      for (let i = 0; i < numNodes; i++) {
        const angle = (Math.PI * 2 * i) / numNodes;
        const distance = Math.random() * radiusRange;

        nodes.push({
          angle,
          distance,
          size: Math.random() * 2 + 1,
          x: Math.cos(angle) * distance,
          y: Math.sin(angle) * distance,
          opacity: Math.random() * 0.5 + 0.5,
        });
      }

      nodesRef.current = nodes;
    };

    const draw = () => {
      const { width, height } = canvas;
      const centerX = width / 2 + offset.current.x;
      const centerY = height / 2 + offset.current.y;

      ctx.clearRect(0, 0, width, height);
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.scale(zoom.current, zoom.current);

      // Draw lines
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.lineWidth = 1 / zoom.current;

      for (const node of nodesRef.current) {
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(node.x, node.y);
        ctx.stroke();
      }

      // Draw nodes
      for (const node of nodesRef.current) {
        ctx.beginPath();
        ctx.fillStyle = `rgba(255, 255, 255, ${node.opacity})`;
        ctx.arc(node.x, node.y, node.size / zoom.current, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();
    };

    const animate = () => {
      draw();
      animationRef.current = requestAnimationFrame(animate);
    };

    const onMouseDown = (e: MouseEvent) => {
      dragging.current = true;
      dragStart.current = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      const dx = e.clientX - dragStart.current.x;
      const dy = e.clientY - dragStart.current.y;
      dragStart.current = { x: e.clientX, y: e.clientY };
      offset.current.x += dx;
      offset.current.y += dy;
    };

    const onMouseUp = () => {
      dragging.current = false;
    };

    const onWheel = (e: WheelEvent) => {
      const zoomFactor = 0.1;
      if (e.deltaY < 0) {
        zoom.current *= 1 + zoomFactor;
      } else {
        zoom.current *= 1 - zoomFactor;
      }
      zoom.current = Math.max(0.1, Math.min(zoom.current, 5));
    };

    resizeCanvas();
    createNodes();
    animate();

    window.addEventListener('resize', resizeCanvas);
    canvas.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('wheel', onWheel);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-auto cursor-grab active:cursor-grabbing"
      style={{ zIndex: 1 }}
    />
  );
};

export default StarConstellation;
