# Frontend Integration Guide

This guide provides detailed instructions for integrating a React frontend with the Social Network backend API.

## Table of Contents
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [GraphQL Setup](#graphql-setup)
- [REST API Setup](#rest-api-setup)
- [WebSocket Setup](#websocket-setup)
- [File Uploads](#file-uploads)
- [Example Implementations](#example-implementations)

## API Endpoints

### Base URLs
- **REST API**: `http://localhost:8000/api/`
- **GraphQL**: `http://localhost:8000/graphql/`
- **WebSocket**: `ws://localhost:8000/ws/`

### CORS Configuration
The backend is configured to accept requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

To add more origins, update the `CORS_ALLOWED_ORIGINS` in `.env`.

## Authentication

### JWT Token Authentication

The backend uses JWT (JSON Web Tokens) for authentication.

#### Obtaining Tokens (REST)

```javascript
// POST /api/token/
const getTokens = async (email, password) => {
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();
  // Returns: { access: 'token...', refresh: 'token...' }
  return data;
};
```

#### Storing Tokens

```javascript
// Store tokens in localStorage
localStorage.setItem('accessToken', data.access);
localStorage.setItem('refreshToken', data.refresh);
```

#### Using Tokens in Requests

```javascript
const authFetch = async (url, options = {}) => {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  return response;
};
```

#### Refreshing Tokens

```javascript
const refreshToken = async () => {
  const refresh = localStorage.getItem('refreshToken');

  const response = await fetch('http://localhost:8000/api/token/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh }),
  });

  const data = await response.json();
  localStorage.setItem('accessToken', data.access);
  return data.access;
};
```

## GraphQL Setup

### Using Apollo Client

#### Installation

```bash
npm install @apollo/client graphql
```

#### Apollo Client Configuration

```javascript
// src/apollo/client.js
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

const httpLink = createHttpLink({
  uri: 'http://localhost:8000/graphql/',
});

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('accessToken');
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    }
  };
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});

export default client;
```

#### App Setup

```javascript
// src/App.js
import { ApolloProvider } from '@apollo/client';
import client from './apollo/client';

function App() {
  return (
    <ApolloProvider client={client}>
      {/* Your app components */}
    </ApolloProvider>
  );
}
```

#### Example Queries

```javascript
// src/graphql/queries.js
import { gql } from '@apollo/client';

export const GET_ME = gql`
  query GetMe {
    me {
      id
      username
      email
      bio
      avatar
    }
  }
`;

export const GET_FEED = gql`
  query GetFeed {
    feed {
      id
      content
      author {
        id
        username
        avatar
      }
      likeCount
      commentCount
      createdAt
    }
  }
`;

export const GET_CONVERSATIONS = gql`
  query GetConversations {
    conversations {
      id
      name
      conversationType
      participants {
        id
        username
        avatar
      }
      lastMessage {
        content
        createdAt
      }
    }
  }
`;
```

#### Example Mutations

```javascript
// src/graphql/mutations.js
import { gql } from '@apollo/client';

export const CREATE_POST = gql`
  mutation CreatePost($content: String!) {
    createPost(input: { content: $content }) {
      post {
        id
        content
        author {
          username
        }
        createdAt
      }
    }
  }
`;

export const FOLLOW_USER = gql`
  mutation FollowUser($userId: ID!) {
    followUser(userId: $userId) {
      success
      message
    }
  }
`;
```

#### Using in Components

```javascript
// src/components/Feed.js
import { useQuery, useMutation } from '@apollo/client';
import { GET_FEED } from '../graphql/queries';
import { CREATE_POST } from '../graphql/mutations';

function Feed() {
  const { loading, error, data, refetch } = useQuery(GET_FEED);
  const [createPost] = useMutation(CREATE_POST, {
    onCompleted: () => refetch(),
  });

  const handleCreatePost = async (content) => {
    await createPost({ variables: { content } });
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div>
      {data.feed.map(post => (
        <div key={post.id}>
          <p>{post.author.username}</p>
          <p>{post.content}</p>
          <p>Likes: {post.likeCount}</p>
        </div>
      ))}
    </div>
  );
}
```

## REST API Setup

### Using Axios

#### Installation

```bash
npm install axios
```

#### Axios Configuration

```javascript
// src/api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(
          'http://localhost:8000/api/token/refresh/',
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem('accessToken', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

#### Example API Calls

```javascript
// src/api/posts.js
import api from './axios';

export const getPosts = () => api.get('/posts/');

export const createPost = (data) => api.post('/posts/', data);

export const likePost = (postId) => api.post(`/posts/${postId}/like/`);

export const getFeed = () => api.get('/posts/feed/');

// src/api/users.js
export const getUsers = () => api.get('/auth/users/');

export const followUser = (userId) => api.post(`/auth/users/${userId}/follow/`);

export const unfollowUser = (userId) => api.post(`/auth/users/${userId}/unfollow/`);
```

## WebSocket Setup

### Chat WebSocket Connection

```javascript
// src/utils/websocket.js
class ChatWebSocket {
  constructor(conversationId, token) {
    this.conversationId = conversationId;
    this.token = token;
    this.ws = null;
    this.messageHandlers = [];
    this.typingHandlers = [];
  }

  connect() {
    const wsUrl = `ws://localhost:8000/ws/chat/${this.conversationId}/`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'chat_message':
          this.messageHandlers.forEach(handler => handler(data.message));
          break;
        case 'typing_event':
          this.typingHandlers.forEach(handler => handler(data));
          break;
        case 'message_read':
          // Handle read receipt
          break;
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect
      setTimeout(() => this.connect(), 3000);
    };
  }

  sendMessage(content) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'chat_message',
        content: content,
      }));
    }
  }

  startTyping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'typing_start',
      }));
    }
  }

  stopTyping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'typing_stop',
      }));
    }
  }

  markMessageRead(messageId) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'message_read',
        message_id: messageId,
      }));
    }
  }

  onMessage(handler) {
    this.messageHandlers.push(handler);
  }

  onTyping(handler) {
    this.typingHandlers.push(handler);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

export default ChatWebSocket;
```

### Using WebSocket in React

```javascript
// src/components/ChatRoom.js
import React, { useState, useEffect, useRef } from 'react';
import ChatWebSocket from '../utils/websocket';

function ChatRoom({ conversationId }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [typingUsers, setTypingUsers] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    const ws = new ChatWebSocket(conversationId, token);

    ws.onMessage((message) => {
      setMessages(prev => [...prev, message]);
    });

    ws.onTyping((data) => {
      if (data.is_typing) {
        setTypingUsers(prev => [...prev, data.username]);
      } else {
        setTypingUsers(prev => prev.filter(u => u !== data.username));
      }
    });

    ws.connect();
    wsRef.current = ws;

    return () => {
      ws.disconnect();
    };
  }, [conversationId]);

  const handleSend = () => {
    if (inputValue.trim() && wsRef.current) {
      wsRef.current.sendMessage(inputValue);
      setInputValue('');
      wsRef.current.stopTyping();
    }
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    if (wsRef.current) {
      wsRef.current.startTyping();
    }
  };

  return (
    <div>
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx}>
            <strong>{msg.sender.username}:</strong> {msg.content}
          </div>
        ))}
      </div>

      {typingUsers.length > 0 && (
        <div>{typingUsers.join(', ')} is typing...</div>
      )}

      <input
        value={inputValue}
        onChange={handleInputChange}
        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}
