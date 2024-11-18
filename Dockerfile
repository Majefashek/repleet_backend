# Start from the official Essentia image
FROM ubuntu:22.04

FROM mtgupf/essentia

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    libsndfile1 \
    ffmpeg

#RUN pip install --no-cache-dir essentia-tensorflow

# Set environment variables for Django
ENV PYTHONUNBUFFERED=1

# Copy your Django project to the container
COPY . /app

# Set the working directory
WORKDIR /app

# Install Django and other Python dependencies
RUN pip install --no-cache-dir --timeout=100 -r requirements.txt

# Expose the port that Django will run on
EXPOSE 9000

# Run Django's development server
CMD ["sh", "-c", "python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:9000"]