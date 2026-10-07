import { Shield, GitBranch, RefreshCw } from 'lucide-react';
import { WorkspaceStatus } from '../types.ts';

interface HeaderProps {
  status: WorkspaceStatus | null;
  isConnected: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ status, isConnected, onRefresh }) => {
  return (
    <header className="h-12 bg-surface border-b border-border flex items-center justify-between px-4 select-none flex-shrink-0">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center justify-center w-7 h-7 rounded bg-brand-600 text-white font-bold text-sm tracking-wider shadow">
          K
        </div>
        <div className="flex flex-col">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-sm text-gray-100">k-method app</span>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-brand-600/30 text-indigo-300 border border-brand-500/40">
              v0 Studio
            </span>
          </div>
        </div>
      </div>

      {/* Middle status badges */}
      <div className="flex items-center space-x-3 text-xs">
        {/* Workspace Branch */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-card border border-border text-gray-300">
          <GitBranch size={13} className="text-gray-400" />
          <span className="font-mono">{status?.branch || 'main'}</span>
        </div>

        {/* Stash Shield */}
        <div className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md border text-xs font-medium ${
          status?.is_clean
            ? 'bg-emerald-950/40 border-emerald-700/60 text-emerald-400'
            : 'bg-amber-950/40 border-amber-700/60 text-amber-400'
        }`}>
          <Shield size={13} />
          <span>Stash Shield: {status?.is_clean ? 'Clean' : 'Dirty'}</span>
        </div>

        {/* WebSocket Connection */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-card border border-border text-xs">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
          <span className="text-gray-400 font-mono text-[11px]">{isConnected ? 'WS Connected' : 'Disconnected'}</span>
        </div>
      </div>

      {/* Right Action buttons */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onRefresh}
          className="p-1.5 rounded-md hover:bg-card border border-transparent hover:border-border text-gray-400 hover:text-gray-200 transition"
          title="Refresh Workspace Status"
        >
          <RefreshCw size={14} />
        </button>
      </div>
    </header>
  );
};
