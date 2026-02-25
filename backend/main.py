from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import shutil
import os
from models import SimulationConfig
from xml_generator import generate_svfsi_xml
from mesh_service import save_upload_file, get_mesh_metadata

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_mesh")
async def process_mesh(file: UploadFile):
    try:
        file_path = await save_upload_file(file)
        metadata = get_mesh_metadata(file_path)
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files for mesh visualization
from fastapi.staticfiles import StaticFiles
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
