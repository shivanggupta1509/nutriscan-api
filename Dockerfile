# Dockerfile
# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
# --no-cache-dir speeds up installation by not storing cached packages
# -r installs packages from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application files (app.py, .pkl files, etc.) into the container
# The order matters: copy requirements.txt and install BEFORE copying app code
# to leverage Docker layer caching (if requirements.txt doesn't change, this layer is cached).
COPY . .

# Expose the port that your application will listen on.
# Hugging Face Spaces expects HTTP services to listen on port 7860.
EXPOSE 7860

# Command to run your Flask application using Gunicorn.
# 'app:app' refers to the 'app' Flask instance within the 'app.py' file.
# --bind 0.0.0.0:7860 tells Gunicorn to listen on all network interfaces on port 7860.
# --workers 1 specifies the number of worker processes. Adjust based on your instance's CPU.
# --timeout 120 sets a timeout for worker processes (in seconds). Increase if predictions are very long.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "app:app"]
