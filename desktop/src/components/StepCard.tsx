import React, { useState } from 'react';
import { 
  CheckCircle2, 
  CircleDashed, 
  AlertCircle, 
  Clock, 
  ChevronDown, 
  ChevronRight
} from 'lucide-react';
import { StepItem } from '../types.ts';

interface StepCardProps {
  step: StepItem;
}

export const StepCard: React.FC<StepCardProps> = ({ step }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const getStatusIcon = () => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0" />;
      case 'running':
        return <CircleDashed size={16} className="text-brand-400 animate-spin flex-shrink-0" />;
      case 'error':
        return <AlertCircle size={16} className="text-rose-400 flex-shrink-0" />;
      default:
        return <Clock size={16} className="text-gray-500 flex-shrink-0" />;
    }
  };

  const getStatusBadge = () => {
    switch (step.status) {
      case 'completed':
        return <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/40">COMPLETADO</span>;
      case 'running':
        return <span className="text-[10px] px-2 py-0.5 rounded bg-brand-950/60 text-brand-300 border border-brand-800/40 animate-pulse">EN EJECUCIÓN</span>;
      case 'error':
        return <span className="text-[10px] px-2 py-0.5 rounded bg-rose-950/60 text-rose-300 border border-rose-800/40">ERROR</span>;
      default:
        return <span className="text-[10px] px-2 py-0.5 rounded bg-gray-800 text-gray-400">PENDIENTE</span>;
    }
  };

  return (
    <div className="rounded-lg border border-border bg-card/60 overflow-hidden shadow-sm my-3 transition">
      {/* Header */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between px-3.5 py-2.5 bg-card cursor-pointer hover:bg-card/80 transition"
      >
        <div className="flex items-center space-x-2.5">
          {getStatusIcon()}
          <span className="font-medium text-xs text-gray-200">{step.title}</span>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusBadge()}
          {isExpanded ? <ChevronDown size={14} className="text-gray-400" /> : <ChevronRight size={14} className="text-gray-400" />}
        </div>
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className="p-3 text-xs border-t border-border/40 bg-surface/40 space-y-2">
          {/* Substeps list */}
          {step.substeps.length > 0 && (
            <ul className="space-y-1.5 font-mono text-[11px] text-gray-300">
              {step.substeps.map((sub, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-brand-400 mt-0.5">›</span>
                  <span className="leading-relaxed">{sub}</span>
                </li>
              ))}
            </ul>
          )}

          {/* Subprocess output preview if any */}
          {step.output && (
            <div className="mt-2 p-2 rounded bg-background border border-border font-mono text-[11px] text-gray-300 overflow-x-auto max-h-48">
              <pre className="whitespace-pre-wrap">{step.output}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
