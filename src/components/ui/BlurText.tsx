'use client';

import { motion } from 'framer-motion';

interface BlurTextProps {
  text?: string;
  delay?: number;
  startDelay?: number;
  className?: string;
  animateBy?: 'words' | 'letters';
  direction?: 'top' | 'bottom';
  onAnimationComplete?: () => void;
}

const BlurText = ({
  text = '',
  delay = 100,
  startDelay = 0,
  className = '',
  animateBy = 'letters',
  direction = 'top',
  onAnimationComplete,
}: BlurTextProps) => {
  const elements = animateBy === 'words' ? text.split(' ') : text.split('');

  return (
    <span style={{ position: 'relative', zIndex: 10 }}>
      {elements.map((segment, index) => (
        <motion.span
          key={index}
          className={`${className} inline-block will-change-[transform,filter,opacity]`}
          initial={{
            filter: 'blur(10px)',
            opacity: 0,
            y: direction === 'top' ? -30 : 30
          }}
          animate={{
            filter: 'blur(0px)',
            opacity: 1,
            y: 0
          }}
          transition={{
            duration: 0.5,
            delay: startDelay / 1000 + (index * delay) / 1000,
            ease: 'easeOut'
          }}
          onAnimationComplete={index === elements.length - 1 ? onAnimationComplete : undefined}
        >
          {segment === ' ' ? '\u00A0' : segment}
          {animateBy === 'words' && index < elements.length - 1 && '\u00A0'}
        </motion.span>
      ))}
    </span>
  );
};

export default BlurText;
