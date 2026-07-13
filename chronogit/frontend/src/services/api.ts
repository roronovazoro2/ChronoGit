import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { 
  RepositoryInfo, RepositoryStats, Commit, CommitListResponse,
  FileNode, FileContent, TimelineResponse, ContributorStats,
  HeatmapResponse, SearchResult, SearchQuery
} from '@chronogit/shared'

const API_BASE = '/api/v1'

// ============================================================================
// Repository Queries
// ============================================================================

export function useRepositories() {
  return useQuery({
    queryKey: ['repositories'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/repositories`)
      if (!response.ok) throw new Error('Failed to fetch repositories')
      return response.json() as Promise<RepositoryInfo[]>
    },
  })
}

export function useRepository(repoId: string) {
  return useQuery({
    queryKey: ['repository', repoId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/repositories/${repoId}`)
      if (!response.ok) throw new Error('Failed to fetch repository')
      return response.json() as Promise<RepositoryInfo>
    },
    enabled: !!repoId,
  })
}

export function useRepositoryStats(repoId: string) {
  return useQuery({
    queryKey: ['repository-stats', repoId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/repositories/${repoId}/stats`)
      if (!response.ok) throw new Error('Failed to fetch stats')
      return response.json() as Promise<RepositoryStats>
    },
    enabled: !!repoId,
  })
}

export function useImportRepository() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: { path: string; name?: string }) => {
      const response = await fetch(`${API_BASE}/repositories/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (!response.ok) throw new Error('Failed to import repository')
      return response.json() as Promise<RepositoryInfo>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repositories'] })
    },
  })
}

// ============================================================================
// Commit Queries
// ============================================================================

export function useCommits(repoId: string, page = 1, pageSize = 50) {
  return useQuery({
    queryKey: ['commits', repoId, page, pageSize],
    queryFn: async () => {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
      const response = await fetch(`${API_BASE}/repositories/${repoId}/commits?${params}`)
      if (!response.ok) throw new Error('Failed to fetch commits')
      return response.json() as Promise<CommitListResponse>
    },
    enabled: !!repoId,
  })
}

export function useCommit(repoId: string, commitHash: string) {
  return useQuery({
    queryKey: ['commit', repoId, commitHash],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/repositories/${repoId}/commits/${commitHash}`)
      if (!response.ok) throw new Error('Failed to fetch commit')
      return response.json() as Promise<Commit>
    },
    enabled: !!repoId && !!commitHash,
  })
}

// ============================================================================
// File Queries
// ============================================================================

export function useFileTree(repoId: string, commit?: string, path?: string) {
  return useQuery({
    queryKey: ['file-tree', repoId, commit, path],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (commit) params.set('commit', commit)
      if (path) params.set('path', path)
      const response = await fetch(`${API_BASE}/repositories/${repoId}/files?${params}`)
      if (!response.ok) throw new Error('Failed to fetch file tree')
      return response.json() as Promise<FileNode[]>
    },
    enabled: !!repoId,
  })
}

export function useFileContent(repoId: string, filePath: string, commit?: string) {
  return useQuery({
    queryKey: ['file-content', repoId, filePath, commit],
    queryFn: async () => {
      const encodedPath = encodeURIComponent(filePath)
      const params = new URLSearchParams()
      if (commit) params.set('commit', commit)
      const response = await fetch(`${API_BASE}/repositories/${repoId}/files/${encodedPath}?${params}`)
      if (!response.ok) throw new Error('Failed to fetch file content')
      return response.json() as Promise<FileContent>
    },
    enabled: !!repoId && !!filePath,
  })
}

// ============================================================================
// Timeline Queries
// ============================================================================

export function useTimeline(repoId: string, limit = 500) {
  return useQuery({
    queryKey: ['timeline', repoId, limit],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: String(limit) })
      const response = await fetch(`${API_BASE}/repositories/${repoId}/timeline?${params}`)
      if (!response.ok) throw new Error('Failed to fetch timeline')
      return response.json() as Promise<TimelineResponse>
    },
    enabled: !!repoId,
  })
}

// ============================================================================
// Analytics Queries
// ============================================================================

export function useContributors(repoId: string) {
  return useQuery({
    queryKey: ['contributors', repoId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/repositories/${repoId}/contributors`)
      if (!response.ok) throw new Error('Failed to fetch contributors')
      return response.json() as Promise<ContributorStats[]>
    },
    enabled: !!repoId,
  })
}

export function useHeatmap(repoId: string, type = 'files') {
  return useQuery({
    queryKey: ['heatmap', repoId, type],
    queryFn: async () => {
      const params = new URLSearchParams({ type })
      const response = await fetch(`${API_BASE}/repositories/${repoId}/heatmap?${params}`)
      if (!response.ok) throw new Error('Failed to fetch heatmap')
      return response.json() as Promise<HeatmapResponse>
    },
    enabled: !!repoId,
  })
}

export function useLanguages(repoId: string) {
  return useQuery({
    queryKey: ['languages', repoId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/repositories/${repoId}/languages`)
      if (!response.ok) throw new Error('Failed to fetch languages')
      return response.json()
    },
    enabled: !!repoId,
  })
}

// ============================================================================
// Search Queries
// ============================================================================

export function useSearch(repoId: string, query: string, types?: string[]) {
  return useQuery({
    queryKey: ['search', repoId, query, types],
    queryFn: async () => {
      const params = new URLSearchParams({ q: query })
      if (types) params.set('types', types.join(','))
      const response = await fetch(`${API_BASE}/repositories/${repoId}/search?${params}`)
      if (!response.ok) throw new Error('Failed to search')
      return response.json() as Promise<SearchResult[]>
    },
    enabled: !!repoId && query.length >= 2,
  })
}

// ============================================================================
// AI Queries
// ============================================================================

export function useCommitSummary(repoId: string, commitHash: string) {
  return useQuery({
    queryKey: ['ai-summary', repoId, commitHash],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/repositories/${repoId}/ai/summary/${commitHash}`)
      if (!response.ok) throw new Error('Failed to fetch AI summary')
      return response.json()
    },
    enabled: !!repoId && !!commitHash,
  })
}

export function useBugAnalysis(repoId: string) {
  return useMutation({
    mutationFn: async (data: { description: string; commit_hash?: string; function_name?: string }) => {
      const response = await fetch(`${API_BASE}/repositories/${repoId}/ai/bug-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (!response.ok) throw new Error('Failed to analyze bug')
      return response.json()
    },
  })
}
