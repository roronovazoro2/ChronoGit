"""
Search routes - full-text search across commits, files, functions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import re

from ..db.database import get_db
from ..models import Repository as RepoModel, Commit, Author
from ..schemas.responses import SearchQuery, SearchResponse, SearchResult, Highlight
from ..services.git_service import git_service

router = APIRouter()


@router.get("/repositories/{repo_id}/search", response_model=SearchResponse)
async def search(
    repo_id: str,
    q: str = Query(..., description="Search query"),
    types: Optional[str] = Query(None, description="Comma-separated types to search"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Search across repository content."""
    from sqlalchemy import select
    
    # Verify repository exists
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Parse types
    search_types = []
    if types:
        search_types = [t.strip() for t in types.split(',')]
    else:
        search_types = ['commit', 'file', 'author']
    
    # Open Git repository
    try:
        repo = await git_service.open_repository(repository.path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    results: List[SearchResult] = []
    
    # Search commits
    if 'commit' in search_types:
        commit_results = _search_commits(repo, q, limit // 3)
        results.extend(commit_results)
    
    # Search authors
    if 'author' in search_types:
        author_results = _search_authors(repo, q, limit // 3)
        results.extend(author_results)
    
    # Search branches
    if 'branch' in search_types:
        branch_results = _search_branches(repo, q, limit // 3)
        results.extend(branch_results)
    
    # Search tags
    if 'tag' in search_types:
        tag_results = _search_tags(repo, q, limit // 3)
        results.extend(tag_results)
    
    # Sort by score and limit
    results.sort(key=lambda x: x.score, reverse=True)
    results = results[:limit]
    
    return SearchResponse(
        results=results,
        total=len(results),
        query=q,
    )


def _search_commits(repo, query: str, limit: int) -> List[SearchResult]:
    """Search through commit messages and metadata."""
    results = []
    query_lower = query.lower()
    query_terms = query_lower.split()
    
    for commit in repo.iter_commits(max_count=1000):
        score = 0.0
        highlights = []
        
        # Search in message
        message = commit.message
        message_lower = message.lower()
        
        matched = False
        for term in query_terms:
            if term in message_lower:
                score += 0.5
                matched = True
                
                # Create highlight
                start = message_lower.find(term)
                if start >= 0:
                    end = min(start + len(term) + 50, len(message))
                    snippet = message[max(0, start - 20):end]
                    highlights.append(Highlight(
                        text=snippet,
                        matched=True,
                    ))
        
        # Search in author
        if query_lower in commit.author.name.lower():
            score += 0.3
            matched = True
        
        if query_lower in commit.author.email.lower():
            score += 0.3
            matched = True
        
        # Search in hash
        if query_lower in commit.hexsha.lower():
            score += 0.8
            matched = True
        
        if matched:
            results.append(SearchResult(
                type='commit',
                id=commit.hexsha,
                title=message.split('\n')[0][:100],
                subtitle=f"by {commit.author.name}",
                commit=commit.hexsha[:7],
                score=score,
                highlights=highlights[:3] if highlights else None,
            ))
            
            if len(results) >= limit:
                break
    
    return results


def _search_authors(repo, query: str, limit: int) -> List[SearchResult]:
    """Search through commit authors."""
    results = []
    query_lower = query.lower()
    seen_authors = set()
    
    for commit in repo.iter_commits(max_count=1000):
        email = commit.author.email
        name = commit.author.name
        
        if email in seen_authors:
            continue
        
        score = 0.0
        
        if query_lower in name.lower():
            score += 0.8
        
        if query_lower in email.lower():
            score += 0.8
        
        if score > 0:
            seen_authors.add(email)
            results.append(SearchResult(
                type='author',
                id=email,
                title=name,
                subtitle=email,
                score=score,
            ))
            
            if len(results) >= limit:
                break
    
    return results


def _search_branches(repo, query: str, limit: int) -> List[SearchResult]:
    """Search through branch names."""
    results = []
    query_lower = query.lower()
    
    for branch in repo.branches:
        if query_lower in branch.name.lower():
            results.append(SearchResult(
                type='branch',
                id=branch.name,
                title=branch.name,
                subtitle=f"HEAD: {branch.commit.hexsha[:7]}",
                score=0.9,
            ))
            
            if len(results) >= limit:
                break
    
    return results


def _search_tags(repo, query: str, limit: int) -> List[SearchResult]:
    """Search through tag names."""
    results = []
    query_lower = query.lower()
    
    for tag in repo.tags:
        if query_lower in tag.name.lower():
            results.append(SearchResult(
                type='tag',
                id=tag.name,
                title=tag.name,
                subtitle=f"Commit: {tag.commit.hexsha[:7]}",
                score=0.9,
            ))
            
            if len(results) >= limit:
                break
    
    return results
