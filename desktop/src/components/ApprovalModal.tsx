import React, { useState } from 'react';
import { ShieldCheck, Check, X } from 'lucide-react';

interface ApprovalModalProps {
  specContent: string;
  onApprove: () => void;
  onReject: (feedback: string) => void;
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({
  specContent,
  onApprove,
  onReject,
}) => {
  const [feedback, setFeedback] = useState('');
  const [showRejectInput, setShowRejectInput] = useState(false);

  return (
    <div className="rounded-xl border border-brand-500/50 bg-brand-950/20 p-4 my-4 shadow-lg backdrop-blur">
      <div className="flex items-center space-x-2 text-brand-400 font-semibold text-sm mb-2">
        <ShieldCheck size={18} />
        <span>Compuerta de Aprobación Humana: Especificación Formal (Layer 1)</span>
      </div>

      <p className="text-xs text-gray-300 mb-2 leading-relaxed">
        El motor ha redactado la especificación formal respetando la regla canónica de Karpathy (máximo 6 ACs).
        Revise el documento en la pestaña lateral <strong>Artifacts</strong> antes de continuar al ciclo TDD.
      </p>

      {specContent && (
        <div className="mb-3 p-2.5 rounded bg-background/80 border border-border/60 text-[11px] font-mono text-gray-300 max-h-24 overflow-y-auto whitespace-pre-wrap">
          {specContent.slice(0, 300)}...
        </div>
      )}

      {showRejectInput ? (
        <div className="space-y-2 mt-3">
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Indique los ajustes requeridos en la especificación..."
            rows={3}
            className="w-full bg-background border border-border rounded-lg p-2.5 text-xs text-gray-200 focus:outline-none focus:border-rose-500 font-mono"
          />
          <div className="flex items-center space-x-2 justify-end">
            <button
              onClick={() => setShowRejectInput(false)}
              className="px-3 py-1.5 rounded-md border border-border text-xs text-gray-300 hover:bg-card"
            >
              Cancelar
            </button>
            <button
              onClick={() => onReject(feedback)}
              className="px-3 py-1.5 rounded-md bg-rose-600 hover:bg-rose-500 text-xs font-semibold text-white flex items-center space-x-1.5 shadow"
            >
              <X size={14} />
              <span>Enviar Rechazo con Ajustes</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-center space-x-3 mt-3">
          <button
            onClick={onApprove}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white flex items-center space-x-2 shadow-md hover:shadow-emerald-600/20 transition cursor-pointer"
          >
            <Check size={16} />
            <span>Aprobar y Ejecutar Ciclo TDD (k-verifier)</span>
          </button>
          <button
            onClick={() => setShowRejectInput(true)}
            className="px-3.5 py-2 rounded-lg bg-card hover:bg-card/80 border border-border text-xs font-semibold text-gray-300 hover:text-white flex items-center space-x-1.5 transition cursor-pointer"
          >
            <X size={14} className="text-rose-400" />
            <span>Solicitar Ajustes</span>
          </button>
        </div>
      )}
    </div>
  );
};
