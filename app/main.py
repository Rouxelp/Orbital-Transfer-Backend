from fastapi import FastAPI
from app.routes import router

# Initialize the FastAPI app
app = FastAPI(
    title="Orbital Transfer API",
    description="API for managing orbits, trajectories, and orbital transfers",
    version="1.0.0"
)

# Include the router
app.include_router(router)

# Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
