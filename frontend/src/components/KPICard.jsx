// src/components/KPICard.jsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

function useCountUp(end, duration = 300) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime = null;
    let animationFrame;

    const step = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const percentage = Math.min(progress / duration, 1);
      
      // ease-out cubic
      const easeOut = 1 - Math.pow(1 - percentage, 3);
      setCount(Math.floor(end * easeOut));

      if (progress < duration) {
        animationFrame = window.requestAnimationFrame(step);
      } else {
        setCount(end);
      }
    };

    animationFrame = window.requestAnimationFrame(step);

    return () => window.cancelAnimationFrame(animationFrame);
  }, [end, duration]);

  return count;
}

export function KPICard({ 
  title, 
  value, 
  icon: Icon, 
  color, 
  loading = false, 
  trend, // { value: number, label: string }
  criticalStatus // 'warning' | 'error'
}) {
  const numericValue = typeof value === 'number' ? value : parseFloat(value) || 0;
  const isPercentage = typeof value === 'string' && value.includes('%');
  const animatedValue = useCountUp(numericValue, 300);
  const displayValue = isPercentage ? `${animatedValue}%` : animatedValue;

  if (loading) {
    return (
      <Card className="p-5 border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 rounded-xl">
        <div className="flex justify-between items-start mb-2">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded bg-slate-200 dark:bg-slate-700 animate-pulse" />
            <div className="h-3 w-24 rounded bg-slate-200 dark:bg-slate-700 animate-pulse" />
          </div>
        </div>
        <div className="h-[48px] w-20 rounded bg-slate-200 dark:bg-slate-700 animate-pulse mt-2" />
      </Card>
    );
  }

  const borderClass = criticalStatus === 'warning' ? 'border-l-4 border-l-warning' : 
                      criticalStatus === 'error' ? 'border-l-4 border-l-danger' : '';

  return (
    <Card className={`p-5 border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 rounded-xl transition-all duration-200 shadow-sm hover:shadow-[0_2px_8px_rgba(0,0,0,0.06)] hover:-translate-y-px flex flex-col justify-between ${borderClass}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {Icon && <Icon className="h-6 w-6 flex-shrink-0" style={{ color }} />}
          <span className="text-[12px] font-medium text-muted-foreground">{title}</span>
        </div>
      </div>

      {/* Value & Trend */}
      <div className="flex items-end justify-between">
        <p className="text-[40px] font-semibold leading-none text-foreground mt-2">
          {displayValue}
        </p>
        
        {trend && value > 0 && (
          <div className={`flex items-center gap-1 text-[11px] font-medium px-2 py-1 rounded-full ${
            trend.value > 0 ? 'bg-success/10 text-success' : 
            trend.value < 0 ? 'bg-danger/10 text-danger' : 
            'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
          }`}>
            {trend.value > 0 ? <TrendingUp className="h-3 w-3" /> : 
             trend.value < 0 ? <TrendingDown className="h-3 w-3" /> : 
             <Minus className="h-3 w-3" />}
            <span>{trend.value > 0 ? '+' : ''}{trend.value}% {trend.label}</span>
          </div>
        )}
      </div>
    </Card>
  );
}
