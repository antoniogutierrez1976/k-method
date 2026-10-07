import { X, Layers } from 'lucide-react';
import { EmbeddedSkill } from '../types.ts';

interface SkillModalProps {
  skill: EmbeddedSkill | null;
  onClose: () => void;
}

export const SkillModal: React.FC<SkillModalProps> = ({ skill, onClose }) => {
  if (!skill) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-card border border-border rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-4 py-3 border-b border-border flex items-center justify-between bg-surface">
          <div className="flex items-center space-x-2">
            <Layers size={16} className="text-brand-500" />
            <h3 className="font-mono text-sm font-semibold text-gray-100">{skill.name}</h3>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-950/60 text-brand-300 border border-brand-800/40 font-mono">
              v0
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-card text-gray-400 hover:text-gray-200"
          >
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div className="p-4 overflow-y-auto space-y-4 text-xs">
          <div>
            <span className="text-gray-400 block text-[11px] mb-1">Capa Metodológica:</span>
            <span className="font-semibold text-brand-400">{skill.layer}</span>
          </div>

          <div>
            <span className="text-gray-400 block text-[11px] mb-1">Descripción:</span>
            <p className="text-gray-300 leading-relaxed">{skill.description}</p>
          </div>

          <div>
            <span className="text-gray-400 block text-[11px] mb-1">Directiva Canónica Inyectada en Memoria (System Prompt):</span>
            <pre className="p-3 rounded-lg bg-background border border-border font-mono text-[11px] text-gray-300 whitespace-pre-wrap max-h-72 overflow-y-auto select-text">
              {skill.directive}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-2.5 border-t border-border bg-surface flex justify-end">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-lg bg-card hover:bg-card/80 border border-border text-xs text-gray-300 hover:text-white"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};
