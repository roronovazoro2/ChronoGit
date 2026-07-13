/**
 * ChronoGit Constants
 */

// ============================================================================
// API Endpoints
// ============================================================================

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Repository management
  REPOSITORIES: '/api/v1/repositories',
  REPOSITORY: (id: string) => `/api/v1/repositories/${id}`,
  REPOSITORY_IMPORT: '/api/v1/repositories/import',
  
  // Commits
  COMMITS: (repoId: string) => `/api/v1/repositories/${repoId}/commits`,
  COMMIT_DETAIL: (repoId: string, hash: string) => 
    `/api/v1/repositories/${repoId}/commits/${hash}`,
  
  // Files
  FILE_TREE: (repoId: string, commit?: string) => 
    `/api/v1/repositories/${repoId}/files${commit ? `?commit=${commit}` : ''}`,
  FILE_CONTENT: (repoId: string, path: string, commit?: string) => 
    `/api/v1/repositories/${repoId}/files/${encodeURIComponent(path)}${commit ? `?commit=${commit}` : ''}`,
  FILE_DIFF: (repoId: string, path: string, from: string, to: string) => 
    `/api/v1/repositories/${repoId}/files/${encodeURIComponent(path)}/diff?from=${from}&to=${to}`,
  
  // Timeline & Replay
  TIMELINE: (repoId: string) => `/api/v1/repositories/${repoId}/timeline`,
  REPLAY: (repoId: string) => `/api/v1/repositories/${repoId}/replay`,
  REPLAY_CONTROL: (repoId: string) => `/api/v1/repositories/${repoId}/replay/control`,
  
  // Analytics
  STATS: (repoId: string) => `/api/v1/repositories/${repoId}/stats`,
  CONTRIBUTORS: (repoId: string) => `/api/v1/repositories/${repoId}/contributors`,
  HEATMAP: (repoId: string) => `/api/v1/repositories/${repoId}/heatmap`,
  
  // Search
  SEARCH: (repoId: string) => `/api/v1/repositories/${repoId}/search`,
  
  // AI Features
  AI_SUMMARY: (repoId: string, hash: string) => 
    `/api/v1/repositories/${repoId}/ai/summary/${hash}`,
  BUG_ANALYSIS: (repoId: string) => `/api/v1/repositories/${repoId}/ai/bug-analysis`,
  ARCHITECTURE: (repoId: string, commit?: string) => 
    `/api/v1/repositories/${repoId}/ai/architecture${commit ? `?commit=${commit}` : ''}`,
  
  // Function-level analysis
  FUNCTIONS: (repoId: string, commit: string) => 
    `/api/v1/repositories/${repoId}/functions?commit=${commit}`,
  FUNCTION_DIFF: (repoId: string, from: string, to: string) => 
    `/api/v1/repositories/${repoId}/functions/diff?from=${from}&to=${to}`,
  
  // Graph & Architecture
  DEPENDENCY_GRAPH: (repoId: string, commit?: string) => 
    `/api/v1/repositories/${repoId}/graph${commit ? `?commit=${commit}` : ''}`,
  ARCHITECTURE_SNAPSHOT: (repoId: string, commit: string) => 
    `/api/v1/repositories/${repoId}/architecture/${commit}`,
  
  // Branches & Tags
  BRANCHES: (repoId: string) => `/api/v1/repositories/${repoId}/branches`,
  TAGS: (repoId: string) => `/api/v1/repositories/${repoId}/tags`,
} as const;

// ============================================================================
// UI Constants
// ============================================================================

export const COLORS = {
  // Brand colors
  PRIMARY: '#6366f1',
  PRIMARY_HOVER: '#4f46e5',
  SECONDARY: '#8b5cf6',
  ACCENT: '#06b6d4',
  
  // Status colors
  SUCCESS: '#22c55e',
  WARNING: '#f59e0b',
  ERROR: '#ef4444',
  INFO: '#3b82f6',
  
  // Git operation colors
  ADDED: '#22c55e',
  MODIFIED: '#3b82f6',
  DELETED: '#ef4444',
  RENAMED: '#f59e0b',
  
  // Commit type colors
  FEATURE: '#6366f1',
  FIX: '#22c55e',
  DOCS: '#f59e0b',
  STYLE: '#ec4899',
  REFACTOR: '#8b5cf6',
  TEST: '#06b6d4',
  CHORE: '#6b7280',
  MERGE: '#9ca3af',
  REVERT: '#ef4444',
  
  // Background colors
  BG_PRIMARY: '#0f0f0f',
  BG_SECONDARY: '#1a1a1a',
  BG_TERTIARY: '#262626',
  BG_ELEVATED: '#333333',
  
  // Text colors
  TEXT_PRIMARY: '#ffffff',
  TEXT_SECONDARY: '#a1a1aa',
  TEXT_MUTED: '#71717a',
  
  // Border colors
  BORDER_SUBTLE: '#27272a',
  BORDER_DEFAULT: '#3f3f46',
  BORDER_FOCUS: '#6366f1',
} as const;

