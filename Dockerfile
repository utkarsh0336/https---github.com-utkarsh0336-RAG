FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose ports
EXPOSE 8501 8000

# Default command (can be overridden in docker-compose)
CMD ["streamlit", "run", "src/ui/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
