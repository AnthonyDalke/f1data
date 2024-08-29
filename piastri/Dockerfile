# Use an official Python runtime as a parent image
FROM python:3.9.18-slim-bookworm

# Set the working directory in the container to /app
WORKDIR /app

# Set the Python path to include /app
ENV PYTHONPATH /app:$PYTHONPATH

# Add the current directory contents into the container at /app
ADD . /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Upgrade pip and install dependencies directly
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run etl.py when the container launches
CMD ["python", "-m", "src.etl"]