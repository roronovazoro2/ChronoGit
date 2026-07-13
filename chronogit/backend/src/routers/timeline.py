"""
Timeline routes - interactive timeline visualization data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math
from datetime import datetime

from ..db.database import get_db
from ..models import Repository as RepoModel
from ..schemas.responses import TimelineResponse, TimelineNode, TimelineEdge, CommitResponse
from ..services.git_service import git_service

router = APIRouter()


@router.get("/repositories/{repo_id}/timeline")
async def get_timeline(
    repo_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    branch: Optional[str] = None,
    limit: int = Query(500, ge=1, le=2000),
    db: AsyncSession = Depends(get_db),
):
    """Get timeline data for visualization."""
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
    
    # Collect commits
    commits_data = []
    
    for commit in repo.iter_commits(max_count=limit):
        # Apply date filters
        commit_date = datetime.fromtimestamp(commit.committed_date)
        
        if start_date:
            try:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if commit_date < start:
                    continue
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                if commit_date > end:
                    continue
            except ValueError:
                pass
        
        # Get commit details
        details = await git_service.get_commit_details(repo, commit.hexsha)
        commits_data.append(details)
    
    # Generate timeline layout
    nodes, edges = _generate_timeline_layout(commits_data)
    
    # Create clusters based on branches
    clusters = _generate_clusters(commits_data)
    
    return TimelineResponse(
        nodes=nodes,
        edges=edges,
        clusters=clusters,
        metadata={
            'total_commits': len(commits_data),
            'date_range': {
                'start': commits_data[-1]['committed_at'].isoformat() if commits_data else None,
                'end': commits_data[0]['committed_at'].isoformat() if commits_data else None,
            },
        },
    )


def _generate_timeline_layout(commits_data: list) -> tuple[list[TimelineNode], list[TimelineEdge]]:
    """Generate 2D/3D layout for timeline visualization."""
    nodes = []
    edges = []
    
    if not commits_data:
        return nodes, edges
    
    # Sort by date (oldest first for left-to-right timeline)
    commits_data.sort(key=lambda x: x['committed_at'])
    
    # Calculate time span
    first_date = commits_data[0]['committed_at']
    last_date = commits_data[-1]['committed_at']
    time_span = (last_date - first_date).total_seconds() or 1
    
    # Track branch lanes
    branch_lanes: dict[str, int] = {}
    next_lane = 0
    
    # Assign lanes to branches
    for commit in commits_data:
        for branch in commit.get('branches', ['main']):
            if branch not in branch_lanes:
                branch_lanes[branch] = next_lane
                next_lane += 1
    
    max_lane = max(branch_lanes.values()) if branch_lanes else 0
    
    # Generate nodes
    for i, commit in enumerate(commits_data):
        # X position based on time
        commit_date = commit['committed_at']
        time_position = (commit_date - first_date).total_seconds() / time_span
        x = time_position * 1000  # Scale to 0-1000
        
        # Y position based on primary branch
        primary_branch = commit['branches'][0] if commit.get('branches') else 'main'
        lane = branch_lanes.get(primary_branch, 0)
        
        # Normalize y to center
        y = (lane - max_lane / 2) * 60  # 60px between lanes
        
        # Z position for merge commits (elevated)
        z = 50 if commit['is_merge'] else 0
        
        # Color based on commit type
        color = _get_commit_color(commit['message'])
        
        # Size based on change magnitude
        changes = commit['insertions'] + commit['deletions']
        size = 8 + min(changes / 50, 16)  # 8-24px
        
        # Create commit response object
        commit_response = CommitResponse(
            id=commit['hash'],
            short_hash=commit['short_hash'],
            repository_id='',  # Will be filled by client
            author_id='',
            message=commit['message'],
            body=commit.get('body'),
            committed_at=commit['committed_at'],
            insertions=commit['insertions'],
            deletions=commit['deletions'],
            files_changed=commit['files_changed'],
            is_merge=commit['is_merge'],
            parent_hashes=commit['parents'],
            branches=commit.get('branches', []),
            tags=commit.get('tags', []),
        )
        
        node = TimelineNode(
            id=commit['hash'],
            commit=commit_response,
            x=x,
            y=y,
            z=z,
            cluster=primary_branch,
            color=color,
            size=size,
        )
        nodes.append(node)
        
        # Create edges to parents
        for parent_hash in commit['parents']:
            edge_type = 'merge' if len(commit['parents']) > 1 else 'parent'
            edges.append(TimelineEdge(
                source=parent_hash,
                target=commit['hash'],
                type=edge_type,
            ))
    
    return nodes, edges


def _generate_clusters(commits_data: list) -> list:
    """Generate commit clusters based on branches."""
    clusters = []
    branch_commits: dict[str, list] = {}
    
    for commit in commits_data:
        for branch in commit.get('branches', ['main']):
            if branch not in branch_commits:
                branch_commits[branch] = []
            branch_commits[branch].append(commit['hash'])
    
    cluster_colors = {
        'main': '#6366f1',
        'master': '#6366f1',
        'develop': '#22c55e',
        'feature': '#06b6d4',
        'release': '#f59e0b',
        'hotfix': '#ef4444',
    }
    
    for branch, commit_ids in branch_commits.items():
        # Determine color based on branch name
        color = '#8b5cf6'  # default
        for prefix, branch_color in cluster_colors.items():
            if prefix in branch.lower():
                color = branch_color
                break
        
        clusters.append({
            'id': branch,
            'label': branch,
            'nodes': commit_ids,
            'color': color,
        })
    
    return clusters


def _get_commit_color(message: str) -> str:
    """Get color for commit based on message patterns."""
    message_lower = message.lower()
    
    if 'merge' in message_lower:
        return '#9ca3af'  # gray
    elif 'fix' in message_lower or 'bug' in message_lower:
        return '#22c55e'  # green
    elif 'feat' in message_lower or 'add' in message_lower:
        return '#6366f1'  # indigo
    elif 'refactor' in message_lower:
        return '#8b5cf6'  # violet
    elif 'test' in message_lower:
        return '#06b6d4'  # cyan
    elif 'doc' in message_lower:
        return '#f59e0b'  # amber
    elif 'style' in message_lower:
        return '#ec4899'  # pink
    elif 'chore' in message_lower:
        return '#6b7280'  # slate
    else:
        return '#3b82f6'  # blue
