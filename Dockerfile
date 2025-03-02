# Use the official Python image from the Docker Hub
FROM --platform=$BUILDPLATFORM python:3.13.1-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set the working directory in the container
WORKDIR /flask

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the environment variable for Flask
ENV FLASK_APP=app:app

# Expose the port that the Flask app runs on
EXPOSE 8888

# Run the Flask app explicitly on port 8888
# CMD ["flask", "run", "--host=0.0.0.0", "--port=8888"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8888", "app:app"]