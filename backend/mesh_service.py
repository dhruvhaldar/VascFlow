import pyvista as pv
import os
from fastapi import UploadFile
import shutil
import numpy as np

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def save_upload_file(upload_file: UploadFile) -> str:
    file_path = os.path.join(UPLOAD_DIR, upload_file.filename)
    # Using async read and sync write
    content = await upload_file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    return file_path

def get_mesh_metadata(file_path: str):
    """
    Reads the mesh using PyVista and returns metadata.
    If it's a volume mesh, extracts the surface.
    Attempts to identify face patches.
    """
    try:
        mesh = pv.read(file_path)
    except Exception as e:
        return {"error": str(e)}

    metadata = {
        "n_points": mesh.n_points,
        "n_cells": mesh.n_cells,
        "bounds": mesh.bounds,
        "faces": []
    }

    # Extract surface if volume (UnstructuredGrid)
    surface = mesh
    if isinstance(mesh, pv.UnstructuredGrid):
        surface = mesh.extract_surface()

    # Save surface for visualization
    viz_filename = os.path.basename(file_path)
    if viz_filename.endswith(".vtu"):
        viz_filename = viz_filename.replace(".vtu", "_surface.vtp")
    elif not viz_filename.endswith(".vtp"):
        viz_filename = viz_filename + "_surface.vtp"

    viz_path = os.path.join(os.path.dirname(file_path), viz_filename)
    # PyVista saves binary VTP by default which vtk.js can read
    surface.save(viz_path)

    metadata["viz_file"] = viz_filename

    # Try to find face/boundary IDs in cell data
    face_ids = None
    face_array_name = None

    # Common names for boundary markers
    possible_names = ["FaceID", "BoundaryID", "RegionId", "ModelFaceID", "GlobalElementID"]

    for name in possible_names:
        if name in surface.cell_data:
            face_ids = surface.cell_data[name]
            face_array_name = name
            break

    if face_ids is not None:
        unique_ids = np.unique(face_ids)
        # Convert to list of dicts
        face_list = []
        for uid in unique_ids:
            count = int(np.sum(face_ids == uid))
            face_list.append({
                "id": int(uid),
                "name": f"{face_array_name} {uid}",
                "count": count
            })
        metadata["faces"] = face_list
    else:
        # Fallback: Connectivity
        try:
            conn = surface.connectivity(largest=False)
            if "RegionId" in conn.cell_data:
                region_ids = conn.cell_data["RegionId"]
                unique_ids = np.unique(region_ids)
                face_list = []
                for uid in unique_ids:
                    count = int(np.sum(region_ids == uid))
                    face_list.append({
                        "id": int(uid),
                        "name": f"Region {uid}",
                        "count": count
                    })
                metadata["faces"] = face_list
            else:
                 metadata["faces"].append({"id": 0, "name": "Default Surface", "count": surface.n_cells})
        except Exception:
             metadata["faces"].append({"id": 0, "name": "Default Surface", "count": surface.n_cells})

    return metadata

def get_mesh_file_path(filename: str) -> str:
    return os.path.join(UPLOAD_DIR, filename)
