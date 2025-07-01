# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev
#build-essential: needed to build Python packages with C extensions
#libpq-dev: required to connect to PostgreSQL

# Copy requirement files
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run the app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#runs the FastAPI app using Uvicorn
# main:app: means FastAPI app object inside main.py
# host 0.0.0.0: makes it accessible to other containers
# reload: auto-reloads on code changes
