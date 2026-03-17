# Social Network Backend

A complete, production-ready Django backend for a full-featured social network and chat platform with GraphQL and REST API support, real-time messaging, and comprehensive social features.

## Features

### Core Functionality
- **User Authentication & Profiles**
  - JWT-based authentication
  - User registration and login
  - Email verification
  - Social login (Google OAuth)
  - Custom user profiles with avatars and bio

- **Social Networking**
  - Follow/unfollow users
  - Post feeds (text, images)
  - Like and comment on posts
  - Repost functionality
  - Friend requests system

- **Chat/Messaging**
  - 1:1 direct messages
  - Group chats
  - Real-time messaging via WebSockets
  - Typing indicators
  - Message read receipts
  - File/image sharing

- **Real-Time Features**
  - WebSocket support via Django Channels
  - Live chat updates
  - Real-time notifications
  - Typing indicators

- **Notifications**
  - Real-time notifications
  - Notification types: likes, comments, follows, messages, friend requests
  - Mark as read functionality

### Technical Stack
- **Django 5.0.6** - Web framework
- **PostgreSQL** - Database
- **Redis** - Caching, sessions, Channels layer, Celery broker
- **Celery** - Background tasks
- **Django Channels** - WebSocket support
- **GraphQL** (Graphene-Django) - Primary API
- **Django REST Framework** - REST API fallback
- **Docker & Docker Compose** - Containerization

## Project Structure

```
social_network/
├── manage.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── social_network/          # Main project directory
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── celery.py
│   └── schema.py          # GraphQL schema
├── accounts/              # Users & Authentication
├── posts/                 # Social posts
├── chat/                  # Messaging & WebSockets
├── notifications/         # Notifications
└── common/                # Utilities
```

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for local development without Docker)

### Installation with Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd social_chat
```

2. **Create environment file**
```bash
cp .env.example .env
```

3. **Update .env file with your settings**
Edit `.env` and update the following critical settings:
- `SECRET_KEY` - Generate a new secret key
- `JWT_SECRET_KEY` - Generate a new JWT secret
- Database credentials (if needed)
- CORS allowed origins

4. **Build and start services**
```bash
docker-compose up --build -d
```

5. **Run migrations**
```bash
docker-compose exec web python manage.py migrate
```

6. **Create a superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

7. **Access the application**
- API: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- GraphQL Playground: http://localhost:8000/graphql/
- API Documentation: http://localhost:8000/api/docs/

### Local Development Setup (Without Docker)

1. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL and Redis**
Make sure PostgreSQL and Redis are running locally.

4. **Create .env file**
```bash
cp .env.example .env
```
Update database and Redis connection settings.

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
# Terminal 1 - Django server
daphne -b 0.0.0.0 -p 8000 social_network.asgi:application

# Terminal 2 - Celery worker
celery -A social_network worker --loglevel=info

# Terminal 3 - Celery beat
celery -A social_network beat --loglevel=info
```

## API Endpoints

### REST API

#### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/token/` - Obtain JWT token pair
- `POST /api/token/refresh/` - Refresh JWT token

#### Users
- `GET /api/auth/users/` - List all users
- `GET /api/auth/users/{id}/` - Get user details
- `GET /api/auth/users/me/` - Get current user
- `POST /api/auth/users/{id}/follow/` - Follow a user
- `POST /api/auth/users/{id}/unfollow/` - Unfollow a user

#### Posts
- `GET /api/posts/` - List posts
- `POST /api/posts/` - Create a post
- `GET /api/posts/{id}/` - Get post details
- `POST /api/posts/{id}/like/` - Like a post
- `POST /api/posts/{id}/unlike/` - Unlike a post
- `GET /api/posts/feed/` - Get personalized feed
- `POST /api/posts/{id}/repost/` - Repost a post

#### Chat
- `GET /api/chat/conversations/` - List conversations
- `POST /api/chat/conversations/` - Create conversation
- `GET /api/chat/conversations/{id}/messages/` - Get messages
- `POST /api/chat/conversations/{id}/send_message/` - Send message

#### Notifications
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/unread/` - Get unread notifications
- `POST /api/notifications/mark_all_read/` - Mark all as read
- `POST /api/notifications/{id}/mark_read/` - Mark one as read

### GraphQL API

GraphQL endpoint: `http://localhost:8000/graphql/`

#### Example Queries

```graphql
# Get current user
query {
  me {
    id
    username
    email
    bio
  }
}

# Get feed
query {
  feed {
    id
    content
    author {
      username
    }
    likeCount
    commentCount
  }
}

# Get conversations
query {
  conversations {
    id
    name
    participants {
      username
    }
    lastMessage {
      content
    }
  }
}
```

#### Example Mutations

```graphql
# Register user
mutation {
  register(input: {
    username: "newuser"
    email: "user@example.com"
    password: "securepassword"
  }) {
    user {
      id
      username
    }
    token
  }
}

# Create post
mutation {
  createPost(input: {
    content: "Hello, world!"
  }) {
    post {
      id
      content
      author {
        username
      }
    }
  }
}

# Follow user
mutation {
  followUser(userId: "1") {
    success
    message
  }
}
```

### WebSocket Endpoints

- `ws://localhost:8000/ws/chat/{conversation_id}/` - Chat room WebSocket

WebSocket message types:
- `chat_message` - Send/receive chat messages
- `typing_start` - User started typing
- `typing_stop` - User stopped typing
- `message_read` - Mark message as read

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CORS_ALLOWED_ORIGINS` - Allowed CORS origins
- `USE_S3` - Enable AWS S3 storage (True/False)
- `EMAIL_BACKEND` - Email backend configuration

### CORS Configuration

Update `CORS_ALLOWED_ORIGINS` in `.env` to include your frontend URL:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/`

Features:
- User management
- Content moderation
- View and manage posts, comments, messages
- Monitor notifications

## Testing

Run tests with pytest:

```bash
# With Docker
docker-compose exec web pytest

# Local
pytest

# With coverage
pytest --cov=.
```

## Production Deployment

1. **Update settings**
   - Set `DEBUG=False`
   - Update `ALLOWED_HOSTS`
   - Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
   - Configure production database
   - Set up AWS S3 for media storage (optional)

2. **Enable HTTPS**
   - Set `SECURE_SSL_REDIRECT=True`
   - Configure SSL certificates

3. **Set up email**
   - Configure email backend for production
   - Update email settings in `.env`

4. **Run collectstatic**
```bash
python manage.py collectstatic --noinput
```

5. **Use production server**
   - Use Gunicorn/uWSGI for WSGI
   - Use Daphne for ASGI (WebSocket support)

## Documentation

- **API Documentation**: Available at `/api/docs/` (Swagger UI)
- **GraphQL Playground**: Available at `/graphql/` (in DEBUG mode)
- **Frontend Integration Guide**: See [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### WebSocket Issues
- Ensure Daphne is running (not Django's runserver)
- Check Redis is properly configured for Channels
- Verify ASGI configuration in `asgi.py`

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.