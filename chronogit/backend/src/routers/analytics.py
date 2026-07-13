"""
Analytics routes - repository statistics, heatmaps, contributor analytics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from ..db.database import get_db
from ..models import Repository as RepoModel, Commit, Author, FileChange, HeatmapEntry
from ..schemas.responses import (
    ContributorStats, HeatmapResponse, HeatmapEntry as HeatmapEntrySchema,
    LanguageStats, RepositoryStats
)
from ..services.git_service import git_service

router = APIRouter()


@router.get("/repositories/{repo_id}/contributors", response_model=List[ContributorStats])
async def get_contributors(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get contributor statistics for a repository."""
    from sqlalchemy import select
    
    # Verify repository exists
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Open Git repository
    try:
        repo = await git_service.open_repository(repository.path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Collect contributor data
    contributors_data: Dict[str, Dict[str, Any]] = {}
    
    for commit in repo.iter_commits(max_count=10000):
        email = commit.author.email
        
        if email not in contributors_data:
            contributors_data[email] = {
                'name': commit.author.name,
                'email': email,
                'commits': 0,
                'insertions': 0,
                'deletions': 0,
                'first_commit': datetime.fromtimestamp(commit.committed_date),
                'last_commit': datetime.fromtimestamp(commit.committed_date),
                'languages': defaultdict(int),
                'files': set(),
                'hours': defaultdict(int),
            }
        
        data = contributors_data[email]
        data['commits'] += 1
        data['last_commit'] = max(
            data['last_commit'],
            datetime.fromtimestamp(commit.committed_date)
        )
        data['first_commit'] = min(
            data['first_commit'],
            datetime.fromtimestamp(commit.committed_date)
        )
        
        # Track hour of day activity
        hour = datetime.fromtimestamp(commit.committed_date).hour
        data['hours'][hour] += 1
        
        # Get file changes for this commit
        try:
            stats = commit.stats
            data['insertions'] += stats.total.insertions
            data['deletions'] += stats.total.deletions
            
            for file_path in stats.files.keys():
                data['files'].add(file_path)
                ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
                lang = _detect_language(ext)
                data['languages'][lang] += 1
        except Exception:
            pass
    
    # Build response
    response = []
    for email, data in contributors_data.items():
        active_days = (data['last_commit'] - data['first_commit']).days + 1
        
        author_schema = {
            'id': f"{repo_id}_{email.replace('@', '_at_')}",
            'repository_id': repo_id,
            'name': data['name'],
            'email': data['email'],
            'commit_count': data['commits'],
            'total_insertions': data['insertions'],
            'total_deletions': data['deletions'],
            'first_commit_date': data['first_commit'],
            'last_commit_date': data['last_commit'],
        }
        
        avg_commit_size = (data['insertions'] + data['deletions']) / max(data['commits'], 1)
        
        response.append(ContributorStats(
            author=author_schema,
            commits=data['commits'],
            insertions=data['insertions'],
            deletions=data['deletions'],
            first_commit=data['first_commit'],
            last_commit=data['last_commit'],
            active_days=active_days,
            languages=dict(data['languages']),
            average_commit_size=avg_commit_size,
        ))
    
    # Sort by commit count
    response.sort(key=lambda x: x.commits, reverse=True)
    
    return response


@router.get("/repositories/{repo_id}/heatmap")
async def get_heatmap(
    repo_id: str,
    heatmap_type: str = 'files',
    db: AsyncSession = Depends(get_db),
):
    """Get heatmap data for visualization."""
    from sqlalchemy import select
    
    # Verify repository exists
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Open Git repository
    try:
        repo = await git_service.open_repository(repository.path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Collect modification counts per path
    path_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        'modifications': 0,
        'insertions': 0,
        'deletions': 0,
        'authors': set(),
    })
    
    for commit in repo.iter_commits(max_count=10000):
        try:
            stats = commit.stats
            author_email = commit.author.email
            
            for file_path, file_stats in stats.files.items():
                metrics = path_metrics[file_path]
                metrics['modifications'] += 1
                metrics['insertions'] += file_stats.insertions
                metrics['deletions'] += file_stats.deletions
                metrics['authors'].add(author_email)
        except Exception:
            pass
    
    # Build heatmap entries
    entries = []
    for path, metrics in path_metrics.items():
        value = metrics['modifications']  # Primary metric
        
        entries.append(HeatmapEntrySchema(
            path=path,
            path_type='file' if '.' in path.split('/')[-1] else 'directory',
            value=float(value),
            metrics={
                'modifications': metrics['modifications'],
                'insertions': metrics['insertions'],
                'deletions': metrics['deletions'],
                'authors': len(metrics['authors']),
            },
        ))
    
    # Sort by value descending
    entries.sort(key=lambda x: x.value, reverse=True)
    
    # Calculate min/max
    values = [e.value for e in entries] if entries else [0]
    
    return HeatmapResponse(
        type=heatmap_type,
        data=entries[:100],  # Limit to top 100
        max=max(values),
        min=min(values),
    )


