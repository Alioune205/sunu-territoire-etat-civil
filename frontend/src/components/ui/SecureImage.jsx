import React, { useState, useEffect, useRef } from 'react';
import useSecureImage from '@/hooks/useSecureImage';

export default function SecureImage({ src, alt, className, ...props }) {
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: '50px' }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => {
      observer.disconnect();
    };
  }, []);

  const { objectUrl, error, loading } = useSecureImage(src, isVisible);

  if (error) {
    return (
      <div 
        ref={containerRef}
        className={`flex items-center justify-center bg-slate-200 text-slate-500 text-sm ${className}`}
      >
        Image indisponible
      </div>
    );
  }

  if (loading || !objectUrl) {
    return (
      <div 
        ref={containerRef}
        className={`animate-pulse bg-slate-200 ${className}`}
      ></div>
    );
  }

  return <img ref={containerRef} src={objectUrl} alt={alt} className={className} {...props} />;
}
