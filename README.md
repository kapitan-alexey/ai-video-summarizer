# AI Video Summarizer

Telegram bot that automatically summarizes YouTube videos and enables intelligent Q&A conversations about video content using AI.

## How It Works

1. **Video Processing**: User shares a YouTube video link with the bot
2. **Transcript Extraction**: Bot extracts video subtitles using YouTube Transcript API
3. **AI Summarization**: OpenAI generates a concise summary of the video content
4. **Vector Storage**: Video transcript is split into chunks, embedded, and stored in Pinecone vector database
5. **Interactive Discussion**: Users can ask questions about the video, and the bot retrieves relevant context from Pinecone to provide accurate answers using RAG (Retrieval-Augmented Generation)

## Tech Stack

### Core Technologies
- **Python 3.10** - Main programming language
- **aiogram 2.25** - Telegram Bot API framework
- **LangChain** - Framework for building LLM applications

### AI & ML
- **OpenAI API** - Text generation and embeddings (gpt-3.5/gpt-4)
- **Pinecone** - Vector database for semantic search and content retrieval
- **youtube-transcript-api** - Extract video transcripts/subtitles

### Storage & Caching
- **Redis** - Caching layer for conversation memory and update validation
- **Pinecone Index** - Persistent vector storage for video embeddings

### Deployment
- **AWS Lambda** - Serverless function execution
- **Docker** - Containerization for Lambda deployment
- **GitHub Actions** - CI/CD pipeline (`.github/workflows/`)

## Deployment

This project runs exclusively on **AWS Lambda** and cannot be executed locally. Deployment is fully automated through GitHub Actions.

### CI/CD Pipeline

The project uses two GitHub Actions workflows for automated deployment:

#### Production Deployment (main branch)
Push to `main` branch triggers:
1. Docker image build
2. Push to Amazon ECR (`video-summary` repository)
3. Update AWS Lambda functions:
   - `video-summary-PROD`
   - `sysdev-PROD`

#### Development Deployment (dev branch)
Push to `dev` branch triggers:
1. Docker image build
2. Push to Amazon ECR
3. Update AWS Lambda function: `video-summary-DEV`

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:
- `AWS_ACCESS_KEY_ID` - AWS access key for ECR and Lambda
- `AWS_SECRET_ACCESS_KEY` - AWS secret key

### AWS Lambda Configuration

Lambda functions must be configured with environment variables:
```
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_PASSWORD=your_redis_password
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENV_KEY=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name
```

## Bot Commands

- `/start` or `/run` - Initialize bot and get welcome message
- `/mockme` - Start a mock system design interview session
- Send any YouTube link - Get video summary and start Q&A

## Key Features

- Automatic YouTube video summarization
- Semantic search through video content
- Conversational Q&A about videos
- Multi-language subtitle support (EN, RU, DE)
- Mock system design interview mode
- Redis-based conversation memory
- Duplicate update prevention

## Project Structure

```
.
├── main.py                 # Entry point and Lambda handler
├── handlers.py             # Message handlers
├── bot.py                  # Bot initialization
├── settings.py             # Configuration management
├── services/
│   ├── summary/           # Video summarization logic
│   ├── discuss/           # Q&A and vector search
│   ├── handlers/          # Handler factories
│   ├── memory/            # Redis memory management
│   └── models/            # Data models
└── requirements.txt       # Python dependencies
```