@router.get("/repositories/{repo_id}/languages")
async def get_languages(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get language distribution statistics."""
    from sqlalchemy import select
    
    # Verify repository exists
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Open Git repository
    try:
        repo = await git_service.open_repository(repository.path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Count files and lines per language
    languages: Dict[str, Dict[str, int]] = defaultdict(lambda: {'files': 0, 'lines': 0})
    total_files = 0
    total_lines = 0
    
    try:
        for item in repo.head.commit.tree.traverse():
            if item.type == 'blob':
                ext = item.name.split('.')[-1].lower() if '.' in item.name else ''
                lang = _detect_language(ext)
                
                # Try to get line count
                try:
                    content = item.data_stream.read().decode('utf-8', errors='ignore')
                    lines = len(content.splitlines())
                except Exception:
                    lines = 0
                
                languages[lang]['files'] += 1
                languages[lang]['lines'] += lines
                total_files += 1
                total_lines += lines
    except Exception:
        pass
    
    # Build response with colors
    language_colors = {
        'typescript': '#3178c6',
        'javascript': '#f7df1e',
        'python': '#3776ab',
        'java': '#b07219',
        'cpp': '#f34b7d',
        'c': '#555555',
        'go': '#00add8',
        'rust': '#dea584',
        'ruby': '#701516',
        'php': '#4F5D95',
        'swift': '#ffac45',
        'kotlin': '#7F52FF',
        'scala': '#c22d40',
        'html': '#e34c26',
        'css': '#563d7c',
        'scss': '#c6538c',
        'shell': '#89e051',
        'yaml': '#cb171e',
        'json': '#555555',
        'markdown': '#083fa1',
        'sql': '#e38c00',
    }
    
    response = []
    for lang, stats in sorted(languages.items(), key=lambda x: x[1]['lines'], reverse=True):
        percentage = (stats['lines'] / max(total_lines, 1)) * 100
        response.append(LanguageStats(
            name=lang,
            files=stats['files'],
            lines=stats['lines'],
            percentage=round(percentage, 2),
            color=language_colors.get(lang, '#888888'),
        ))
    
    return response


def _detect_language(ext: str) -> str:
    """Detect programming language from file extension."""
    language_map = {
        'ts': 'typescript',
        'tsx': 'typescript',
        'js': 'javascript',
        'jsx': 'javascript',
        'py': 'python',
        'rb': 'ruby',
        'rs': 'rust',
        'go': 'go',
        'java': 'java',
        'cpp': 'cpp',
        'cc': 'cpp',
        'cxx': 'cpp',
        'c': 'c',
        'h': 'c',
        'hpp': 'cpp',
        'cs': 'csharp',
        'php': 'php',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'sh': 'shell',
        'bash': 'shell',
        'yaml': 'yaml',
        'yml': 'yaml',
        'json': 'json',
        'xml': 'xml',
        'html': 'html',
        'css': 'css',
        'scss': 'scss',
        'less': 'less',
        'sql': 'sql',
        'md': 'markdown',
    }
    return language_map.get(ext, 'other')
