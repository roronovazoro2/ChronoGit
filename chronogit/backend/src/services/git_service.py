"""
Git Service - Core Git operations using GitPython
"""

import asyncio
import hashlib
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor

import git
from git import Repo, Commit as GitCommit, Blob, Tree
import networkx as nx

from ..core.config import settings
from ..models import Repository as RepoModel, Commit, Author, Branch, Tag, FileChange
from ..schemas.responses import (
    CommitResponse, FileNode, FileContent, FileDiff, DiffHunk, DiffLine,
    BranchResponse, TagResponse, FunctionInfo
)

logger = logging.getLogger(__name__)


class GitService:
    """Service for interacting with Git repositories."""
    
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._repo_cache: Dict[str, Repo] = {}
    
    async def open_repository(self, path: str) -> Repo:
        """Open a Git repository."""
        path = os.path.abspath(path)
        
        if not os.path.exists(path):
            raise ValueError(f"Repository path does not exist: {path}")
        
        if not os.path.exists(os.path.join(path, '.git')):
            raise ValueError(f"Not a Git repository: {path}")
        
        # Check cache
        if path in self._repo_cache:
            repo = self._repo_cache[path]
            try:
                repo.head.commit  # Test if repo is still valid
                return repo
            except Exception:
                del self._repo_cache[path]
        
        # Open repository asynchronously
        loop = asyncio.get_event_loop()
        repo = await loop.run_in_executor(
            self._executor,
            lambda: git.Repo(path)
        )
        
        self._repo_cache[path] = repo
        logger.info(f"Opened repository: {path}")
        return repo
    
    def close_repository(self, path: str) -> None:
        """Close and remove a repository from cache."""
        if path in self._repo_cache:
            self._repo_cache[path].close()
            del self._repo_cache[path]
    
    async def get_head_commit(self, repo: Repo) -> Optional[str]:
        """Get the HEAD commit hash."""
        try:
            return repo.head.commit.hexsha
        except Exception:
            return None
    
    async def get_commit_count(self, repo: Repo) -> int:
        """Get total number of commits."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: len(list(repo.iter_commits()))
        )
    
    async def iterate_commits(
        self,
        repo: Repo,
        batch_size: int = 100,
        max_commits: Optional[int] = None
    ) -> AsyncGenerator[List[GitCommit], None]:
        """Iterate through commits in batches."""
        loop = asyncio.get_event_loop()
        
        def get_batch(skip: int, count: int) -> List[GitCommit]:
            return list(repo.iter_commits(max_count=count, skip=skip))
        
        skip = 0
        total = 0
        
        while True:
            limit = max_commits - total if max_commits else batch_size
            batch = await loop.run_in_executor(
                self._executor,
                lambda s=skip, l=limit: get_batch(s, l)
            )
            
            if not batch:
                break
            
            yield batch
            skip += len(batch)
            total += len(batch)
            
            if max_commits and total >= max_commits:
                break
    
    async def get_commit_details(self, repo: Repo, commit_hash: str) -> Dict[str, Any]:
        """Get detailed information about a commit."""
        loop = asyncio.get_event_loop()
        
        def _get_details():
            try:
                commit = repo.commit(commit_hash)
                
                # Get stats
                stats = commit.stats
                
                # Get branches containing this commit
                branches = []
                for branch in repo.branches:
                    try:
                        if repo.is_ancestor(branch.commit, commit):
                            branches.append(branch.name)
                    except Exception:
                        pass
                
                # Get tags pointing to this commit
                tags = [tag.name for tag in repo.tags if tag.commit.hexsha == commit.hexsha]
                
                return {
                    'hash': commit.hexsha,
                    'short_hash': commit.hexsha[:7],
                    'message': commit.message.split('\n')[0].strip(),
                    'body': '\n'.join(commit.message.split('\n')[1:]).strip() or None,
                    'author_name': commit.author.name,
                    'author_email': commit.author.email,
                    'committed_at': datetime.fromtimestamp(commit.committed_date),
                    'committer_name': commit.committer.name,
                    'committer_email': commit.committer.email,
                    'parents': [p.hexsha for p in commit.parents],
                    'insertions': stats.total.insertions,
                    'deletions': stats.total.deletions,
                    'files_changed': stats.total.files,
                    'is_merge': len(commit.parents) > 1,
                    'branches': branches,
                    'tags': tags,
                }
            except Exception as e:
                logger.error(f"Error getting commit details: {e}")
                raise
        
        return await loop.run_in_executor(self._executor, _get_details)
    
    async def get_file_tree(
        self,
        repo: Repo,
        commit_hash: str = 'HEAD',
        path: str = ''
    ) -> List[FileNode]:
        """Get file tree at a specific commit."""
        loop = asyncio.get_event_loop()
        
        def _get_tree():
            try:
                commit = repo.commit(commit_hash)
                tree = commit.tree
                
                # Navigate to subdirectory if path specified
                if path:
                    for part in path.strip('/').split('/'):
                        if part:
                            tree = tree[part]
                
                nodes = []
                for item in sorted(tree, key=lambda x: (x.type != 'tree', x.name)):
                    item_path = f"{path}/{item.name}" if path else item.name
                    
                    if item.type == 'tree':
                        nodes.append(FileNode(
                            id=f"dir_{item_path}",
                            name=item.name,
                            path=item_path,
                            type='directory',
                            icon='folder',
                        ))
                    else:
                        # Get file size
                        try:
                            blob = item
                            size = blob.size
                        except Exception:
                            size = None
                        
                        # Detect language
                        ext = os.path.splitext(item.name)[1].lower()
                        language = self._detect_language(ext)
                        
                        nodes.append(FileNode(
                            id=f"file_{item_path}",
                            name=item.name,
                            path=item_path,
                            type='file',
                            size=size,
                            language=language,
                            icon=self._get_file_icon(ext),
                        ))
                
                return nodes
            except Exception as e:
                logger.error(f"Error getting file tree: {e}")
                return []
        
        return await loop.run_in_executor(self._executor, _get_tree)
    
    async def get_file_content(
        self,
        repo: Repo,
        file_path: str,
        commit_hash: str = 'HEAD'
    ) -> Optional[FileContent]:
        """Get file content at a specific commit."""
        loop = asyncio.get_event_loop()
        
        def _get_content():
            try:
                commit = repo.commit(commit_hash)
                
                # Navigate to file
                parts = file_path.split('/')
                obj = commit.tree
                for part in parts:
                    obj = obj[part]
                
                if obj.type != 'blob':
                    return None
                
                # Try to decode content
                try:
                    content = obj.data_stream.read().decode('utf-8')
                    encoding = 'utf-8'
                except UnicodeDecodeError:
                    content = obj.data_stream.read().decode('latin-1')
                    encoding = 'latin-1'
                
                # Detect language
                ext = os.path.splitext(file_path)[1].lower()
                language = self._detect_language(ext)
                
                return FileContent(
                    path=file_path,
                    content=content,
                    encoding=encoding,
                    size=len(content),
                    language=language,
                    lines=len(content.splitlines()),
                    sha=obj.hexsha,
                )
            except Exception as e:
                logger.error(f"Error getting file content: {e}")
                return None
        
        return await loop.run_in_executor(self._executor, _get_content)
    
    async def get_commit_diff(
        self,
        repo: Repo,
        commit_hash: str
    ) -> List[FileDiff]:
        """Get diff for a commit."""
        loop = asyncio.get_event_loop()
        
        def _get_diff():
            try:
                commit = repo.commit(commit_hash)
                
                # Get parent commit(s)
                if not commit.parents:
                    # First commit - compare against empty tree
                    parent = None
                else:
                    parent = commit.parents[0]
                
                diffs = []
                
                # Use git diff for detailed output
                if parent:
                    diff_index = parent.diff(commit)
                else:
                    diff_index = commit.diff(git.NULL_TREE)
                
                for diff in diff_index:
                    # Determine status
                    if diff.deleted_file:
                        status = 'deleted'
                    elif diff.renamed_file:
                        status = 'renamed'
                    elif diff.new_file:
                        status = 'added'
                    else:
                        status = 'modified'
                    
                    # Parse diff text
                    hunks = self._parse_diff(diff.diff.decode('utf-8', errors='replace'))
                    
                    diffs.append(FileDiff(
                        path=diff.b_path or diff.a_path,
                        old_path=diff.a_path if diff.renamed_file else None,
                        status=status,
                        hunks=hunks,
                        insertions=diff.b_blob.data_stream.read().count(b'\n+') if diff.b_blob else 0,
                        deletions=diff.a_blob.data_stream.read().count(b'\n-') if diff.a_blob else 0,
                        binary=diff.binary,
                    ))
                
                return diffs
            except Exception as e:
                logger.error(f"Error getting commit diff: {e}")
                return []
        
        return await loop.run_in_executor(self._executor, _get_diff)
    
    def _parse_diff(self, diff_text: str) -> List[DiffHunk]:
        """Parse unified diff format into structured hunks."""
        hunks = []
        current_hunk = None
        
        for line in diff_text.split('\n'):
            if line.startswith('@@'):
                # New hunk header
                if current_hunk:
                    hunks.append(current_hunk)
                
                # Parse @@ -old_start,old_lines +new_start,new_lines @@
                parts = line.split('@@')
                if len(parts) >= 2:
                    ranges = parts[1].strip().split(' ')
                    old_range = ranges[0][1:].split(',')  # Remove leading '-'
                    new_range = ranges[1][1:].split(',') if len(ranges) > 1 else ['1']
                    
                    current_hunk = DiffHunk(
                        old_start=int(old_range[0]),
                        old_lines=int(old_range[1]) if len(old_range) > 1 else 1,
                        new_start=int(new_range[0]),
                        new_lines=int(new_range[1]) if len(new_range) > 1 else 1,
                        header=line,
                        lines=[],
                    )
            
            elif current_hunk:
                if line.startswith('+'):
                    current_hunk.lines.append(DiffLine(
                        type='add',
                        content=line[1:],
                    ))
                elif line.startswith('-'):
                    current_hunk.lines.append(DiffLine(
                        type='delete',
                        content=line[1:],
                    ))
                else:
                    current_hunk.lines.append(DiffLine(
                        type='context',
                        content=line[1:] if line.startswith(' ') else line,
                    ))
        
        if current_hunk:
            hunks.append(current_hunk)
        
        return hunks
    
    async def get_branches(self, repo: Repo) -> List[BranchResponse]:
        """Get all branches."""
        loop = asyncio.get_event_loop()
        
        def _get_branches():
            branches = []
            current = repo.active_branch.name if not repo.head.is_detached else None
            
            for branch in repo.branches:
                branches.append(BranchResponse(
                    name=branch.name,
                    is_current=branch.name == current,
                    is_remote=False,
                    head_commit=branch.commit.hexsha,
                ))
            
            # Add remote branches
            for remote in repo.remotes:
                for ref in remote.refs:
                    branches.append(BranchResponse(
                        name=ref.name,
                        is_current=False,
                        is_remote=True,
                        head_commit=ref.commit.hexsha if ref.commit else None,
                    ))
            
            return branches
        
        return await loop.run_in_executor(self._executor, _get_branches)
    
    async def get_tags(self, repo: Repo) -> List[TagResponse]:
        """Get all tags."""
        loop = asyncio.get_event_loop()
        
        def _get_tags():
            tags = []
            for tag in repo.tags:
                tags.append(TagResponse(
                    name=tag.name,
                    commit=tag.commit.hexsha,
                    message=tag.message if hasattr(tag, 'message') else None,
                    tagger_name=tag.tagger.name if hasattr(tag, 'tagger') and tag.tagger else None,
                    tagger_email=tag.tagger.email if hasattr(tag, 'tagger') and tag.tagger else None,
                    tagged_at=datetime.fromtimestamp(tag.tagged_date) if hasattr(tag, 'tagged_date') else None,
                ))
            return tags
        
        return await loop.run_in_executor(self._executor, _get_tags)
    
    def _detect_language(self, ext: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
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
            '.cs': 'csharp',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'shell',
            '.bash': 'shell',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.sql': 'sql',
            '.md': 'markdown',
        }
        return language_map.get(ext, 'plaintext')
    
    def _get_file_icon(self, ext: str) -> str:
        """Get icon name for file extension."""
        icon_map = {
            '.ts': 'typescript',
            '.tsx': 'react',
            '.js': 'javascript',
            '.py': 'python',
            '.rb': 'ruby',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'terminal',
            '.yaml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'sass',
            '.sql': 'database',
            '.md': 'markdown',
            '.png': 'image',
            '.jpg': 'image',
            '.svg': 'image',
        }
        return icon_map.get(ext, 'file')
    
    async def get_repository_stats(self, repo: Repo) -> Dict[str, Any]:
        """Get comprehensive repository statistics."""
        loop = asyncio.get_event_loop()
        
        def _get_stats():
            try:
                # Basic counts
                total_commits = len(list(repo.iter_commits()))
                total_branches = len(repo.branches)
                total_tags = len(repo.tags)
                total_remotes = len(repo.remotes)
                
                # Get first and last commit dates
                commits = list(repo.iter_commits())
                if commits:
                    first_commit = commits[-1]
                    last_commit = commits[0]
                    first_date = datetime.fromtimestamp(first_commit.committed_date)
                    last_date = datetime.fromtimestamp(last_commit.committed_date)
                    age_days = (last_date - first_date).days
                else:
                    first_date = last_date = datetime.now()
                    age_days = 0
                
                # Count files
                try:
                    tree = repo.head.commit.tree
                    total_files = sum(1 for _ in tree.traverse() if _.type == 'blob')
                except Exception:
                    total_files = 0
                
                # Language stats
                languages: Dict[str, int] = {}
                try:
                    for item in repo.head.commit.tree.traverse():
                        if item.type == 'blob':
                            ext = os.path.splitext(item.name)[1].lower()
                            lang = self._detect_language(ext)
                            languages[lang] = languages.get(lang, 0) + 1
                except Exception:
                    pass
                
                # Contributor count
                authors = set()
                for commit in repo.iter_commits(max_count=1000):
                    authors.add(commit.author.email)
                
                return {
                    'total_commits': total_commits,
                    'total_files': total_files,
                    'total_branches': total_branches,
                    'total_tags': total_tags,
                    'total_remotes': total_remotes,
                    'first_commit': first_date,
                    'last_commit': last_date,
                    'age_days': age_days,
                    'contributors': len(authors),
                    'languages': languages,
                }
            except Exception as e:
                logger.error(f"Error getting repository stats: {e}")
                return {}
        
        return await loop.run_in_executor(self._executor, _get_stats)
    
    async def build_commit_graph(self, repo: Repo) -> nx.DiGraph:
        """Build a NetworkX graph of commit relationships."""
        loop = asyncio.get_event_loop()
        
        def _build_graph():
            G = nx.DiGraph()
            
            for commit in repo.iter_commits():
                commit_hash = commit.hexsha
                G.add_node(
                    commit_hash,
                    message=commit.message.split('\n')[0],
                    author=commit.author.name,
                    date=datetime.fromtimestamp(commit.committed_date),
                    is_merge=len(commit.parents) > 1,
                )
                
                # Add edges to parents
                for parent in commit.parents:
                    G.add_edge(parent.hexsha, commit_hash)
            
            return G
        
        return await loop.run_in_executor(self._executor, _build_graph)


# Global service instance
git_service = GitService()
