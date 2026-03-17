interface AnimatedOrbProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeClasses = {
  sm: 'w-24 h-24',
  md: 'w-32 h-32',
  lg: 'w-48 h-48',
  xl: 'w-64 h-64',
};

export function AnimatedOrb({ size = 'lg', className = '' }: AnimatedOrbProps) {
  return (
    <div className={`${sizeClasses[size]} rounded-full relative ${className}`}>
      <div className="absolute inset-0 bg-linear-to-b from-white via-indigo-200 to-indigo-500 rounded-full blur-xl opacity-80 animate-pulse"></div>
      <div className="absolute inset-0 bg-linear-to-b from-white via-indigo-300 to-indigo-600 rounded-full"></div>
    </div>
  );
}
