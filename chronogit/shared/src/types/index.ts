/**
 * ChronoGit Shared Types
 * Common type definitions used across frontend and backend
 */

// ============================================================================
// Core Git Types
// ============================================================================

export interface Commit {
  hash: string;
  shortHash: string;
  message: string;
  body: string;
  author: Author;
  committer: Author;
  timestamp: string;
  parents: string[];
  branches: string[];
  tags: string[];
  stats: CommitStats;
  isMerge: boolean;
  aiSummary?: AISummary;
}

export interface Author {
  name: string;
  email: string;
  avatar?: string;
}

export interface CommitStats {
  insertions: number;
  deletions: number;
  filesChanged: number;
  totalLines: number;
}

export interface Branch {
  name: string;
  isCurrent: boolean;
  isRemote: boolean;
  headCommit: string;
  upstream?: string;
}

export interface Tag {
  name: string;
  commit: string;
  message?: string;
  tagger?: Author;
  timestamp?: string;
}

// ============================================================================
// File System Types
// ============================================================================

export interface FileNode {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  children?: FileNode[];
  status?: FileStatus;
  language?: string;
  icon?: string;
}

export type FileStatus = 
  | 'added'
  | 'modified'
  | 'deleted'
  | 'renamed'
  | 'copied'
  | 'untracked'
  | 'unchanged';

export interface FileContent {
  path: string;
  content: string;
  encoding: 'utf-8' | 'base64';
  size: number;
  language: string;
  lines: number;
  sha: string;
}

export interface FileDiff {
  path: string;
  oldPath?: string;
  status: FileStatus;
  hunks: DiffHunk[];
  insertions: number;
  deletions: number;
  binary?: boolean;
}

export interface DiffHunk {
  oldStart: number;
  oldLines: number;
  newStart: number;
  newLines: number;
  header: string;
  lines: DiffLine[];
}

export interface DiffLine {
  type: 'context' | 'add' | 'delete';
  content: string;
  lineNumber?: number;
  oldLineNumber?: number;
  newLineNumber?: number;
}

// ============================================================================
// Function-Level Analysis Types
// ============================================================================

export interface FunctionInfo {
  name: string;
  kind: 'function' | 'class' | 'method' | 'interface' | 'enum' | 'type' | 'variable' | 'import';
  signature: string;
  startLine: number;
  endLine: number;
  parameters?: ParameterInfo[];
  returnType?: string;
  accessModifier?: 'public' | 'private' | 'protected';
  isStatic?: boolean;
  isAsync?: boolean;
  docComment?: string;
  complexity?: number;
}

export interface ParameterInfo {
  name: string;
  type: string;
  optional?: boolean;
  defaultValue?: string;
}

export interface FunctionDiff {
  function: FunctionInfo;
  status: 'added' | 'removed' | 'modified' | 'renamed' | 'moved';
  oldFunction?: FunctionInfo;
  changes?: {
    added?: FunctionInfo[];
    removed?: FunctionInfo[];
    modified?: ModifiedFunction[];
  };
}

export interface ModifiedFunction {
  name: string;
  signatureChange?: {
    old: string;
    new: string;
  };
  parameterChanges?: {
    added?: ParameterInfo[];
    removed?: ParameterInfo[];
    modified?: ParameterInfo[];
  };
  bodyChanged: boolean;
  complexityChange?: number;
}

// ============================================================================
// AI Types
// ============================================================================

export interface AISummary {
  title: string;
  description: string;
  changes: string[];
  impact: string;
  confidence: number;
  model: string;
  generatedAt: string;
}

export interface BugAnalysis {
  likelyCommit: string;
  probability: number;
  reasoning: string;
  affectedFiles: string[];
  relatedCommits: string[];
  suggestedFix?: string;
  evidence: EvidenceItem[];
}

export interface EvidenceItem {
  type: 'code_change' | 'test_failure' | 'error_message' | 'pattern_match';
  description: string;
  relevance: number;
  location?: {
    file: string;
    line?: number;
  };
}

export interface ArchitectureExplanation {
  overview: string;
  components: ComponentInfo[];
  dependencies: DependencyInfo[];
  patterns: string[];
  suggestions: string[];
}

export interface ComponentInfo {
  name: string;
  type: string;
  responsibility: string;
  files: string[];
}

