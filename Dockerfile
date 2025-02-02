FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make entrypoint executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Collect static files
RUN python manage.py collectstatic --noinput

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Run daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "sales_dashboard.asgi:application"] 