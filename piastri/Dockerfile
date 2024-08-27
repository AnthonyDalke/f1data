# Use an official Python runtime as a parent image
FROM python:3.9.18-slim-bookworm

# Set the working directory in the container to /app
WORKDIR /app

# Set the Python path to include /app
ENV PYTHONPATH /app:$PYTHONPATH

# Add the current directory contents into the container at /app
ADD . /app

# Create a virtual environment
RUN python -m venv venv

# Activate the virtual environment and install dependencies
RUN . venv/bin/activate && pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Run etl.py when the container launches
CMD ["python", "-m", "src.etl"]