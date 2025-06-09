# Meeting AI - Architecture Documentation

## Overview

Meeting AI is a cloud-native, microservices-based platform designed for high-scale meeting intelligence processing. This document provides detailed architectural insights for developers, DevOps engineers, and system architects.

## System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Application]
        MOBILE[Mobile App]
        API_CLIENT[API Clients]
    end
    
    subgraph "Load Balancing"
        ALB[Application Load Balancer]
        CF[CloudFront CDN]
    end
    
    subgraph "Application Layer"
        API[FastAPI Backend]
        WORKERS[Celery Workers]
        SCHEDULER[Celery Beat]
    end
    
    subgraph "Processing Layer"
        SF[Step Functions]
        LAMBDA[Lambda Functions]
        BATCH[AWS Batch]
    end
    
    subgraph "AI Services"
        WHISPER[OpenAI Whisper]
        EMBEDDING[Embedding Service]
        GEMINI[Google Gemini]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL + pgvector)]
        REDIS[(Redis)]
        S3[(S3 Storage)]
        SECRETS[Secrets Manager]
    end
    
    subgraph "Monitoring"
        CW[CloudWatch]
        XRAY[X-Ray]
        PROM[Prometheus]
    end
    
    WEB --> CF
    MOBILE --> ALB
    API_CLIENT --> ALB
    CF --> ALB
    ALB --> API
    
    API --> PG
    API --> REDIS
    API --> S3
    API --> WORKERS
    
    WORKERS --> SF
    SF --> LAMBDA
    SF --> BATCH
    
    LAMBDA --> WHISPER
    LAMBDA --> EMBEDDING
    LAMBDA --> GEMINI
    
    API --> CW
    API --> XRAY
    WORKERS --> PROM
```

## Component Architecture

### Frontend Architecture (Next.js 14)

```mermaid
graph TB
    subgraph "Browser"
        UI[User Interface]
    end
    
    subgraph "Next.js App Router"
        PAGES[Pages/Routes]
        LAYOUTS[Layouts]
        COMPONENTS[Components]
    end
    
    subgraph "State Management"
        QUERY[TanStack Query]
        ZUSTAND[Zustand Store]
        CONTEXT[React Context]
    end
    
    subgraph "Services"
        API_CLIENT[API Client]
        WS[WebSocket Client]
        AUTH[Auth Service]
    end
    
    UI --> PAGES
    PAGES --> LAYOUTS
    LAYOUTS --> COMPONENTS
    COMPONENTS --> QUERY
    COMPONENTS --> ZUSTAND
    QUERY --> API_CLIENT
    WS --> COMPONENTS
    AUTH --> CONTEXT
```

**Key Design Decisions:**
- **App Router**: Leverages Next.js 14's new routing system for better performance
- **Server Components**: Reduces client-side JavaScript bundle size
- **Streaming**: Progressive page loading for better perceived performance
- **TypeScript**: Full type safety across the application

### Backend Architecture (FastAPI)

```mermaid
graph TB
    subgraph "API Layer"
        ROUTER[API Routers]
        MIDDLEWARE[Middleware Stack]
        DEPS[Dependencies]
    end
    
    subgraph "Business Logic"
        SERVICES[Services]
        MODELS[Pydantic Models]
        SCHEMAS[Response Schemas]
    end
    
    subgraph "Data Access"
        ORM[SQLAlchemy ORM]
        MIGRATIONS[Alembic Migrations]
        REPOS[Repository Pattern]
    end
    
    subgraph "Background Processing"
        CELERY[Celery Tasks]
        BEAT[Celery Beat]
        MONITOR[Flower Monitoring]
    end
    
    ROUTER --> SERVICES
    MIDDLEWARE --> ROUTER
    DEPS --> SERVICES
    SERVICES --> MODELS
    SERVICES --> ORM
    ORM --> REPOS
    SERVICES --> CELERY
    BEAT --> CELERY
