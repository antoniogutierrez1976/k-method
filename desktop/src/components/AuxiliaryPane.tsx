import React, { useState } from 'react';
import { 
  FileText, 
  GitCommit, 
  Terminal, 
  Network, 
  Copy, 
  Check, 
  RefreshCw 
} from 'lucide-react';
import { ArtifactFile } from '../types.ts';

interface AuxiliaryPaneProps {
  artifacts: ArtifactFile[];
  activeArtifact: string | null;
  onSelectArtifact: (path: string) => void;
  gitDiff: string;
  onRefreshDiff: () => void;
  tddLogs: string;
}

export const AuxiliaryPane: React.FC<AuxiliaryPaneProps> = ({
  artifacts,
  activeArtifact,
  onSelectArtifact,
  gitDiff,
  onRefreshDiff,
  tddLogs,
}) => {
  const [activeTab, setActiveTab] = useState<'artifacts' | 'diff' | 'tdd' | 'okf'>('artifacts');
  const [copied, setCopied] = useState(false);

  const selectedFile = artifacts.find(a => a.path === activeArtifact) || artifacts[0];

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const okfNodes = [
    { id: 'ADR-001', title: 'Arquitectura de 3 Capas de Karpathy', status: 'active', type: 'decision' },
    { id: 'ADR-002', title: 'Protocolo de Compuerta de Calidad Stash Shield', status: 'active', type: 'decision' },
    { id: 'ADR-003', title: 'Arnés de Ejecución de Doble SDK', status: 'active', type: 'decision' },
    { id: 'ADR-004', title: 'k-method app y Patrón de Skills Embebidas', status: 'active', type: 'decision' },
    { id: 'PAT-001', title: 'Circuit Breaker en Ciclo TDD', status: 'active', type: 'pattern' },
    { id: 'PAT-002', title: 'Inyección Canónica en System Prompt', status: 'active', type: 'pattern' },
  ];

  return (
    <div className="w-96 bg-surface border-l border-border flex flex-col h-full overflow-hidden select-none flex-shrink-0">
      {/* Tabs Header */}
      <div className="h-10 bg-card/60 border-b border-border flex items-center px-2 space-x-1 flex-shrink-0">
        <button
          onClick={() => setActiveTab('artifacts')}
          className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition ${
            activeTab === 'artifacts'
              ? 'bg-background text-brand-400 border border-border/80 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <FileText size={13} />
          <span>Artifacts</span>
        </button>

        <button
          onClick={() => setActiveTab('diff')}
          className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition ${
            activeTab === 'diff'
              ? 'bg-background text-brand-400 border border-border/80 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <GitCommit size={13} />
          <span>Files Changed</span>
        </button>

        <button
          onClick={() => setActiveTab('tdd')}
          className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition ${
            activeTab === 'tdd'
              ? 'bg-background text-brand-400 border border-border/80 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Terminal size={13} />
          <span>TDD Logs</span>
        </button>

        <button
          onClick={() => setActiveTab('okf')}
          className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition ${
            activeTab === 'okf'
              ? 'bg-background text-brand-400 border border-border/80 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Network size={13} />
          <span>OKF Graph</span>
        </button>
      </div>

      {/* Tab 1: Artifacts */}
      {activeTab === 'artifacts' && (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Artifact Selector Header */}
          <div className="p-2 border-b border-border bg-card/20 flex items-center justify-between">
            <div className="flex items-center space-x-2 overflow-x-auto text-xs font-mono">
              {artifacts.length === 0 ? (
                <span className="text-gray-500 italic">No artifacts generated yet</span>
              ) : (
                artifacts.map(a => (
                  <button
                    key={a.path}
                    onClick={() => onSelectArtifact(a.path)}
                    className={`px-2.5 py-1 rounded text-xs transition ${
                      selectedFile?.path === a.path
                        ? 'bg-brand-600/30 text-brand-300 border border-brand-500/40'
                        : 'text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    {a.name}
                  </button>
                ))
              )}
            </div>

            {selectedFile && (
              <button
                onClick={() => handleCopy(selectedFile.content)}
                className="p-1.5 rounded hover:bg-card text-gray-400 hover:text-gray-200"
                title="Copiar contenido"
              >
                {copied ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
              </button>
            )}
          </div>

          {/* Artifact Content Viewer */}
          <div className="flex-1 p-3 overflow-y-auto font-mono text-xs text-gray-300 bg-background whitespace-pre-wrap select-text leading-relaxed">
            {selectedFile ? selectedFile.content : '# Sin artefactos\n\nLos artefactos formales (spec.md, PR-DESCRIPTION.md) aparecerán aquí.'}
          </div>
        </div>
      )}

      {/* Tab 2: Files Changed / Diff */}
      {activeTab === 'diff' && (
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="p-2 border-b border-border bg-card/20 flex items-center justify-between">
            <span className="text-xs font-mono text-gray-400">git diff (working tree)</span>
            <button
              onClick={onRefreshDiff}
              className="p-1 rounded hover:bg-card text-gray-400 hover:text-gray-200"
              title="Refrescar Diff"
            >
              <RefreshCw size={13} />
            </button>
          </div>
          <div className="flex-1 p-3 overflow-y-auto font-mono text-xs bg-background select-text">
            {gitDiff ? (
              <div className="space-y-0.5">
                {gitDiff.split('\n').map((line, idx) => {
                  let color = 'text-gray-300';
                  let bg = 'transparent';
                  if (line.startsWith('+') && !line.startsWith('+++')) {
                    color = 'text-emerald-400';
                    bg = 'rgba(16, 185, 129, 0.08)';
                  } else if (line.startsWith('-') && !line.startsWith('---')) {
                    color = 'text-rose-400';
                    bg = 'rgba(244, 63, 94, 0.08)';
                  } else if (line.startsWith('@@')) {
                    color = 'text-cyan-400';
                  } else if (line.startsWith('diff --git')) {
                    color = 'text-amber-300 font-bold';
                  }
                  return (
                    <div key={idx} style={{ backgroundColor: bg }} className={`${color} whitespace-pre-wrap font-mono py-0.5 px-1`}>
                      {line}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8 italic">
                Working tree limpio. No hay cambios pendientes.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: TDD Console */}
      {activeTab === 'tdd' && (
        <div className="flex-1 flex flex-col overflow-hidden bg-background">
          <div className="p-2 border-b border-border bg-card/20 flex items-center justify-between">
            <span className="text-xs font-mono text-gray-400">Verifier Engine Output</span>
          </div>
          <div className="flex-1 p-3 overflow-y-auto font-mono text-xs text-gray-300 whitespace-pre-wrap select-text leading-relaxed">
            {tddLogs || 'Esperando inicio del ciclo TDD (k-verifier)...'}
          </div>
        </div>
      )}

      {/* Tab 4: OKF Graph */}
      {activeTab === 'okf' && (
        <div className="flex-1 flex flex-col overflow-hidden bg-background">
          <div className="p-2 border-b border-border bg-card/20 flex items-center justify-between">
            <span className="text-xs font-mono text-gray-400">OKF Wiki Nodes (9 activos)</span>
          </div>
          <div className="flex-1 p-3 overflow-y-auto space-y-2">
            {okfNodes.map(node => (
              <div key={node.id} className="p-2.5 rounded-lg bg-card/60 border border-border hover:border-brand-500/40 transition">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-xs text-brand-400 font-semibold">{node.id}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/40 uppercase">
                    {node.status}
                  </span>
                </div>
                <div className="text-xs text-gray-300 font-medium">{node.title}</div>
                <div className="text-[10px] text-gray-500 font-mono mt-1 capitalize">Tipo: {node.type}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
