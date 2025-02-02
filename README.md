# Sales Dashboard

A real-time sales dashboard application built with Django, Channels, Redis, and PostgreSQL.

## Prerequisites

Before running the project, ensure you have the following installed:

1. Python 3.8 or higher
2. PostgreSQL 12 or higher
3. Redis Server
4. pip (Python package manager)

## Installation Guide

### 1. PostgreSQL Setup

#### Windows
1. Download PostgreSQL installer from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run the installer
3. Set password for postgres user
4. Keep default port (5432)
5. Complete installation

#### Mac OS
```bash
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Redis Setup

#### Windows
1. Download Redis for Windows through [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install)
2. Install Redis in WSL:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start
```

#### Mac OS
```bash
brew install redis
brew services start redis
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 3. Database Setup
1. Open terminal/command prompt
2. Access PostgreSQL:
```bash
# Windows
psql -U postgres

# Mac/Linux
sudo -u postgres psql
```

3. Create database:
```sql
CREATE DATABASE sales_dashboard;
```

### 4. Project Setup

1. Clone the repository:
```bash
git clone [your-repository-url]
cd sales_dashboard
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=sales_dashboard
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379
```

5. Update database settings in `sales_dashboard/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'sales_dashboard'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

6. Create static and media directories:
```bash
mkdir static media
```

7. Apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

8. Create superuser:
```bash
python manage.py createsuperuser
```

9. Collect static files:
```bash
python manage.py collectstatic
```

## Running the Project

1. Ensure Redis server is running:
```bash
# Check Redis status
redis-cli ping
# Should return PONG
```

2. Start the development server:
```bash
python manage.py runserver
```

3. Access the application:
- Main application: http://localhost:8000
- Admin panel: http://localhost:8000/admin

## Project Structure
```
sales_dashboard/
├── dashboard/         # Dashboard app
├── sales/            # Sales app
├── static/           # Static files
├── media/           # Media files
├── templates/       # HTML templates
└── sales_dashboard/ # Project settings
```

## Features
- Real-time sales updates using WebSockets
- Interactive dashboard
- Sales data visualization
- User authentication
- Admin interface for data management

## Common Issues and Solutions

### 1. Database Connection Issues
- Verify PostgreSQL is running:
```bash
# Windows
net start postgresql

# Mac/Linux
sudo systemctl status postgresql
```
- Check database credentials in .env file
- Ensure database exists

### 2. Redis Connection Issues
- Verify Redis is running:
```bash
redis-cli ping
```
- Check Redis connection string in settings.py
- Ensure Redis port (6379) is not blocked

### 3. Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### 4. Migration Issues
```bash
python manage.py migrate --run-syncdb
```

## Development

### Requirements Update
To update requirements.txt:
```bash
pip freeze > requirements.txt
```

### Running Tests
```bash
python manage.py test
```

## Production Deployment Notes

1. Update `.env`:
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

2. Configure proper security settings
3. Use production-grade servers (Gunicorn, Daphne)
4. Set up SSL/TLS certificates
5. Configure proper Redis security