```

**Key Design Patterns:**
- **Dependency Injection**: Clean separation of concerns
- **Repository Pattern**: Abstracted data access layer
- **Service Layer**: Business logic encapsulation
- **Async/Await**: Non-blocking I/O operations

## Data Architecture

### Database Design

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email UK
        string full_name
        string role
        boolean is_active
        timestamp created_at
    }
    
    MEETINGS {
        uuid id PK
        string title
        text description
        timestamp scheduled_at
        integer duration_seconds
        json participants
        string status
        string processing_status
        string s3_audio_uri
        float processing_cost_usd
        timestamp created_at
    }
    
    SEGMENTS {
        uuid id PK
        uuid meeting_id FK
        integer sequence_number
        float start_time_seconds
        float end_time_seconds
        text content
        string speaker
        vector embedding
        timestamp created_at
    }
    
    INSIGHTS {
        uuid id PK
        uuid meeting_id FK
        string insight_type
        string title
        text content
        json data
        float confidence_score
        timestamp created_at
    }
    
    TEMPLATE_RUNS {
        uuid id PK
        uuid meeting_id FK
        string template_type
        text system_prompt
        text user_prompt
        text raw_response
        json structured_output
        integer total_tokens
        float cost_usd
        timestamp created_at
    }
    
    USERS ||--o{ MEETINGS : organizes
    MEETINGS ||--o{ SEGMENTS : contains
    MEETINGS ||--o{ INSIGHTS : generates
    MEETINGS ||--o{ TEMPLATE_RUNS : processes
    TEMPLATE_RUNS ||--o{ INSIGHTS : creates
```

### Vector Storage Strategy

**pgvector Implementation:**
- **Embedding Dimension**: 1536 (OpenAI text-embedding-3-small)
- **Index Type**: IVFFlat with 100 lists for <1M vectors
- **Distance Metric**: Cosine similarity for semantic search
- **Chunking Strategy**: 256 tokens with 32 token overlap

```sql
-- Vector index creation
CREATE INDEX ix_segments_embedding_ivfflat 
ON segments USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Semantic search query
SELECT id, content, 1 - (embedding <=> $1::vector) as similarity
FROM segments 
WHERE 1 - (embedding <=> $1::vector) > $2
ORDER BY similarity DESC 
LIMIT $3;
```

## Processing Architecture

### Audio Processing Pipeline

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant S3
    participant StepFunctions
    participant Whisper
    participant Embedding
    participant Gemini
    participant Database
    
    Client->>API: Upload audio file
    API->>S3: Store raw audio
    API->>StepFunctions: Trigger processing
    
    StepFunctions->>Whisper: Transcribe audio
    Whisper-->>StepFunctions: Return transcript
    
    StepFunctions->>Embedding: Generate embeddings
    Embedding-->>StepFunctions: Return vectors
    
    StepFunctions->>Gemini: Analyze with templates
    Gemini-->>StepFunctions: Return insights
    
    StepFunctions->>Database: Store results
    StepFunctions->>API: Webhook completion
    API-->>Client: Processing complete
```

### Step Functions State Machine

```json
{
  "Comment": "Meeting processing pipeline",
  "StartAt": "TranscribeAudio",
  "States": {
    "TranscribeAudio": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:whisper-processor",
      "Retry": [{"ErrorEquals": ["States.ALL"], "MaxAttempts": 3}],
      "Next": "ChunkAndEmbed"
    },
    "ChunkAndEmbed": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:embedding-processor",
      "Next": "AnalyzeTemplates"
    },
    "AnalyzeTemplates": {
      "Type": "Map",
      "ItemsPath": "$.templates",
      "MaxConcurrency": 5,
      "Iterator": {
        "StartAt": "ProcessTemplate",
        "States": {
          "ProcessTemplate": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:region:account:function:template-processor",
            "End": true
          }
        }
      },
      "Next": "StoreResults"
    },
    "StoreResults": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:result-processor",
      "End": true
    }
  }
}
```

## Infrastructure Architecture

### AWS Infrastructure

```mermaid
graph TB
    subgraph "VPC"
        subgraph "Public Subnets"
            ALB[Application Load Balancer]
            NAT[NAT Gateway]
        end
        
        subgraph "Private Subnets"
            ECS[ECS Fargate]
            RDS[(RDS PostgreSQL)]
            REDIS[(ElastiCache Redis)]
            LAMBDA[Lambda Functions]
        end
    end
    
    subgraph "Storage"
        S3[S3 Buckets]
        EFS[EFS File System]
    end
    
    subgraph "Monitoring"
        CW[CloudWatch]
        XRAY[X-Ray]
        SNS[SNS Notifications]
    end
    
    Internet --> ALB
    ALB --> ECS
    ECS --> RDS
    ECS --> REDIS
    ECS --> S3
    LAMBDA --> RDS
    LAMBDA --> S3
    
    ECS --> CW
    LAMBDA --> XRAY
    CW --> SNS
