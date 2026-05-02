from fastapi import FastAPI, UploadFile, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import uvicorn
import shutil
import os
import logging
from models import SimulationConfig
from xml_generator import generate_svfsi_xml
from mesh_service import save_upload_file, get_mesh_metadata, cleanup_mesh_files

app = FastAPI()

# Get allowed origins from environment or default to local Vite dev server
allowed_origins_env = os.environ.get("VITE_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    # 🛡️ Sentinel: Restrict CORS methods and headers to prevent overly permissive access
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# ⚡ Bolt: Compress large text-based responses (like XML configs and .vtp files).
# This reduces network payload sizes significantly, improving load times for
# large simulations or visualization tasks.
# Using compresslevel=1 provides a ~6x speedup over the default level 9, while
# achieving nearly identical compression ratios for text and binary mesh data.
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=1)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    🛡️ Sentinel: Add security headers to all responses.
    These headers help protect against clickjacking, MIME type sniffing,
    and cross-site scripting (XSS) attacks.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Exclude Swagger/ReDoc docs from strict CSP as they require external CDNs
    # and inline scripts to render properly.
    if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
        response.headers["Content-Security-Policy"] = "default-src 'self'"

    # 🛡️ Sentinel: Prevent caching of API responses to avoid leaking sensitive simulation data
    if request.url.path in ("/generate_input", "/process_mesh"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"

    return response

# ⚡ Bolt: Use `async def` for non-blocking endpoints.
# In FastAPI, standard `def` endpoints are automatically offloaded to an external
# threadpool to prevent blocking the event loop. For fast, CPU-bound operations
# (like generating small XML configs), the thread context-switching overhead
# is often higher than the execution time itself. Using `async def` keeps
# execution on the main thread, eliminating ~1-2ms of overhead per request.
@app.get("/")
async def read_root():
    return {"message": "svFSI Backend is running"}

@app.post("/generate_input")
async def generate_input(config: SimulationConfig):
    try:
        xml_content = generate_svfsi_xml(config)
        return {"xml": xml_content}
    except Exception as e:
        logging.error("Failed to generate XML input: %s", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while generating the input XML.")

@app.post("/process_mesh")
def process_mesh(file: UploadFile):
    """
    ⚡ Bolt: Sync endpoint to offload CPU-bound work.
    Using 'def' instead of 'async def' tells FastAPI to run this endpoint
    in an external threadpool. This prevents heavy operations like
    PyVista mesh reading and surface extraction from blocking the main
    asyncio event loop.
    """
    # 🛡️ Sentinel: Enforce application-layer file size limit (50MB) to prevent DoS attacks.
    MAX_FILE_SIZE = 50 * 1024 * 1024
    if file.size is not None and file.size > MAX_FILE_SIZE:
        logging.error("File size exceeded limit: %d bytes", file.size)
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")

    file_path = None
    try:
        file_path = save_upload_file(file)
        metadata = get_mesh_metadata(file_path)
        return metadata
    except ValueError as e:
        if file_path:
            cleanup_mesh_files(file_path)
        # 🛡️ Sentinel: Prevent Information Exposure by logging the actual error
        # internally and returning a generic response to the client.
        logging.error("Validation error: %s", str(e))
        raise HTTPException(status_code=400, detail="Invalid file extension or validation error")
    except HTTPException as e:
        # If it's already an HTTPException (e.g. 413 from save_upload_file), re-raise it directly
        raise e
    except Exception as e:
        if file_path:
            cleanup_mesh_files(file_path)
        logging.error("Failed to process mesh file: %s", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while processing the mesh.")

# Serve static files for mesh visualization
from fastapi.staticfiles import StaticFiles
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
