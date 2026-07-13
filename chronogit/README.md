# ChronoGit

An AI-powered Git repository explorer that allows developers to literally travel through a repository's history as if they were watching software evolve over time.

## Overview

ChronoGit is not another GitHub clone. It feels like Google Earth meets Git, VS Code, and GitLens, allowing developers to replay the evolution of an entire codebase.

### Key Features

- **Interactive Timeline**: Explore every commit chronologically with infinite zoom and pan
- **3D Time Travel View**: Fly through commits in a Three.js visualization
- **Repository Replay**: Watch your codebase evolve from first commit to HEAD
- **AI-Powered Insights**: Commit summaries, bug origin analysis, and architecture explanations
- **Function-Level Diffs**: Understand changes at the function level, not just lines
- **Heatmaps**: Discover hotspots and unstable areas in your codebase
- **Contributor Analytics**: Deep insights into team activity and code ownership
- **Architecture Evolution**: Visualize how your system architecture changed over time

## Technology Stack

### Frontend
- React 19 with TypeScript
- Vite for blazing fast development
- TailwindCSS for modern styling
- Framer Motion for smooth animations
- Three.js & React Three Fiber for 3D visualizations
- Monaco Editor for code viewing
- D3.js & Chart.js for data visualization

### Backend
- FastAPI with Python 3.13
- GitPython for Git operations
- Tree-sitter for AST parsing
- SQLAlchemy with SQLite/PostgreSQL
- NetworkX for graph analysis

### AI Features
- Local LLM integration (Qwen Coder compatible)
- No external API requirements
- Commit summaries and explanations
- Bug origin reasoning

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/chronogit.git
cd chronogit

# Start with Docker Compose
docker-compose up -d

# Or run locally
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Documentation

- [Architecture Guide](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Developer Guide](docs/developer-guide.md)
- [Deployment Guide](docs/deployment.md)
- [User Manual](docs/user-manual.md)

## Project Structure

```
chronogit/
├── frontend/          # React application
├── backend/           # FastAPI server
├── shared/            # Shared types and utilities
├── parser/            # Code parsing utilities
├── ai/                # AI integration
├── database/          # Database models and migrations
├── docs/              # Documentation
├── docker/            # Docker configurations
├── scripts/           # Utility scripts
├── tests/             # Test suites
└── examples/          # Example repositories
```

## License

MIT License - See LICENSE file for details
