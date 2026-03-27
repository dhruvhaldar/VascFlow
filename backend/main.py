from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import shutil
import os
import logging
from models import SimulationConfig
from xml_generator import generate_svfsi_xml
from mesh_service import save_upload_file, get_mesh_metadata

logger = logging.getLogger(__name__)

app = FastAPI()

# 🛡️ Sentinel: Restrict CORS origins to prevent unauthorized cross-origin requests
# Origins can be configured via VITE_ALLOWED_ORIGINS environment variable
allowed_origins_env = os.environ.get("VITE_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "svFSI Backend is running"}

@app.post("/generate_input")
def generate_input(config: SimulationConfig):
    try:
        xml_content = generate_svfsi_xml(config)
        return {"xml": xml_content}
    except Exception as e:
        # 🛡️ Sentinel: Log internal error and return generic message to prevent info leakage
        logger.error(f"Error generating XML: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the input file.")

@app.post("/process_mesh")
def process_mesh(file: UploadFile):
    """
    ⚡ Bolt: Sync endpoint to offload CPU-bound work.
    Using 'def' instead of 'async def' tells FastAPI to run this endpoint
    in an external threadpool. This prevents heavy operations like
    PyVista mesh reading and surface extraction from blocking the main
    asyncio event loop.
    """
    try:
        file_path = save_upload_file(file)
        metadata = get_mesh_metadata(file_path)
        return metadata
    except ValueError as e:
        # 🛡️ Sentinel: Return 400 for bad input (like invalid file extension)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 🛡️ Sentinel: Log internal error and return generic message to prevent info leakage
        logger.error(f"Error processing mesh: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the mesh.")

# Serve static files for mesh visualization
from fastapi.staticfiles import StaticFiles
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
