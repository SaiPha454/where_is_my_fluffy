from fastapi import FastAPI
from .routers.user_route import router as user_router

# Main entry file to run the application
app = FastAPI(
    title="MyFluffy API",
    description="A FastAPI application for MyFluffy",
    version="1.0.0"
)

# Include routers
app.include_router(user_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to MyFluffy API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)