# Use an official Python runtime as a parent image
FROM python:3.9.18-slim-bookworm

# Set the working directory in the container to /app
WORKDIR /app

# Set the Python path to include /app
ENV PYTHONPATH /app:$PYTHONPATH

# Copy the files from local storage to the container
COPY . /app

# Upgrade pip and install dependencies directly
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Run etl.py when the container launches
CMD ["python", "-m", "src.etl"]