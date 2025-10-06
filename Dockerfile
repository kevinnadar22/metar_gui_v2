# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend requirements and install them
COPY app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire app folder
COPY app ./app

# Expose port (Flask default 5000)
EXPOSE 5000

# Set environment variable for Flask
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

#  Start Flask app using Gunicorn and your factory structure
WORKDIR /app
CMD ["gunicorn", "--chdir", "backend", "--bind", "0.0.0.0:5000", "app:app"]
