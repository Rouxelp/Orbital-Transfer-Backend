FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copyequirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the entrypoint script and make the entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Define the default entrypoint for the container
ENTRYPOINT ["/entrypoint.sh"]