```

### Container Architecture

**Backend Container (ECS Fargate)**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Frontend Container (ECS Fargate)**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

## Security Architecture

### Network Security

```mermaid
graph TB
    subgraph "Internet"
        USERS[Users]
    end
    
    subgraph "AWS Cloud"
        subgraph "CloudFront + WAF"
            CF[CloudFront CDN]
            WAF[Web Application Firewall]
        end
        
        subgraph "VPC (10.0.0.0/16)"
            subgraph "Public Subnets"
                ALB[Application Load Balancer]
                NAT[NAT Gateway]
            end
            
            subgraph "Private Subnets"
                APP[Application Servers]
                DB[(Database)]
            end
        end
    end
    
    USERS --> WAF
    WAF --> CF
    CF --> ALB
    ALB --> APP
    APP --> DB
    APP --> NAT
    NAT --> Internet
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Auth0
    participant Database
    
    User->>Frontend: Login request
    Frontend->>Auth0: Redirect to Auth0
    Auth0->>User: Present login form
    User->>Auth0: Submit credentials
    Auth0->>Frontend: Return auth code
    Frontend->>Backend: Exchange code for tokens
    Backend->>Auth0: Validate token
    Auth0-->>Backend: Token valid
    Backend->>Database: Create/update user
    Backend-->>Frontend: Return JWT
    Frontend-->>User: Login successful
```

## Monitoring Architecture

### Observability Stack

```mermaid
graph TB
    subgraph "Application Metrics"
        PROM[Prometheus]
        GRAFANA[Grafana]
        ALERT[Alertmanager]
    end
    
    subgraph "AWS Monitoring"
        CW[CloudWatch]
        XRAY[X-Ray]
        CWL[CloudWatch Logs]
    end
    
    subgraph "Business Metrics"
        CUSTOM[Custom Metrics]
        COST[Cost Tracking]
        SLA[SLA Monitoring]
    end
    
    Applications --> PROM
    Applications --> CW
    Applications --> XRAY
    
    PROM --> GRAFANA
    PROM --> ALERT
    CW --> GRAFANA
    
    CUSTOM --> PROM
    COST --> CW
    SLA --> ALERT
```

### Key Metrics

**Application Metrics:**
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Database connection pool usage
- Cache hit/miss ratios

**Business Metrics:**
- Meetings processed per hour
- Average processing time
- AI service costs per meeting
- User engagement metrics

**Infrastructure Metrics:**
- CPU and memory utilization
- Database query performance
- Storage usage and growth
- Network throughput

## Scalability Considerations

### Horizontal Scaling

**Frontend:**
- CloudFront CDN for global distribution
- Multiple ECS tasks across availability zones
- Auto-scaling based on CPU/memory metrics

**Backend:**
- Load balancer with health checks
- ECS service auto-scaling
- Database read replicas
- Redis cluster mode

**Processing:**
- Lambda functions for burst capacity
- SQS queues for task distribution
- Step Functions for workflow orchestration
- Batch jobs for large-scale processing

### Performance Optimization

**Database:**
- Connection pooling (20 connections per instance)
- Query optimization with EXPLAIN plans
- Materialized views for analytics
- Partitioning for large tables

**Caching Strategy:**
- Redis for session data (TTL: 30 minutes)
- Application-level caching for API responses
- CDN caching for static assets
- Database query result caching

## Disaster Recovery

### Backup Strategy

**Database:**
- Automated daily backups with 7-day retention
- Point-in-time recovery capability
- Cross-region backup replication
- Backup encryption with AWS KMS

**Storage:**
- S3 cross-region replication
- Versioning enabled on all buckets
- Lifecycle policies for cost optimization
- Glacier Deep Archive for long-term retention

### Recovery Procedures

**RTO/RPO Targets:**
- Database: RTO < 4 hours, RPO < 1 hour
- Application: RTO < 1 hour, RPO < 15 minutes
- Storage: RTO < 2 hours, RPO < 24 hours

## Cost Optimization

### Resource Optimization

**Compute:**
- Spot instances for non-critical workloads
- Reserved instances for baseline capacity
- Lambda for variable workloads
- ECS Fargate for container orchestration

**Storage:**
- S3 Intelligent Tiering
- EBS gp3 volumes with optimized IOPS
- CloudFront for bandwidth optimization
- Data compression and deduplication

### Cost Monitoring

**Budget Controls:**
- AWS Budgets with alerts at 80%, 100%
- Cost anomaly detection
- Resource tagging for cost allocation
- Monthly cost reviews and optimization

---

This architecture documentation provides the foundation for understanding, maintaining, and evolving the Meeting AI platform. For specific implementation details, refer to the individual service documentation.