export const ANIMATION_DURATIONS = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
  VERY_SLOW: 800,
} as const;

export const TRANSITION_EASINGS = {
  EASE_OUT: 'cubic-bezier(0.33, 1, 0.68, 1)',
  EASE_IN_OUT: 'cubic-bezier(0.65, 0, 0.35, 1)',
  SPRING: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
} as const;

// ============================================================================
// Timeline Constants
// ============================================================================

export const TIMELINE_CONFIG = {
  MIN_ZOOM: 0.1,
  MAX_ZOOM: 10,
  INITIAL_ZOOM: 1,
  NODE_SIZE_BASE: 8,
  NODE_SIZE_MAX: 24,
  CLUSTER_PADDING: 40,
  ANIMATION_DURATION: 600,
  REPLAY_DEFAULT_SPEED: 500, // ms per commit
  REPLAY_MIN_SPEED: 50,
  REPLAY_MAX_SPEED: 2000,
} as const;

export const COMMIT_COLORS = {
  feature: COLORS.FEATURE,
  fix: COLORS.FIX,
  docs: COLORS.DOCS,
  style: COLORS.STYLE,
  refactor: COLORS.REFACTOR,
  test: COLORS.TEST,
  chore: COLORS.CHORE,
  merge: COLORS.MERGE,
  revert: COLORS.REVERT,
  default: COLORS.INFO,
} as const;

// ============================================================================
// Editor Constants
// ============================================================================

export const EDITOR_CONFIG = {
  MIN_FONT_SIZE: 10,
  MAX_FONT_SIZE: 24,
  DEFAULT_FONT_SIZE: 14,
  TAB_SIZE: 2,
  MINIMAP_ENABLED: true,
  WORD_WRAP: 'off' as const,
  SCROLL_BEYOND_LAST_LINE: true,
  SMOOTH_SCROLLING: true,
  CURSOR_BLINKING: 'smooth' as const,
  FONT_FAMILY: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
} as const;

export const SUPPORTED_LANGUAGES = [
  'typescript', 'javascript', 'python', 'java', 'go', 'rust',
  'cpp', 'c', 'csharp', 'ruby', 'php', 'swift', 'kotlin',
  'scala', 'shellscript', 'yaml', 'json', 'xml', 'html',
  'css', 'scss', 'less', 'sql', 'markdown', 'plaintext',
] as const;

// ============================================================================
// Performance Constants
// ============================================================================

export const PERFORMANCE_CONFIG = {
  MAX_VISIBLE_COMMITS: 500,
  VIRTUAL_SCROLL_OVERSCAN: 20,
  DEBOUNCE_DELAY: 300,
  THROTTLE_DELAY: 100,
  CACHE_TIME: 5 * 60 * 1000, // 5 minutes
  STALE_TIME: 30 * 1000, // 30 seconds
  MAX_CONCURRENT_REQUESTS: 5,
  RETRY_COUNT: 3,
  RETRY_DELAY: 1000,
} as const;

// ============================================================================
// File Type Icons
// ============================================================================

