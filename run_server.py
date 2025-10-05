#!/usr/bin/env python3
"""
Server runner script for MyFluffy API
Run this script to start the FastAPI server with uvicorn
Usage: python3 run_server.py
"""

import uvicorn
import sys

def main():
    """Main function to run the FastAPI server"""
    
    print("🐕 Starting MyFluffy API Server...")
    print("🌐 Server will be available at:")
    print("   - Local: http://localhost:8000")
    print("   - Network: http://0.0.0.0:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        # Run the server with uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()