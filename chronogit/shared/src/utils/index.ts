/**
 * ChronoGit Shared Utilities
 */

export * from './types';
export * from './constants';

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Formats a git hash to short form (7 characters)
 */
export function shortenHash(hash: string): string {
  return hash.slice(0, 7);
}

/**
 * Formats a date to relative time string
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const then = new Date(date);
  const diffMs = now.getTime() - then.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);
  const diffYears = Math.floor(diffDays / 365);

  if (diffSecs < 60) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffWeeks < 4) return `${diffWeeks}w ago`;
  if (diffMonths < 12) return `${diffMonths}mo ago`;
  return `${diffYears}y ago`;
}

/**
 * Formats a number with K/M suffixes
 */
export function formatNumber(num: number): string {
  if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(1)}M`;
  }
  if (num >= 1_000) {
    return `${(num / 1_000).toFixed(1)}K`;
  }
  return num.toString();
}

/**
 * Formats file size in bytes to human readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

/**
 * Gets the language from a file path
 */
export function getLanguageFromPath(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase() || '';
  const languageMap: Record<string, string> = {
    ts: 'typescript',
    tsx: 'typescript',
    js: 'javascript',
    jsx: 'javascript',
    py: 'python',
    rb: 'ruby',
    rs: 'rust',
    go: 'go',
    java: 'java',
    cpp: 'cpp',
    c: 'c',
    h: 'c',
    hpp: 'cpp',
    cs: 'csharp',
    php: 'php',
    swift: 'swift',
    kt: 'kotlin',
    scala: 'scala',
    sh: 'shell',
    bash: 'shell',
    zsh: 'shell',
    yaml: 'yaml',
    yml: 'yaml',
    json: 'json',
    xml: 'xml',
    html: 'html',
    css: 'css',
    scss: 'scss',
    less: 'less',
    sql: 'sql',
    md: 'markdown',
    txt: 'plaintext',
  };
  return languageMap[ext] || 'plaintext';
}

/**
 * Gets the icon name for a file path
 */
export function getFileIcon(path: string): string {
  const fileName = path.split('/').pop()?.toLowerCase() || '';
  const ext = `.${path.split('.').pop()?.toLowerCase()}`;
  
  // Check for special filenames first
  const specialFiles: Record<string, string> = {
    'license': 'license',
    'readme': 'readme',
    'changelog': 'changelog',
    'contributing': 'contributing',
    'dockerfile': 'docker',
    'makefile': 'makefile',
    '.gitignore': 'git',
    '.gitattributes': 'git',
  };
  
  if (specialFiles[fileName]) {
    return specialFiles[fileName];
  }
  
  // Then check extensions
  const extIcons: Record<string, string> = {
    '.ts': 'typescript',
    '.tsx': 'react',
    '.js': 'javascript',
    '.jsx': 'react',
    '.py': 'python',
    '.rb': 'ruby',
    '.rs': 'rust',
    '.go': 'go',
    '.java': 'java',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.c': 'c',
    '.h': 'c',
    '.hpp': 'cpp',
    '.hxx': 'cpp',
    '.cs': 'csharp',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.scala': 'scala',
    '.sc': 'scala',
    '.sh': 'terminal',
    '.bash': 'terminal',
    '.zsh': 'terminal',
    '.fish': 'terminal',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'settings',
    '.json': 'json',
    '.jsonc': 'json',
    '.xml': 'xml',
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.scss': 'sass',
    '.sass': 'sass',
    '.less': 'less',
    '.vue': 'vue',
    '.svelte': 'svelte',
    '.sql': 'database',
    '.db': 'database',
    '.sqlite': 'database',
    '.md': 'markdown',
    '.mdx': 'markdown',
    '.txt': 'document',
    '.rst': 'document',
    '.pdf': 'document',
    '.png': 'image',
    '.jpg': 'image',
    '.jpeg': 'image',
    '.gif': 'image',
    '.svg': 'image',
    '.ico': 'image',
    '.webp': 'image',
    '.avif': 'image',
    '.mp4': 'video',
    '.webm': 'video',
    '.mov': 'video',
    '.avi': 'video',
    '.mp3': 'audio',
    '.wav': 'audio',
    '.ogg': 'audio',
    '.flac': 'audio',
  };
  
  return extIcons[ext] || 'file';
}

/**
 * Determines commit type from message
 */
export function getCommitType(message: string): string {
  const lowerMessage = message.toLowerCase();
  
  const patterns: [RegExp, string][] = [
    [/^merge /i, 'merge'],
    [/^revert /i, 'revert'],
    [/^(feat|feature)[:(]/i, 'feature'],
    [/^fix[:(]/i, 'fix'],
    [/^(docs|doc)[:(]/i, 'docs'],
    [/^style[:(]/i, 'style'],
    [/^(refactor|refactoring)[:(]/i, 'refactor'],
    [/^test[:(]/i, 'test'],
    [/^(chore|maintenance)[:(]/i, 'chore'],
    [/^perf[:(]/i, 'performance'],
    [/^ci[:(]/i, 'ci'],
    [/^build[:(]/i, 'build'],
  ];
  
  for (const [pattern, type] of patterns) {
    if (pattern.test(lowerMessage)) {
      return type;
    }
  }
  
  // Fallback heuristics
  if (lowerMessage.includes('merge')) return 'merge';
  if (lowerMessage.includes('revert')) return 'revert';
  if (lowerMessage.includes('fix') || lowerMessage.includes('bug')) return 'fix';
  if (lowerMessage.includes('doc') || lowerMessage.includes('readme')) return 'docs';
  if (lowerMessage.includes('test')) return 'test';
  if (lowerMessage.includes('refactor')) return 'refactor';
  
  return 'default';
}

/**
 * Calculates diff statistics
 */
export function calculateDiffStats(hunks: Array<{ lines: Array<{ type: string }> }>): {
  insertions: number;
  deletions: number;
  totalChanges: number;
} {
  let insertions = 0;
  let deletions = 0;
  
  for (const hunk of hunks) {
    for (const line of hunk.lines) {
      if (line.type === 'add') insertions++;
      if (line.type === 'delete') deletions++;
    }
  }
  
  return {
    insertions,
    deletions,
    totalChanges: insertions + deletions,
  };
}

/**
 * Creates a debounced function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Creates a throttled function
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Deep clones an object
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(item => deepClone(item)) as T;
  
  const cloned: Record<string, unknown> = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      cloned[key] = deepClone((obj as Record<string, unknown>)[key]);
    }
  }
  return cloned as T;
}

/**
 * Generates a unique ID
 */
export function generateId(prefix = ''): string {
  return `${prefix}${Date.now().toString(36)}${Math.random().toString(36).slice(2, 9)}`;
}

/**
 * Truncates text with ellipsis
 */
export function truncate(text: string, maxLength: number, ellipsis = '...'): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - ellipsis.length) + ellipsis;
}

/**
 * Escapes HTML special characters
 */
export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, char => map[char]);
}

/**
 * Parses a git remote URL
 */
export function parseRemoteUrl(url: string): {
  host?: string;
  owner?: string;
  repo?: string;
  protocol?: string;
} | null {
  try {
    // SSH format: git@github.com:owner/repo.git
    const sshMatch = url.match(/^git@([^:]+):([^/]+)\/([^/.]+)(?:\.git)?$/);
    if (sshMatch) {
      return {
        host: sshMatch[1],
        owner: sshMatch[2],
        repo: sshMatch[3],
        protocol: 'ssh',
      };
    }
    
    // HTTPS format: https://github.com/owner/repo.git
    const httpsMatch = url.match(/^https?:\/\/([^/]+)\/([^/]+)\/([^/.]+)(?:\.git)?$/);
    if (httpsMatch) {
      return {
        host: httpsMatch[1],
        owner: httpsMatch[2],
        repo: httpsMatch[3],
        protocol: 'https',
      };
    }
    
    return null;
  } catch {
    return null;
  }
}

/**
 * Groups items by a key function
 */
export function groupBy<T, K extends string>(
  items: T[],
  keyFn: (item: T) => K
): Record<K, T[]> {
  return items.reduce((acc, item) => {
    const key = keyFn(item);
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {} as Record<K, T[]>);
}

/**
 * Sorts an array by multiple keys
 */
export function sortBy<T>(
  items: T[],
  selectors: Array<(item: T) => unknown>,
  orders: Array<'asc' | 'desc'> = []
): T[] {
  return [...items].sort((a, b) => {
    for (let i = 0; i < selectors.length; i++) {
      const aVal = selectors[i](a);
      const bVal = selectors[i](b);
      const order = orders[i] || 'asc';
      
      if (aVal < bVal) return order === 'asc' ? -1 : 1;
      if (aVal > bVal) return order === 'asc' ? 1 : -1;
    }
    return 0;
  });
}

/**
 * Interpolates between two colors
 */
export function interpolateColor(color1: string, color2: string, factor: number): string {
  const hex2rgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16),
        }
      : { r: 0, g: 0, b: 0 };
  };
  
  const rgb2hex = (r: number, g: number, b: number) =>
    '#' +
    [r, g, b]
      .map(x => {
        const hex = Math.round(x).toString(16);
        return hex.length === 1 ? '0' + hex : hex;
      })
      .join('');
  
  const c1 = hex2rgb(color1);
  const c2 = hex2rgb(color2);
  
  const r = c1.r + (c2.r - c1.r) * factor;
  const g = c1.g + (c2.g - c1.g) * factor;
  const b = c1.b + (c2.b - c1.b) * factor;
  
  return rgb2hex(r, g, b);
}

/**
 * Creates a color scale based on value range
 */
export function createColorScale(
  min: number,
  max: number,
  colorStart: string,
  colorEnd: string
): (value: number) => string {
  return (value: number) => {
    const normalized = (value - min) / (max - min);
    return interpolateColor(colorStart, colorEnd, Math.max(0, Math.min(1, normalized)));
  };
}

/**
 * Safely parses JSON with error handling
 */
export function safeJsonParse<T>(json: string, fallback: T): T {
  try {
    return JSON.parse(json) as T;
  } catch {
    return fallback;
  }
}

/**
 * Checks if a value is defined (not null or undefined)
 */
export function isDefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

/**
 * Creates a promise that resolves after a delay
 */
export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retries a function with exponential backoff
 */
export async function retry<T>(
  fn: () => Promise<T>,
  options: {
    retries?: number;
    delay?: number;
    backoff?: number;
  } = {}
): Promise<T> {
  const { retries = 3, delay: baseDelay = 1000, backoff = 2 } = options;
  
  let lastError: Error;
  let currentDelay = baseDelay;
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (attempt < retries) {
        await delay(currentDelay);
        currentDelay *= backoff;
      }
    }
  }
  
  throw lastError!;
}
