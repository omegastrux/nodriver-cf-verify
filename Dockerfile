# Use the official Python 3.12 slim image as the base
FROM python:3.12-slim

# Force Python stdout and stderr streams to be unbuffered
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/chromium

# Set the working directory inside the container
WORKDIR /app

# Install Chromium, Xvfb, and Fonts in a single clean layer.
RUN apt-get update && apt-get install -y \
    chromium \
    xvfb \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Execute script wrapped in xvfb-run
CMD ["sh", "-c", "xvfb-run -a python docker_example.py"]