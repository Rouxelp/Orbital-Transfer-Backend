#!/bin/bash

# Check the first argument to determine the command to execute
if [ "$1" = "fastapi" ]; then
    echo "Starting FastAPI app..."
    # Launch the FastAPI application with uvicorn
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000

elif [ "$1" = "pytest" ]; then
    echo "Running tests with pytest..."
    # Run tests using pytest
    exec pytest --maxfail=1 --disable-warnings -v

elif [ "$1" = "bash" ]; then
    echo "Starting interactive bash shell..."
    # Launch a bash shell for debugging or manual commands
    exec /bin/bash

else
    # Display an error message for invalid commands
    echo "Invalid command. Use 'fastapi' to start the app, 'pytest' to run tests, or 'bash' for an interactive shell."
    exit 1
fi
