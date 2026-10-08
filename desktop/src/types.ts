export type SDLCStage =
  | 'IDLE'
  | 'TRIAGE'
  | 'SPEC'
  | 'STASH_SHIELD'
  | 'VERIFIER_RED'
  | 'VERIFIER_GREEN'
  | 'CIRCUIT_BREAKER'
  | 'OKF_LINT'
  | 'PR_GENERATED'
  | 'COMPLETED'
  | 'ERROR'
  | 'QUERY';

export interface StepItem {
  id: string;
  title: string;
  stage: SDLCStage;
  status: 'pending' | 'running' | 'completed' | 'error';
  substeps: string[];
  output?: string;
  startedAt?: Date;
  finishedAt?: Date;
}

export interface ModelInfo {
  id: string;
  name: string;
  default?: boolean;
  source?: string;
}

export interface WorkspaceStatus {
  workspace: string;
  branch: string;
  is_clean: boolean;
  provider_default?: string;
  active_provider?: string;
  available_providers?: string[];
  models?: Record<string, ModelInfo[]>;
}

export interface EmbeddedSkill {
  name: string;
  version: string;
  layer: string;
  description: string;
  directive: string;
}

export interface Message {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  intent?: string;
  stage?: SDLCStage;
}

export interface ArtifactFile {
  name: string;
  path: string;
  content: string;
}