export interface DependencyInfo {
  from: string;
  to: string;
  type: 'import' | 'call' | 'inheritance' | 'composition';
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface ContributorStats {
  author: Author;
  commits: number;
  insertions: number;
  deletions: number;
  firstCommit: string;
  lastCommit: string;
  activeDays: number;
  languages: Record<string, number>;
  filesTouched: string[];
  ownershipMap: Record<string, number>;
  workingHours: HourlyActivity;
  averageCommitSize: number;
}

export interface HourlyActivity {
  hours: Record<number, number>;
  timezone?: string;
}

export interface HeatmapData {
  type: 'files' | 'folders' | 'functions' | 'authors';
  data: HeatmapEntry[];
  max: number;
  min: number;
}

export interface HeatmapEntry {
  path: string;
  value: number;
  metrics: {
    modifications: number;
    insertions: number;
    deletions: number;
    authors: number;
    complexity?: number;
  };
}

export interface RepositoryStats {
  totalCommits: number;
  totalFiles: number;
  totalDirectories: number;
  totalLines: number;
  firstCommit: string;
  lastCommit: string;
  age: number; // in days
  contributors: number;
  branches: number;
  tags: number;
  languages: LanguageStats[];
  locOverTime: TimeSeriesPoint[];
  commitFrequency: TimeSeriesPoint[];
  averageCommitSize: number;
  complexityMetrics: ComplexityMetrics;
}

export interface LanguageStats {
  name: string;
  files: number;
  lines: number;
  percentage: number;
  color: string;
}

export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface ComplexityMetrics {
  cyclomatic: number;
  cognitive: number;
  halstead?: {
    vocabulary: number;
    length: number;
    volume: number;
    difficulty: number;
    effort: number;
  };
  maintainabilityIndex: number;
}

// ============================================================================
// Timeline & Visualization Types
// ============================================================================

export interface TimelineNode {
  id: string;
  commit: Commit;
  x: number;
  y: number;
  z?: number;
  cluster?: string;
  color: string;
  size: number;
}

export interface TimelineEdge {
  source: string;
  target: string;
  type: 'parent' | 'merge' | 'cherry_pick';
  style?: Record<string, unknown>;
}

export interface ReplayState {
  isPlaying: boolean;
  currentCommit: string;
  speed: number;
  direction: 'forward' | 'backward';
  skipMerges: boolean;
  commitRange: [string, string];
}

export interface ViewportState {
  zoom: number;
  pan: { x: number; y: number };
  rotation?: { x: number; y: number; z: number };
  target?: string;
}

// ============================================================================
// Search Types
// ============================================================================

export interface SearchResult {
  type: 'commit' | 'file' | 'function' | 'author' | 'branch' | 'tag';
  id: string;
  title: string;
  subtitle?: string;
  path?: string;
  commit?: string;
  score: number;
  highlights?: Highlight[];
}

export interface Highlight {
  text: string;
  matched: boolean;
}

export interface SearchQuery {
  query: string;
  types: SearchResult['type'][];
  commitRange?: [string, string];
  authors?: string[];
  files?: string[];
  limit?: number;
  offset?: number;
}

// ============================================================================
// Graph & Architecture Types
// ============================================================================

export interface DependencyGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  clusters: GraphCluster[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'module' | 'file' | 'function' | 'class';
  size?: number;
  color?: string;
  data?: Record<string, unknown>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: 'imports' | 'calls' | 'extends' | 'implements' | 'uses';
  weight?: number;
  label?: string;
}

export interface GraphCluster {
  id: string;
  label: string;
  nodes: string[];
  color?: string;
}

export interface ArchitectureSnapshot {
  commit: string;
  timestamp: string;
  modules: ModuleInfo[];
  layers: LayerInfo[];
  cycles: CycleInfo[];
  deadCode: string[];
  metrics: ArchitectureMetrics;
}

export interface ModuleInfo {
  name: string;
  path: string;
  files: string[];
  dependencies: string[];
  dependents: string[];
  complexity: number;
}

export interface LayerInfo {
  name: string;
  modules: string[];
  description: string;
}

export interface CycleInfo {
  nodes: string[];
  severity: 'error' | 'warning' | 'info';
}

export interface ArchitectureMetrics {
  coupling: number;
  cohesion: number;
  instability: number;
  abstractness: number;
  distanceFromMainSequence: number;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface APIResponse<T> {
  data: T;
  meta?: {
    page?: number;
    pageSize?: number;
    total?: number;
    totalPages?: number;
  };
  error?: APIError;
}

export interface APIError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// ============================================================================
// Repository Management Types
// ============================================================================

export interface RepositoryInfo {
  id: string;
  name: string;
  path: string;
  remote?: string;
  HEAD: string;
  branch: string;
  indexedAt: string;
  lastOpened: string;
  size: number;
  commitCount: number;
  status: 'indexed' | 'indexing' | 'error';
  error?: string;
}

export interface RepositoryConfig {
  maxCommitsToIndex?: number;
  enableAI?: boolean;
  enableParsing?: boolean;
  excludedPaths?: string[];
  includedLanguages?: string[];
}

// ============================================================================
// WebSocket Message Types
// ============================================================================

export interface WSMessage {
  type: WSMessageType;
  payload: unknown;
  timestamp: string;
}

export type WSMessageType =
  | 'replay_update'
  | 'index_progress'
  | 'ai_complete'
  | 'search_results'
  | 'error';

export interface IndexProgress {
  phase: 'commits' | 'files' | 'parsing' | 'ai' | 'complete';
  progress: number;
  total: number;
  current?: string;
}