```

## File Uploads

### Uploading Images with Posts

```javascript
// Using FormData for file uploads
const uploadPost = async (content, imageFile) => {
  const formData = new FormData();
  formData.append('content', content);
  if (imageFile) {
    formData.append('image', imageFile);
  }

  const token = localStorage.getItem('accessToken');
  const response = await fetch('http://localhost:8000/api/posts/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });

  return await response.json();
};
```

### File Upload Component

```javascript
// src/components/PostCreate.js
import React, { useState } from 'react';

function PostCreate() {
  const [content, setContent] = useState('');
  const [image, setImage] = useState(null);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('content', content);
    if (image) {
      formData.append('image', image);
    }

    const token = localStorage.getItem('accessToken');
    const response = await fetch('http://localhost:8000/api/posts/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (response.ok) {
      setContent('');
      setImage(null);
      // Refresh feed
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="What's on your mind?"
      />
      <input
        type="file"
        accept="image/*"
        onChange={handleImageChange}
      />
      <button type="submit">Post</button>
    </form>
  );
}
```

## Example Implementations

### Complete Auth Context

```javascript
// src/context/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      try {
        const response = await axios.get('http://localhost:8000/api/auth/users/me/', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      }
    }
    setLoading(false);
  };

  const login = async (email, password) => {
    const response = await axios.post('http://localhost:8000/api/token/', {
      email,
      password,
    });

    localStorage.setItem('accessToken', response.data.access);
    localStorage.setItem('refreshToken', response.data.refresh);
    await checkAuth();
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  const register = async (userData) => {
    await axios.post('http://localhost:8000/api/auth/register/', userData);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, register, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Protected Route Component

```javascript
// src/components/ProtectedRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  return user ? children : <Navigate to="/login" />;
}

export default ProtectedRoute;
```

## Best Practices

1. **Token Management**
   - Store tokens securely
   - Implement automatic token refresh
   - Clear tokens on logout

2. **Error Handling**
   - Handle network errors gracefully
   - Show user-friendly error messages
   - Implement retry logic for failed requests

3. **WebSocket Management**
   - Implement reconnection logic
   - Clean up connections on component unmount
   - Handle connection state in UI

4. **Performance**
   - Implement pagination for large lists
   - Use debouncing for search/typing indicators
   - Cache GraphQL queries appropriately

5. **Security**
   - Never expose tokens in URLs
   - Validate user input before sending
   - Use HTTPS in production

## Troubleshooting

### CORS Issues
If you encounter CORS errors, make sure:
- Backend CORS settings include your frontend URL
- Credentials are properly configured
- Preflight requests are handled

### Authentication Issues
- Verify token is being sent in Authorization header
- Check token expiration
- Ensure refresh token logic is working

### WebSocket Issues
- Check WebSocket URL format
- Verify backend Channels configuration
- Ensure Redis is running

## Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [GraphQL Documentation](https://graphql.org/)
- [Apollo Client Documentation](https://www.apollographql.com/docs/react/)
- [Django Channels Documentation](https://channels.readthedocs.io/)
