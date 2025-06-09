# Meeting AI - End-to-End Meeting Intelligence Platform

![Meeting AI](https://img.shields.io/badge/Meeting-AI-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A comprehensive AI-powered platform for meeting transcription, analysis, and intelligence extraction. Transform your audio recordings into actionable insights with advanced speech-to-text, semantic search, and automated analysis.

## 🚀 Features

### Core Capabilities
- **AI Transcription**: High-accuracy speech-to-text using OpenAI Whisper
- **Speaker Diarization**: Automatic speaker identification and timestamps
- **Semantic Search**: Vector-based search across all meeting content
- **Smart Analysis**: 9 specialized analysis templates for insights extraction
- **RAG Q&A**: Ask questions about your meetings using natural language
- **Real-time Processing**: Sub-30 second processing for most audio files

### Analysis Templates
1. **Key Points** - Extract main discussion topics and takeaways
2. **Action Items** - Identify tasks with owners and due dates
3. **Decisions** - Capture important decisions made
4. **Risks & Blockers** - Identify potential issues and impediments
5. **Follow-ups** - List next steps and future actions
6. **Parking Lot** - Topics deferred for later discussion
7. **Roadmap** - Timeline and planning discussions
8. **Kudos** - Recognition and positive feedback
9. **Custom** - Configurable templates for specific needs

### Enterprise Features
- **Security**: End-to-end encryption, VPC deployment, SOC 2 compliance
- **Scalability**: Serverless architecture with auto-scaling
- **Cost Tracking**: Built-in monitoring and budget controls
- **Multi-format Support**: WAV, MP3, M4A, FLAC, OGG
- **API-first**: Complete REST API with OpenAPI documentation

## 🏗️ Architecture

### High-Level System Design

```mermaid
graph TB
    Client[Frontend - Next.js] --> ALB[Application Load Balancer]
    ALB --> API[FastAPI Backend]
    API --> DB[(PostgreSQL + pgvector)]
    API --> Cache[(Redis)]
    API --> Queue[Celery Workers]
    
    Upload[Audio Upload] --> S3[S3 Raw Audio]
    S3 --> SF[Step Functions]
    SF --> Whisper[OpenAI Whisper]
    SF --> Embed[Embedding Service]
    SF --> LLM[Google Gemini]
    
    Queue --> Workers[Processing Workers]
    Workers --> S3P[S3 Processed]
    Workers --> DB
```

### Technology Stack

**Frontend**
- Next.js 14 with App Router
- React 19 with Server Components
- TypeScript for type safety
- Tailwind CSS + shadcn/ui
- TanStack Query for state management

**Backend**
- FastAPI with async/await
- SQLAlchemy 2.0 with async support
- Celery for background processing
- Pydantic for data validation
- pgvector for vector operations

**Infrastructure**
- AWS ECS Fargate for containerized services
- PostgreSQL 16 with pgvector extension
- Redis for caching and message queuing
- S3 for object storage with lifecycle policies
- Step Functions for audio processing orchestration

**AI/ML Services**
- OpenAI Whisper for speech-to-text
- OpenAI text-embedding-3-small for embeddings
- Google Gemini 2.0 Flash for text analysis
- pgvector for semantic search

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- AWS CLI (for cloud deployment)

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/meeting-ai.git
cd meeting-ai

# Copy environment files
make env

# Edit .env files with your API keys
# Required: OPENAI_API_KEY, GOOGLE_API_KEY
vim .env
vim backend/.env
vim frontend/.env.local
```

### 2. Start Development Environment

```bash
# Start all services
make start

# Services will be available at:
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 3. Initialize Database

```bash
# Run database migrations
make db-migrate

# (Optional) Seed with sample data
make db-seed
```

### 4. Upload Your First Meeting

1. Open http://localhost:3000
2. Click "Upload Meeting"
3. Upload an audio file (WAV, MP3, etc.)
4. Wait for processing (typically 30-60 seconds)
5. View transcripts and insights

## 📚 Development Guide

### Project Structure

```
meeting-ai/
├── frontend/          # Next.js frontend application
│   ├── src/app/       # App router pages
│   ├── src/components/ # Reusable UI components
│   └── src/lib/       # Utilities and API client
├── backend/           # FastAPI backend application
│   ├── app/api/       # API endpoints
│   ├── app/models/    # Database models
│   ├── app/services/  # Business logic
│   └── app/workers/   # Celery tasks
├── infrastructure/    # Terraform infrastructure as code
│   ├── modules/       # Reusable Terraform modules
│   └── environments/ # Environment-specific configs
└── scripts/          # Utility scripts and tools
```

### Available Commands

```bash
# Development
make start          # Start all services
make stop           # Stop all services
make restart        # Restart services
make logs          # View service logs

# Building
make build         # Build all Docker images
make build-backend # Build backend only
make build-frontend # Build frontend only

# Database
make db-migrate    # Run migrations
make db-reset      # Reset database
make db-seed       # Seed with sample data

# Testing
make test          # Run all tests
make test-backend  # Run backend tests
make test-frontend # Run frontend tests

# Code Quality
make lint          # Run linting
make format        # Format code
make type-check    # Type checking

# Infrastructure
make infra-plan    # Plan Terraform changes
make infra-apply   # Apply infrastructure

# Maintenance
make clean         # Clean containers/volumes
make clean-all     # Clean everything
```

### API Documentation

The backend provides comprehensive API documentation:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

Key endpoints:
- `POST /api/v1/meetings/` - Create meeting
- `GET /api/v1/meetings/{id}` - Get meeting details
- `POST /api/v1/meetings/{id}/upload-url` - Get upload URL
- `GET /api/v1/search/` - Semantic search
- `POST /api/v1/questions/ask` - Ask questions

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# AI Services
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_RAW_AUDIO=your-audio-bucket

# Auth
JWT_SECRET_KEY=your-secret-key
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Feature Flags

Control features via environment variables:
- `ENABLE_SPEAKER_DIARIZATION=true` - Enable speaker identification
- `ENABLE_REAL_TIME_PROCESSING=true` - Enable live transcription
- `ENABLE_COST_TRACKING=true` - Track AI service costs

## 🚀 Deployment

### Local Development
Already covered in Quick Start section.

### AWS Production Deployment

1. **Setup AWS Infrastructure**
```bash
cd infrastructure/environments/prod
terraform init
terraform plan
terraform apply
```

2. **Configure CI/CD**
Set GitHub secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`

3. **Deploy Application**
Push to main branch to trigger automated deployment.

### Environment-Specific Configs

- **Development**: `infrastructure/environments/dev/`
- **Staging**: `infrastructure/environments/staging/`
- **Production**: `infrastructure/environments/prod/`

## 🧪 Testing

### Backend Testing
```bash
cd backend
poetry run pytest -v --cov=app
```

Test categories:
- Unit tests for business logic
- Integration tests for API endpoints
- Database tests with fixtures
- Async tests for background tasks

### Frontend Testing
```bash
cd frontend
npm test
npm run test:coverage
```

Test categories:
- Component unit tests
- API integration tests
- E2E tests with Playwright
- Accessibility tests

### Testing Strategy
- **Unit Tests**: 80%+ coverage target
- **Integration Tests**: API contracts and database operations
- **E2E Tests**: Critical user journeys
- **Performance Tests**: Load testing with k6

## 📊 Monitoring & Observability

### Metrics
- **Application**: Custom metrics via Prometheus
- **Infrastructure**: CloudWatch metrics
- **Business**: Meeting processing stats
- **Cost**: AI service usage tracking

### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Centralized**: CloudWatch Logs with log aggregation
- **Levels**: Debug, Info, Warning, Error, Critical

### Alerting
- **SLA Monitoring**: 99.5% availability target
- **Error Rates**: Alert on >1% error rate
- **Latency**: Alert on >30s processing time
- **Cost**: Alert on budget overruns

## 🔒 Security

### Authentication & Authorization
- **JWT Tokens**: Secure session management
- **RBAC**: Role-based access control
- **SSO**: SAML/OpenID Connect support
- **MFA**: Multi-factor authentication

### Data Protection
- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **PII Handling**: Automatic detection and masking
- **Data Retention**: Configurable policies
- **Backup**: Encrypted backups with point-in-time recovery

### Infrastructure Security
- **VPC**: Private subnets with NAT gateways
- **WAF**: Web application firewall
- **Security Groups**: Least-privilege access
- **Secrets**: AWS Secrets Manager

## 📈 Performance

### Benchmarks
- **Transcription**: ~2x audio length (60 min audio = 30 min processing)
- **Embedding**: <5 seconds for typical meeting
- **Analysis**: <10 seconds per template
- **Search**: <100ms for semantic queries

### Optimization
- **Database**: Optimized indexes and queries
- **Caching**: Redis for frequently accessed data
- **CDN**: CloudFront for static assets
- **Compression**: Gzip/Brotli for API responses

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run quality checks: `make lint && make test`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Create Pull Request

### Code Standards
- **Python**: Black formatting, Ruff linting, MyPy type checking
- **TypeScript**: ESLint + Prettier, strict TypeScript config
- **Commits**: Conventional commit messages
- **Documentation**: Update README and API docs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)

### Community
- **Issues**: [GitHub Issues](https://github.com/your-org/meeting-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/meeting-ai/discussions)
- **Discord**: [Community Server](https://discord.gg/meeting-ai)

### Professional Support
For enterprise support, custom integrations, or consulting:
- **Email**: support@meeting-ai.com
- **Website**: https://meeting-ai.com
- **Calendar**: [Book a consultation](https://meeting-ai.com/contact)

---

## 🎯 Roadmap

### Current Version (v1.0)
- ✅ Core transcription and analysis
- ✅ Semantic search and Q&A
- ✅ 9 analysis templates
- ✅ Web interface and API

### Next Release (v1.1)
- 🔄 Real-time transcription
- 🔄 Speaker diarization improvements
- 🔄 Mobile app (React Native)
- 🔄 Slack/Teams integrations

### Future (v2.0)
- 📋 Custom template builder
- 📋 Advanced analytics dashboard
- 📋 Multi-language support
- 📋 On-premise deployment option

---

**Built with ❤️ by the Meeting AI Team**