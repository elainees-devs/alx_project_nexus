# Use Python base image 
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


# Copy project files
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Run gunicorn server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

