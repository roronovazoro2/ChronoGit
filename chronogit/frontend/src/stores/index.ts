import { create } from 'zustand'
import type { RepositoryInfo, ReplayState, ViewportState } from '@chronogit/shared'

// ============================================================================
// Application Store
// ============================================================================

interface AppState {
  // Current repository
  currentRepository: RepositoryInfo | null
  
  // Actions
  setCurrentRepository: (repo: RepositoryInfo | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  currentRepository: null,
  
  setCurrentRepository: (repo) => set({ currentRepository: repo }),
}))

// ============================================================================
// Replay Store
// ============================================================================

interface ReplayStore {
  state: ReplayState
  
  // Actions
  setIsPlaying: (playing: boolean) => void
  setCurrentCommit: (commit: string) => void
  setSpeed: (speed: number) => void
  setDirection: (direction: 'forward' | 'backward') => void
  setSkipMerges: (skip: boolean) => void
  play: () => void
  pause: () => void
  stop: () => void
  next: () => void
  prev: () => void
  jumpTo: (commit: string) => void
}

const defaultReplayState: ReplayState = {
  isPlaying: false,
  currentCommit: '',
  speed: 500,
  direction: 'forward',
  skipMerges: false,
  commitRange: ['', ''],
}

export const useReplayStore = create<ReplayStore>((set, get) => ({
  state: defaultReplayState,
  
  setIsPlaying: (playing) => 
    set((state) => ({ state: { ...state.state, isPlaying: playing } })),
  
  setCurrentCommit: (commit) => 
    set((state) => ({ state: { ...state.state, currentCommit: commit } })),
  
  setSpeed: (speed) => 
    set((state) => ({ state: { ...state.state, speed } })),
  
  setDirection: (direction) => 
    set((state) => ({ state: { ...state.state, direction } })),
  
  setSkipMerges: (skip) => 
    set((state) => ({ state: { ...state.state, skipMerges: skip } })),
  
  play: () => set((state) => ({ state: { ...state.state, isPlaying: true } })),
  pause: () => set((state) => ({ state: { ...state.state, isPlaying: false } })),
  stop: () => set((state) => ({ state: { ...state.state, isPlaying: false, currentCommit: '' } })),
  
  next: () => {
    // Would be implemented with actual commit navigation
    console.log('Next commit')
  },
  
  prev: () => {
    // Would be implemented with actual commit navigation
    console.log('Previous commit')
  },
  
  jumpTo: (commit) => 
    set((state) => ({ state: { ...state.state, currentCommit: commit, isPlaying: false } })),
}))

// ============================================================================
// Viewport Store
// ============================================================================

interface ViewportStore {
  state: ViewportState
  
  // Actions
  setZoom: (zoom: number) => void
  setPan: (pan: { x: number; y: number }) => void
  setRotation: (rotation: { x: number; y: number; z: number }) => void
  setTarget: (target: string | undefined) => void
  reset: () => void
}

const defaultViewportState: ViewportState = {
  zoom: 1,
  pan: { x: 0, y: 0 },
  rotation: { x: 0, y: 0, z: 0 },
}

export const useViewportStore = create<ViewportStore>((set) => ({
  state: defaultViewportState,
  
  setZoom: (zoom) => 
    set((state) => ({ state: { ...state.state, zoom } })),
  
  setPan: (pan) => 
    set((state) => ({ state: { ...state.state, pan } })),
  
  setRotation: (rotation) => 
    set((state) => ({ state: { ...state.state, rotation } })),
  
  setTarget: (target) => 
    set((state) => ({ state: { ...state.state, target } })),
  
  reset: () => set({ state: defaultViewportState }),
}))

// ============================================================================
// UI Store
// ============================================================================

interface UIStore {
  sidebarOpen: boolean
  rightPanelOpen: boolean
  searchOpen: boolean
  selectedFile: string | null
  selectedCommit: string | null
  
  // Actions
  toggleSidebar: () => void
  toggleRightPanel: () => void
  toggleSearch: () => void
  setSelectedFile: (file: string | null) => void
  setSelectedCommit: (commit: string | null) => void
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  rightPanelOpen: true,
  searchOpen: false,
  selectedFile: null,
  selectedCommit: null,
  
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleRightPanel: () => set((state) => ({ rightPanelOpen: !state.rightPanelOpen })),
  toggleSearch: () => set((state) => ({ searchOpen: !state.searchOpen })),
  setSelectedFile: (file) => set({ selectedFile: file }),
  setSelectedCommit: (commit) => set({ selectedCommit: commit }),
}))
