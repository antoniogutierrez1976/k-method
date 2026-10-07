import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header.tsx';
import { Sidebar } from './components/Sidebar.tsx';
import { ChatCanvas } from './components/ChatCanvas.tsx';
import { AuxiliaryPane } from './components/AuxiliaryPane.tsx';
import { SkillModal } from './components/SkillModal.tsx';
import { 
  SDLCStage, 
  StepItem, 
  WorkspaceStatus, 
  EmbeddedSkill, 
  Message, 
  ArtifactFile 
} from './types.ts';

const API_BASE = 'http://127.0.0.1:8000';
const WS_BASE = 'ws://127.0.0.1:8000/ws/sdlc';

export const App: React.FC = () => {
  const [status, setStatus] = useState<WorkspaceStatus | null>(null);
  const [skills, setSkills] = useState<EmbeddedSkill[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('mock');
  const [selectedModel, setSelectedModel] = useState<string>('mock-model');
  const [isConnected, setIsConnected] = useState<boolean>(false);

  const [messages, setMessages] = useState<Message[]>([]);
  const [steps, setSteps] = useState<StepItem[]>([]);
  const [currentStage, setCurrentStage] = useState<SDLCStage>('IDLE');
  const [streamingToken, setStreamingToken] = useState<string>('');
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [approvalSpec, setApprovalSpec] = useState<string | null>(null);

  const [artifacts, setArtifacts] = useState<ArtifactFile[]>([]);
  const [activeArtifact, setActiveArtifact] = useState<string | null>(null);
  const [gitDiff, setGitDiff] = useState<string>('');
  const [tddLogs, setTddLogs] = useState<string>('');
  const [modalSkill, setModalSkill] = useState<EmbeddedSkill | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // 1. Fetch initial status, skills, diff, artifacts
  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/status`);
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
        if (data.active_provider) {
          setSelectedProvider(data.active_provider);
        }
      }
    } catch (e) {
      console.warn('Status fetch error:', e);
    }
  };

  const fetchSkills = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/skills`);
      if (res.ok) {
        const data = await res.json();
        setSkills(data.skills || []);
      }
    } catch (e) {
      console.warn('Skills fetch error:', e);
    }
  };

  const fetchDiff = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/diff`);
      if (res.ok) {
        const data = await res.json();
        setGitDiff(data.diff || '');
      }
    } catch (e) {
      console.warn('Diff fetch error:', e);
    }
  };

  const fetchArtifacts = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/artifacts`);
      if (res.ok) {
        const data = await res.json();
        if (data.artifacts && data.artifacts.length > 0) {
          setArtifacts(data.artifacts);
          const firstPath = data.artifacts[0].path;
          setActiveArtifact(firstPath);
          try {
            const cRes = await fetch(`${API_BASE}/api/artifact?path=${encodeURIComponent(firstPath)}`);
            if (cRes.ok) {
              const cData = await cRes.json();
              setArtifacts(prev => prev.map(a => a.path === firstPath ? { ...a, content: cData.content } : a));
            }
          } catch (err) {
            console.warn('First artifact content error:', err);
          }
        }
      }
    } catch (e) {
      console.warn('Artifacts fetch error:', e);
    }
  };

  const handleSelectArtifact = async (path: string) => {
    setActiveArtifact(path);
    const existing = artifacts.find(a => a.path === path);
    if (!existing || !existing.content) {
      try {
        const res = await fetch(`${API_BASE}/api/artifact?path=${encodeURIComponent(path)}`);
        if (res.ok) {
          const data = await res.json();
          setArtifacts(prev => prev.map(a => a.path === path ? { ...a, content: data.content } : a));
        }
      } catch (e) {
        console.warn('Failed to load artifact content:', e);
      }
    }
  };

  const refreshAll = () => {
    fetchStatus();
    fetchSkills();
    fetchDiff();
    fetchArtifacts();
  };

  // 2. Connect WebSocket
  const connectWebSocket = () => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      const socket = new WebSocket(WS_BASE);

      socket.onopen = () => {
        setIsConnected(true);
        console.log('[WebSocket] Connected to SDLC engine');
      };

      socket.onclose = () => {
        setIsConnected(false);
        console.log('[WebSocket] Disconnected. Reconnecting in 3s...');
        reconnectTimeoutRef.current = window.setTimeout(connectWebSocket, 3000);
      };

      socket.onerror = (err) => {
        console.warn('[WebSocket] Error:', err);
        socket.close();
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleServerEvent(data);
        } catch (e) {
          console.error('[WebSocket] Failed to parse message:', event.data, e);
        }
      };

      wsRef.current = socket;
    } catch (err) {
      console.error('[WebSocket] Setup failure:', err);
      reconnectTimeoutRef.current = window.setTimeout(connectWebSocket, 3000);
    }
  };

  // 3. Handle events from backend
  const handleServerEvent = (msg: any) => {
    const { event } = msg;

    if (event === 'stage_changed') {
      const stage: SDLCStage = msg.stage;
      setCurrentStage(stage);

      if (stage === 'SPEC') {
        const newStep: StepItem = {
          id: `step-${Date.now()}`,
          title: 'Fase 1: Especificación Formal Canónica (k-spec)',
          stage: 'SPEC',
          status: 'running',
          substeps: [
            'Analizando requerimientos y matriz de 6 ACs',
            'Inyectando directivas canónicas de Karpathy v0',
          ],
        };
        setSteps(prev => [...prev, newStep]);
      } else if (stage === 'VERIFIER_RED') {
        setSteps(prev => prev.map(s => s.status === 'running' ? { ...s, status: 'completed' } : s));
        const newStep: StepItem = {
          id: `step-${Date.now()}`,
          title: 'Fase 2: Verifier TDD - Ciclo Rojo (Fallo Inicial)',
          stage: 'VERIFIER_RED',
          status: 'running',
          substeps: ['Ejecutando suite para verificar ausencia de código'],
        };
        setSteps(prev => [...prev, newStep]);
      } else if (stage === 'VERIFIER_GREEN') {
        setSteps(prev => prev.map(s => s.status === 'running' ? { ...s, status: 'completed' } : s));
        const newStep: StepItem = {
          id: `step-${Date.now()}`,
          title: 'Fase 3: Verifier TDD - Ciclo Verde (Implementación)',
          stage: 'VERIFIER_GREEN',
          status: 'running',
          substeps: ['Compilando lógica mínima de paso y cobertura'],
        };
        setSteps(prev => [...prev, newStep]);
      } else if (stage === 'QUERY') {
        // Query stage
      }
    } else if (event === 'intent_discriminated') {
      setMessages(prev => [
        ...prev,
        {
          id: `msg-${Date.now()}`,
          sender: 'assistant',
          content: msg.message,
          timestamp: new Date().toLocaleTimeString(),
          intent: msg.intent,
        },
      ]);
    } else if (event === 'token') {
      setStreamingToken(prev => prev + msg.content);
    } else if (event === 'approval_required') {
      setApprovalSpec(msg.spec_content);
      // Also register as artifact
      const newArtifact: ArtifactFile = {
        name: 'spec.md',
        path: 'specs/spec.md',
        content: msg.spec_content,
      };
      setArtifacts(prev => [newArtifact, ...prev.filter(a => a.name !== 'spec.md')]);
      setActiveArtifact('specs/spec.md');
    } else if (event === 'tdd_output') {
      const outputText = `[Exit Code ${msg.returncode}]\n${msg.output}\n`;
      setTddLogs(prev => prev + outputText);
      setSteps(prev => prev.map(s => {
        if (s.status === 'running') {
          return {
            ...s,
            substeps: [...s.substeps, `TDD Run terminado con código ${msg.returncode}`],
            output: msg.output,
          };
        }
        return s;
      }));
    } else if (event === 'completed') {
      setIsExecuting(false);
      setCurrentStage('COMPLETED');
      setSteps(prev => prev.map(s => s.status === 'running' ? { ...s, status: 'completed' } : s));
      if (streamingToken) {
        setMessages(prev => [
          ...prev,
          {
            id: `msg-${Date.now()}`,
            sender: 'assistant',
            content: streamingToken,
            timestamp: new Date().toLocaleTimeString(),
          },
        ]);
        setStreamingToken('');
      }
      if (msg.pr_content) {
        const prArtifact: ArtifactFile = {
          name: 'PR-DESCRIPTION.md',
          path: 'specs/PR-DESCRIPTION.md',
          content: msg.pr_content,
        };
        setArtifacts(prev => [prArtifact, ...prev.filter(a => a.name !== 'PR-DESCRIPTION.md')]);
      }
      refreshAll();
    } else if (event === 'circuit_breaker') {
      setIsExecuting(false);
      setCurrentStage('CIRCUIT_BREAKER');
      setSteps(prev => prev.map(s => ({
        ...s,
        status: s.status === 'running' ? 'error' : s.status,
        substeps: [...s.substeps, 'Circuit Breaker activado (2 fallos idénticos)'],
      })));
      setTddLogs(prev => prev + `\n🛑 CIRCUIT BREAKER ACTIVATED:\n${msg.report}`);
    } else if (event === 'error') {
      setIsExecuting(false);
      setCurrentStage('ERROR');
      setMessages(prev => [
        ...prev,
        {
          id: `msg-${Date.now()}`,
          sender: 'assistant',
          content: `❌ Error: ${msg.message}`,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    }
  };

  // 4. Send Message / Trigger Task
  const handleSendMessage = (task: string) => {
    setMessages(prev => [
      ...prev,
      {
        id: `msg-${Date.now()}`,
        sender: 'user',
        content: task,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
    setIsExecuting(true);
    setStreamingToken('');
    setApprovalSpec(null);
    setSteps([]);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action: 'start',
        task,
        provider: selectedProvider,
        model: selectedModel,
      }));
    } else {
      setMessages(prev => [
        ...prev,
        {
          id: `msg-${Date.now()}`,
          sender: 'assistant',
          content: '⚠️ No se pudo conectar con el servidor WebSocket (127.0.0.1:8000).',
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
      setIsExecuting(false);
    }
  };

  // 5. Spec Approval responses
  const handleApproveSpec = () => {
    setApprovalSpec(null);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action: 'approval_response',
        approved: true,
      }));
    }
  };

  const handleRejectSpec = (feedback: string) => {
    setApprovalSpec(null);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action: 'approval_response',
        approved: false,
        feedback,
      }));
    }
  };

  // 6. Abort task
  const handleAbort = () => {
    setIsExecuting(false);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        action: 'abort',
      }));
    }
    setSteps(prev => prev.map(s => s.status === 'running' ? { ...s, status: 'error' } : s));
  };

  useEffect(() => {
    refreshAll();
    connectWebSocket();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-background text-gray-200">
      {/* Top Header */}
      <Header 
        status={status} 
        isConnected={isConnected} 
        onRefresh={refreshAll} 
      />

      {/* Main 3-Column Body Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Column: Sidebar */}
        <Sidebar
          status={status}
          skills={skills}
          selectedProvider={selectedProvider}
          onProviderChange={setSelectedProvider}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
          onSelectSkill={setModalSkill}
        />

        {/* Center Column: Chat Canvas */}
        <ChatCanvas
          messages={messages}
          steps={steps}
          currentStage={currentStage}
          streamingToken={streamingToken}
          isExecuting={isExecuting}
          approvalSpec={approvalSpec}
          onSendMessage={handleSendMessage}
          onApproveSpec={handleApproveSpec}
          onRejectSpec={handleRejectSpec}
          onAbort={handleAbort}
          provider={selectedProvider}
          model={selectedModel}
        />

        {/* Right Column: Auxiliary Pane */}
        <AuxiliaryPane
          artifacts={artifacts}
          activeArtifact={activeArtifact}
          onSelectArtifact={handleSelectArtifact}
          gitDiff={gitDiff}
          onRefreshDiff={fetchDiff}
          tddLogs={tddLogs}
        />
      </div>

      {/* Skill Directive Preview Modal */}
      <SkillModal
        skill={modalSkill}
        onClose={() => setModalSkill(null)}
      />
    </div>
  );
};

export default App;
