import React, { useState } from 'react';
import { 
  FolderTree, 
  Cpu, 
  Layers, 
  Folder, 
  ChevronRight, 
  ChevronDown, 
  FileCode, 
  BookOpen, 
  Box
} from 'lucide-react';
import { EmbeddedSkill, WorkspaceStatus, ModelInfo } from '../types.ts';

interface SidebarProps {
  status: WorkspaceStatus | null;
  skills: EmbeddedSkill[];
  availableModels?: Record<string, ModelInfo[]>;
  selectedProvider: string;
  onProviderChange: (p: string) => void;
  selectedModel: string;
  onModelChange: (m: string) => void;
  onSelectSkill: (skill: EmbeddedSkill) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  status,
  skills,
  availableModels,
  selectedProvider,
  onProviderChange,
  selectedModel,
  onModelChange,
  onSelectSkill,
}) => {
  const [customMode, setCustomMode] = useState<boolean>(false);
  const currentModels = (availableModels && availableModels[selectedProvider]) || [];
  const [expandedFolders, setExpandedFolders] = useState<Record<string, boolean>>({
    'workspace': true,
    'skills': true,
  });

  const toggleFolder = (key: string) => {
    setExpandedFolders(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <aside className="w-72 bg-surface border-r border-border flex flex-col h-full overflow-hidden select-none flex-shrink-0">
      {/* Workspace Folders Section */}
      <div className="p-3 border-b border-border flex-shrink-0">
        <div 
          onClick={() => toggleFolder('workspace')}
          className="flex items-center justify-between text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 cursor-pointer hover:text-gray-200"
        >
          <div className="flex items-center space-x-1.5">
            <FolderTree size={14} className="text-brand-500" />
            <span>Workspace</span>
          </div>
          {expandedFolders['workspace'] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </div>

        {expandedFolders['workspace'] && (
          <div className="space-y-1 text-xs font-mono">
            <div className="flex items-center space-x-2 px-2 py-1.5 rounded bg-card/60 text-gray-200 border border-border/50">
              <Folder size={13} className="text-amber-400" />
              <span className="truncate font-semibold">{status?.workspace || 'k-method'} (root)</span>
            </div>
            <div className="flex items-center space-x-2 px-2 py-1.5 rounded hover:bg-card/40 text-gray-400 hover:text-gray-200 transition pl-4">
              <FileCode size={13} className="text-blue-400" />
              <span>specs/ (Karpathy Layer 1)</span>
            </div>
            <div className="flex items-center space-x-2 px-2 py-1.5 rounded hover:bg-card/40 text-gray-400 hover:text-gray-200 transition pl-4">
              <BookOpen size={13} className="text-emerald-400" />
              <span>knowledge-base/ (OKF Wiki)</span>
            </div>
            <div className="flex items-center space-x-2 px-2 py-1.5 rounded hover:bg-card/40 text-gray-400 hover:text-gray-200 transition pl-4">
              <Layers size={13} className="text-purple-400" />
              <span>.agents/skills/ (Karpathy v0)</span>
            </div>
          </div>
        )}
      </div>

      {/* Provider & Model Selector */}
      <div className="p-3 border-b border-border flex-shrink-0 bg-card/30">
        <div className="flex items-center space-x-1.5 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
          <Cpu size={14} className="text-brand-500" />
          <span>LLM Engine Provider</span>
        </div>

        <div className="space-y-2 text-xs">
          <div>
            <label className="block text-[11px] text-gray-400 mb-1">Provider Adapter</label>
            <select
              value={selectedProvider}
              onChange={(e) => onProviderChange(e.target.value)}
              className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-gray-200 focus:outline-none focus:border-brand-500 font-mono text-xs"
            >
              <option value="copilot">GitHub Copilot SDK</option>
              <option value="antigravity">Google GenAI SDK</option>
              <option value="mock">Deterministic Mock Runner</option>
            </select>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-[11px] text-gray-400">Execution Model</label>
              {currentModels.length > 0 && (
                <button
                  type="button"
                  onClick={() => setCustomMode(prev => !prev)}
                  className="text-[10px] text-brand-400 hover:text-brand-300 font-sans cursor-pointer transition"
                >
                  {customMode ? 'Elegir del SDK' : 'Personalizado...'}
                </button>
              )}
            </div>

            {currentModels.length > 0 && !customMode ? (
              <select
                value={selectedModel}
                onChange={(e) => {
                  if (e.target.value === '__custom__') {
                    setCustomMode(true);
                  } else {
                    onModelChange(e.target.value);
                  }
                }}
                className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-gray-200 focus:outline-none focus:border-brand-500 font-mono text-xs"
              >
                {selectedModel && !currentModels.some(m => m.id === selectedModel) && (
                  <option value={selectedModel}>
                    {selectedModel} (Personalizado)
                  </option>
                )}
                {currentModels.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name || m.id} {m.default ? '★' : ''}
                  </option>
                ))}
                <option value="__custom__">✏️ Personalizado (escribir a mano)...</option>
              </select>
            ) : (
              <div className="space-y-1">
                <input
                  type="text"
                  value={selectedModel}
                  onChange={(e) => onModelChange(e.target.value)}
                  placeholder="e.g. gpt-4o, gemini-2.5-pro, mock"
                  className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-gray-200 focus:outline-none focus:border-brand-500 font-mono text-xs"
                />
                {customMode && (
                  <div className="text-[10px] text-gray-400 flex items-center justify-between">
                    <span>Identificador libre del modelo</span>
                    <button
                      type="button"
                      onClick={() => setCustomMode(false)}
                      className="text-brand-400 hover:text-brand-300 underline"
                    >
                      Volver al SDK
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Embedded Skills Section */}
      <div className="flex-1 overflow-y-auto p-3">
        <div 
          onClick={() => toggleFolder('skills')}
          className="flex items-center justify-between text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 cursor-pointer hover:text-gray-200"
        >
          <div className="flex items-center space-x-1.5">
            <Layers size={14} className="text-brand-500" />
            <span>Embedded Skills (v0)</span>
          </div>
          {expandedFolders['skills'] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </div>

        {expandedFolders['skills'] && (
          <div className="space-y-1.5">
            {skills.map((skill) => (
              <div
                key={skill.name}
                onClick={() => onSelectSkill(skill)}
                className="p-2 rounded-md bg-card/40 hover:bg-card border border-border/40 hover:border-brand-500/40 cursor-pointer transition group"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-semibold text-gray-200 group-hover:text-brand-400">
                    {skill.name}
                  </span>
                  <span className="text-[10px] px-1 py-0.2 rounded bg-surface border border-border text-gray-400 font-mono">
                    v0
                  </span>
                </div>
                <div className="text-[11px] text-gray-400 mt-1 line-clamp-2">
                  {skill.description}
                </div>
                <div className="mt-1 flex items-center text-[10px] text-indigo-400 font-medium">
                  <span>{skill.layer}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Footer Details */}
      <div className="p-3 border-t border-border bg-surface text-[11px] text-gray-400 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-1.5">
          <Box size={13} className="text-brand-500" />
          <span>k-method Studio</span>
        </div>
        <span className="font-mono text-[10px] text-gray-400">Karpathy v0</span>
      </div>
    </aside>
  );
};
