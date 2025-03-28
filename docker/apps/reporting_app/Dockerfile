# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY apps/reporting_app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY apps/reporting_app /app/src/reporting_app

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=src.reporting_app.app
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 8050

# Command to run the application
CMD ["python", "-m", "src.reporting_app.app"]
