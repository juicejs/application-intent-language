FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command
CMD ["python", "-m", "app"]