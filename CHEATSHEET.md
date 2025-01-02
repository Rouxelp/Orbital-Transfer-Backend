# Docker Cheat Sheet for FastAPI and Pytest

This cheat sheet provides useful Docker commands to work with the FastAPI application and Pytest setup. All commands assume you are using **PowerShell** on Windows.

---

## 🐳 **Build the Docker Image**
Build the Docker image with a specific name (`hohmann-transfer-app`):

```bash
docker build -t hohmann-transfer-app .
```

## 🚀 Run FastAPI Server
Start the FastAPI server and mount the local directory as a volume to reflect code changes:

```bash
docker run -v ${PWD}:/app hohmann-transfer-app fastapi
```

## 🧪 Run Pytest
Run tests using Pytest with the local directory mounted:

```bash
docker run -it -v ${PWD}:/app hohmann-transfer-app pytest
```

## 🖥️ Start a Bash Shell in the Container
Run an interactive Bash shell for debugging:

```bash
docker run -it -v ${PWD}:/app hohmann-transfer-app bash
```

## 🛑 Stop and Remove Containers
Stop and remove all running containers:

```bash
docker stop $(docker ps -q) && docker rm $(docker ps -a -q)
```

## 📋 View Running Containers
List all running containers:

```bash
docker ps
```
