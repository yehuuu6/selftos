FROM ubuntu:22.04

# Update package lists and install necessary tools
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the Python dependencies
RUN pip install -r requirements.txt

# Define the default command to run when the container starts
CMD ["python3", "./room.py"]