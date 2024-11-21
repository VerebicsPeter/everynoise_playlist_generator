# Use an official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg zip

# Clean up
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install
RUN playwright install-deps

# Copy the rest of the application code
COPY . .

# Expose the port the FastAPI app will run on
EXPOSE 8000

# Define the command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
