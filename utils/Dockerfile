FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Show requirements content for debugging
RUN echo "=== Requirements file content ===" && cat requirements.txt

# Install dependencies with verbose output
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Verify installation
RUN python -c "import telegram; print('✅ Telegram module installed successfully!')"

# Copy application code
COPY . .

# Create temp directory
RUN mkdir -p temp

# Expose port
EXPOSE 5000

# Run the bot
CMD ["python", "-u", "bot.py"]
