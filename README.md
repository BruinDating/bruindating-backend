# BruinDating Chat Application

A real-time chat application built with Django Channels and WebSocket.

## Prerequisites

- Python 3.8 or higher
- Redis
- Node.js (for Tailwind CSS)

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd bruindating-backend
```

### 2. Set up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# For Mac/Linux:
source venv/bin/activate
# For Windows:
.\venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install django
pip install channels
pip install channels-redis
pip install daphne
pip install python-dotenv
pip install djangorestframework
pip install django-cors-headers
```

### 4. Create .env file

```bash
# Create .env file in project root
touch .env

# Add the following to your .env file:
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Redis Setup

Make sure Redis is installed and running:

For Mac (using Homebrew):

```bash
# Install Redis if not already installed
brew install redis

# Start Redis
brew services start redis

# Verify Redis is running
redis-cli ping
# Should return "PONG"
```

For Linux:

```bash
sudo apt-get install redis-server
sudo service redis-server start
```

For Windows:
Download and install Redis from [https://redis.io/download](https://redis.io/download)

### 6. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 7. Running the Application

```bash
# Start the server using daphne
daphne bruindating_backend.asgi:application -p 8000

# Alternatively, you can use uvicorn
uvicorn bruindating_backend.asgi:application --port 8000
```

Visit http://127.0.0.1:8000/ in your browser to use the chat application.

## Features

- Real-time chat functionality
- User join/leave notifications
- Online users list
- Message history
- Multiple chat rooms

## Testing the Chat

1. Open multiple browser windows/tabs
2. Enter the same room name in each window
3. Start chatting to test real-time communication

## Troubleshooting

### Redis Connection Issues

If you see Redis connection errors:

```bash
# Check if Redis is running
redis-cli ping

# Restart Redis if needed
# For Mac:
brew services restart redis
# For Linux:
sudo service redis-server restart
```

### WebSocket Connection Issues

- Make sure you're using daphne or uvicorn to run the server
- Check that Redis is running
- Verify your ASGI configuration in settings.py

### Database Issues

If you see database errors:

```bash
# Reset migrations if needed
python manage.py makemigrations chat
python manage.py migrate
```

## Project Structure
