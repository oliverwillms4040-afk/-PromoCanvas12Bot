FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Show requirements content for debugging
RUN echo "=== Installing dependencies ===" && cat requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Verify installation
RUN python -c "import telegram; print('✅ Telegram installed')" && \
    python -c "import dotenv; print('✅ Dotenv installed')" && \
    python -c "import PIL; print('✅ Pillow installed')"

# Copy application code
COPY . .

# Create temp directory
RUN mkdir -p temp

# Expose port
EXPOSE 5000

# Run the bot
CMD ["python", "-u", "bot.py"]
