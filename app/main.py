from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers.user_route import router as user_router
from .routers.auth_route import router as auth_router
from .routers.post_route import router as post_router
from .routers.report_route import router as report_router
from .routers.notification_route import router as notification_router
from .db.database import create_tables

# Main entry file to run the application
app = FastAPI(
    title="MyFluffy API",
    description="A FastAPI application for MyFluffy",
    version="1.0.0"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Mount static files directory for serving uploaded images
app.mount("/images", StaticFiles(directory="app/images"), name="images")

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(post_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(notification_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to MyFluffy API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)