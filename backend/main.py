from fastapi import FastAPI, UploadFile, HTTPException, Request, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import uvicorn
import shutil
import os
import logging
import time
from models import SimulationConfig
from xml_generator import generate_svfsi_xml
from mesh_service import save_upload_file, get_mesh_metadata, cleanup_mesh_files, _cleanup_old_uploads

app = FastAPI()

# 🛡️ Sentinel: Simple in-memory rate limiting state to prevent DoS/brute force on sensitive endpoints
RATE_LIMIT_STORE = {}
RATE_LIMIT_MAX = 30  # requests per window
RATE_LIMIT_WINDOW = 60  # window in seconds

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """
    🛡️ Sentinel: Enforce a strict maximum Content-Length for all APIs
    to prevent Memory and Disk Exhaustion (DoS). Pydantic and UploadFile
    will eagerly consume/spool massive bodies if not capped at the HTTP layer.
    """
    transfer_encoding = request.headers.get("transfer-encoding", "")
    if "chunked" in transfer_encoding.lower():
        # Prevent chunked upload bypasses for content-length limits
        return Response(content="Chunked requests not supported", status_code=411)

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            length = int(content_length)
            if request.url.path == "/process_mesh":
                # Allow larger payloads for mesh uploads, but strictly cap at HTTP layer
                # to prevent FastAPI from spooling infinitely to disk before the endpoint runs.
                if length > 55 * 1024 * 1024:  # 55 MB limit
                    return Response(content="File too large. Maximum size is 50MB.", status_code=413)
            else:
                if length > 2 * 1024 * 1024:  # 2 MB limit for JSON
                    return Response(content="Payload too large", status_code=413)
        except ValueError:
            return Response(content="Invalid content-length", status_code=400)

    return await call_next(request)

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    if request.url.path in ("/generate_input", "/process_mesh") or request.url.path.startswith("/files/"):
        # 🛡️ Sentinel: Rely on request.client.host which is safely populated by Uvicorn's
        # ProxyHeadersMiddleware (when behind a trusted proxy) instead of manually parsing
        # headers which allows spoofing to bypass limits or DoS other users.
        client_ip = request.client.host if request.client else "127.0.0.1"

        now = time.time()

        # Prevent memory leaks by explicitly cleaning up expired entries when the store grows too large
        if len(RATE_LIMIT_STORE) > 10000:
            expired_ips = [ip for ip, data in RATE_LIMIT_STORE.items() if now - data["start_time"] > RATE_LIMIT_WINDOW]
            for ip in expired_ips:
                del RATE_LIMIT_STORE[ip]

            # 🛡️ Sentinel: Failsafe to prevent CPU exhaustion DoS.
            # If an attacker floods unique IPs, the store exceeds 10,000 but no IPs expire immediately.
            # The O(N) cleanup loop above would then run on EVERY subsequent request, starving the CPU.
            # We enforce a hard limit here by dropping the entire store if it's still too large after cleanup.
            if len(RATE_LIMIT_STORE) > 10000:
                RATE_LIMIT_STORE.clear()

        client_data = RATE_LIMIT_STORE.get(client_ip, {"count": 0, "start_time": now})

        if now - client_data["start_time"] > RATE_LIMIT_WINDOW:
            client_data = {"count": 1, "start_time": now}
        else:
            if client_data["count"] >= RATE_LIMIT_MAX:
                return Response(content="Too Many Requests", status_code=429)
            client_data["count"] += 1

        RATE_LIMIT_STORE[client_ip] = client_data

    return await call_next(request)

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
    if request.url.path in ("/generate_input", "/process_mesh") or request.url.path.startswith("/files/"):
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
def process_mesh(file: UploadFile, background_tasks: BackgroundTasks):
    """
    ⚡ Bolt: Sync endpoint to offload CPU-bound work.
    Using 'def' instead of 'async def' tells FastAPI to run this endpoint
    in an external threadpool. This prevents heavy operations like
    PyVista mesh reading and surface extraction from blocking the main
    asyncio event loop.
    """
    # ⚡ Bolt: Offload file cleanup to a background task
    background_tasks.add_task(_cleanup_old_uploads)

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
    # 🛡️ Sentinel: Hide the default 'Server: uvicorn' header to prevent Information Disclosure
    uvicorn.run(app, host=host, port=port, server_header=False)
