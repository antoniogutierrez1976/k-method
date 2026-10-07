import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Square, 
  Sparkles, 
  Bot, 
  User, 
  ChevronRight,
  Flame,
  HelpCircle,
  Compass
} from 'lucide-react';
import { Message, SDLCStage, StepItem } from '../types.ts';
import { StepCard } from './StepCard.tsx';
import { ApprovalModal } from './ApprovalModal.tsx';

interface ChatCanvasProps {
  messages: Message[];
  steps: StepItem[];
  currentStage: SDLCStage;
  streamingToken: string;
  isExecuting: boolean;
  approvalSpec: string | null;
  onSendMessage: (task: string) => void;
  onApproveSpec: () => void;
  onRejectSpec: (feedback: string) => void;
  onAbort: () => void;
  provider: string;
  model: string;
}

export const ChatCanvas: React.FC<ChatCanvasProps> = ({
  messages,
  steps,
  currentStage,
  streamingToken,
  isExecuting,
  approvalSpec,
  onSendMessage,
  onApproveSpec,
  onRejectSpec,
  onAbort,
  provider,
  model,
}) => {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, steps, streamingToken, approvalSpec]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isExecuting) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const getStageTitle = (stage: SDLCStage) => {
    switch (stage) {
      case 'SPEC': return 'Fase 1: Especificación Formal Canónica (k-spec)';
      case 'VERIFIER_RED': return 'Fase 2: Verifier TDD - Ciclo Rojo';
      case 'VERIFIER_GREEN': return 'Fase 3: Verifier TDD - Ciclo Verde';
      case 'OKF_LINT': return 'Fase 4: Verificación Grafo OKF';
      case 'PR_GENERATED': return 'Fase 5: Pull Request & Cierre';
      case 'QUERY': return 'Consulta Informativa / Asistencia';
      default: return 'Listo';
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-background overflow-hidden relative">
      {/* Breadcrumbs Bar */}
      <div className="h-9 px-4 border-b border-border/60 bg-surface/50 flex items-center justify-between text-xs text-gray-400 select-none flex-shrink-0">
        <div className="flex items-center space-x-1.5 font-mono">
          <span className="text-gray-300">k-method</span>
          <ChevronRight size={13} className="text-gray-600" />
          <span className="text-gray-400">main</span>
          <ChevronRight size={13} className="text-gray-600" />
          <span className="text-brand-400 font-semibold">{getStageTitle(currentStage)}</span>
        </div>

        {isExecuting && (
          <div className="flex items-center space-x-1.5 text-brand-400 animate-pulse">
            <Sparkles size={13} />
            <span className="text-[11px] font-mono">Motor en progreso...</span>
          </div>
        )}
      </div>

      {/* Message and Steps Stream */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && steps.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 select-none opacity-80">
            <div className="w-14 h-14 rounded-2xl bg-card border border-border flex items-center justify-center text-brand-500 mb-4 shadow-lg">
              <Compass size={28} />
            </div>
            <h2 className="text-base font-semibold text-gray-100 mb-1">k-method Studio</h2>
            <p className="text-xs text-gray-400 max-w-md leading-relaxed mb-4">
              Arnés de desarrollo de software agentico gobernado por la metodología de 3 capas de Karpathy v0.
            </p>
            <div className="grid grid-cols-2 gap-2 text-left max-w-lg text-xs font-mono">
              <div 
                onClick={() => setInput("Explicar la arquitectura de 3 capas")}
                className="p-2.5 rounded-lg bg-card/60 border border-border/60 hover:border-brand-500/40 cursor-pointer text-gray-300 hover:text-white transition"
              >
                <div className="flex items-center space-x-1.5 text-brand-400 font-bold mb-1">
                  <HelpCircle size={13} />
                  <span>Consulta</span>
                </div>
                <span>"Explicar la arquitectura de 3 capas"</span>
              </div>
              <div 
                onClick={() => setInput("Implementar endpoint para exportar métricas en JSON")}
                className="p-2.5 rounded-lg bg-card/60 border border-border/60 hover:border-brand-500/40 cursor-pointer text-gray-300 hover:text-white transition"
              >
                <div className="flex items-center space-x-1.5 text-emerald-400 font-bold mb-1">
                  <Flame size={13} />
                  <span>Feature SDLC</span>
                </div>
                <span>"Implementar endpoint para métricas"</span>
              </div>
            </div>
          </div>
        )}

        {/* Render Conversation Messages & Steps */}
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={`flex items-start space-x-3 text-xs leading-relaxed ${
              msg.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {msg.sender !== 'user' && (
              <div className="w-6 h-6 rounded bg-brand-600/30 border border-brand-500/40 flex items-center justify-center text-brand-300 flex-shrink-0 mt-0.5">
                <Bot size={14} />
              </div>
            )}

            <div 
              className={`max-w-[85%] rounded-xl px-4 py-3 shadow-sm ${
                msg.sender === 'user' 
                  ? 'bg-brand-600 text-white font-medium ml-12' 
                  : 'bg-card border border-border text-gray-200 mr-12'
              }`}
            >
              {msg.intent && (
                <div className="mb-1.5">
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-surface border border-border text-brand-300 font-semibold">
                    Intención: {msg.intent}
                  </span>
                </div>
              )}
              <div className="whitespace-pre-wrap font-sans">{msg.content}</div>
            </div>

            {msg.sender === 'user' && (
              <div className="w-6 h-6 rounded bg-gray-700 border border-gray-600 flex items-center justify-center text-gray-200 flex-shrink-0 mt-0.5">
                <User size={14} />
              </div>
            )}
          </div>
        ))}

        {/* Step Cards Progress */}
        {steps.map((step) => (
          <StepCard key={step.id} step={step} />
        ))}

        {/* Human In The Loop Approval Modal */}
        {approvalSpec && (
          <ApprovalModal
            specContent={approvalSpec}
            onApprove={onApproveSpec}
            onReject={onRejectSpec}
          />
        )}

        {/* Live Streaming Token output */}
        {streamingToken && (
          <div className="p-3 rounded-lg bg-card/80 border border-brand-500/30 text-xs text-gray-200 font-mono whitespace-pre-wrap leading-relaxed">
            {streamingToken}
            <span className="inline-block w-1.5 h-3.5 bg-brand-400 ml-1 animate-pulse" />
          </div>
        )}
      </div>

      {/* Floating Bottom Prompt Bar */}
      <div className="p-3 border-t border-border bg-surface/80 backdrop-blur flex-shrink-0">
        <form onSubmit={handleSubmit} className="flex flex-col space-y-2">
          <div className="flex items-center justify-between px-1 text-[11px] text-gray-400 font-mono">
            <span className="flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-brand-500" />
              <span>{provider} ({model})</span>
            </span>
            <span>Shift+Enter para nueva línea</span>
          </div>

          <div className="flex items-end space-x-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describa una tarea, requerimiento, bugfix o consulta..."
              rows={2}
              disabled={isExecuting}
              className="flex-1 bg-background border border-border rounded-xl px-3.5 py-2.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-brand-500 transition resize-none disabled:opacity-50"
            />

            {isExecuting ? (
              <button
                type="button"
                onClick={onAbort}
                className="p-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium shadow-md transition flex items-center justify-center cursor-pointer"
                title="Abortar Ejecución (/task-abort)"
              >
                <Square size={16} />
              </button>
            ) : (
              <button
                type="submit"
                disabled={!input.trim()}
                className="p-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium shadow-md transition flex items-center justify-center disabled:opacity-40 disabled:hover:bg-brand-600 cursor-pointer"
                title="Ejecutar Tarea"
              >
                <Send size={16} />
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};