export const FILE_ICONS: Record<string, string> = {
  // Languages
  '.ts': 'typescript',
  '.tsx': 'react',
  '.js': 'javascript',
  '.jsx': 'react',
  '.py': 'python',
  '.java': 'java',
  '.go': 'go',
  '.rs': 'rust',
  '.rb': 'ruby',
  '.php': 'php',
  '.swift': 'swift',
  '.kt': 'kotlin',
  '.scala': 'scala',
  '.cs': 'csharp',
  '.cpp': 'cpp',
  '.c': 'c',
  '.h': 'c',
  '.hpp': 'cpp',
  
  // Config files
  '.json': 'json',
  '.yaml': 'yaml',
  '.yml': 'yaml',
  '.toml': 'settings',
  '.ini': 'settings',
  '.env': 'settings',
  '.config': 'settings',
  
  // Documentation
  '.md': 'markdown',
  '.mdx': 'markdown',
  '.rst': 'document',
  '.txt': 'document',
  
  // Web
  '.html': 'html',
  '.css': 'css',
  '.scss': 'sass',
  '.less': 'less',
  '.vue': 'vue',
  '.svelte': 'svelte',
  
  // Database
  '.sql': 'database',
  '.db': 'database',
  '.sqlite': 'database',
  
  // Images
  '.png': 'image',
  '.jpg': 'image',
  '.jpeg': 'image',
  '.gif': 'image',
  '.svg': 'image',
  '.ico': 'image',
  '.webp': 'image',
  
  // Other
  '.gitignore': 'git',
  '.gitattributes': 'git',
  'LICENSE': 'license',
  'README': 'readme',
  'CHANGELOG': 'changelog',
  'CONTRIBUTING': 'contributing',
  'Dockerfile': 'docker',
  'docker-compose.yml': 'docker',
  'Makefile': 'makefile',
  '.sh': 'terminal',
  '.bash': 'terminal',
  '.zsh': 'terminal',
};

// ============================================================================
// Keyboard Shortcuts
// ============================================================================

export const KEYBOARD_SHORTCUTS = {
  // Navigation
  GO_TO_FILE: 'Ctrl+P',
  GO_TO_COMMIT: 'Ctrl+K',
  GO_TO_NEXT_COMMIT: 'Ctrl+]',
  GO_TO_PREV_COMMIT: 'Ctrl+[',
  ZOOM_IN: 'Ctrl+=',
  ZOOM_OUT: 'Ctrl+-',
  RESET_VIEW: 'Ctrl+0',
  
  // Playback
  PLAY_PAUSE: 'Space',
  SPEED_UP: 'Shift+ArrowUp',
  SLOW_DOWN: 'Shift+ArrowDown',
  TOGGLE_DIRECTION: 'R',
  
  // Search
  GLOBAL_SEARCH: 'Ctrl+Shift+F',
  FILTER_COMMITS: 'Ctrl+F',
  
  // View
  TOGGLE_SIDEBAR: 'Ctrl+B',
  TOGGLE_PANEL: 'Ctrl+\\',
  FULLSCREEN: 'F11',
  
  // Editor
  SAVE: 'Ctrl+S',
  UNDO: 'Ctrl+Z',
  REDO: 'Ctrl+Shift+Z',
  FIND: 'Ctrl+F',
  REPLACE: 'Ctrl+H',
} as const;

// ============================================================================
// Error Messages
// ============================================================================

export const ERROR_MESSAGES = {
  REPOSITORY_NOT_FOUND: 'Repository not found',
  INVALID_COMMIT_HASH: 'Invalid commit hash',
  FILE_NOT_FOUND: 'File not found at this commit',
  INDEXING_FAILED: 'Failed to index repository',
  AI_UNAVAILABLE: 'AI service is unavailable',
  RATE_LIMIT_EXCEEDED: 'Rate limit exceeded. Please try again later.',
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNKNOWN_ERROR: 'An unexpected error occurred',
} as const;

// ============================================================================
// Local Storage Keys
// ============================================================================

export const STORAGE_KEYS = {
  THEME: 'chronogit:theme',
  PREFERENCES: 'chronogit:preferences',
  RECENT_REPOSITORIES: 'chronogit:recent-repos',
  PINNED_REPOSITORIES: 'chronogit:pinned-repos',
  VIEW_STATE: 'chronogit:view-state',
  REPLAY_STATE: 'chronogit:replay-state',
} as const;

// ============================================================================
// Default Preferences
// ============================================================================

export const DEFAULT_PREFERENCES = {
  theme: 'dark',
  editorFontSize: EDITOR_CONFIG.DEFAULT_FONT_SIZE,
  timelineDensity: 'medium',
  showCommitAuthors: true,
  showBranchLabels: true,
  enableAnimations: true,
  replaySpeed: 500,
  autoPlayOnLoad: false,
  confirmBeforeReplay: true,
  showMinimap: true,
  wordWrap: false,
  renderWhitespace: 'selection',
} as const;
