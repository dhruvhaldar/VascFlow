import pyvista as pv
import os
import logging
from fastapi import UploadFile
import shutil
import numpy as np
import uuid

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_upload_file(upload_file: UploadFile) -> str:
    """
    ⚡ Bolt: Synchronous file save.
    Using sync operations here allows FastAPI to run this in a threadpool
    when called from a sync endpoint, preventing event loop blocking during
    large file IO and CPU-heavy PyVista operations.
    """
    # Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(upload_file.filename.replace('\\', '/'))

    # Validate file extension to prevent unrestricted file upload
    ALLOWED_EXTENSIONS = {'.vtu', '.vtp', '.vtk'}
    _, ext = os.path.splitext(safe_filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file extension. Allowed extensions are: {', '.join(ALLOWED_EXTENSIONS)}")

    # 🛡️ Sentinel: Use UUIDs for uploaded files instead of original filenames to prevent
    # file overwriting by concurrent uploads and Insecure Direct Object Reference (IDOR).
    unique_filename = f"{uuid.uuid4()}{ext.lower()}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
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
        logging.error("Failed to read mesh file using PyVista: %s", str(e))
        return {"error": "Failed to read mesh file."}

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
    # ⚡ Bolt: Only save the surface if it's a new file.
    # If the user uploaded a .vtp file, viz_path == file_path, and calling
    # surface.save(viz_path) would unnecessarily rewrite the entire file to disk.
    # Avoiding this redundant write saves significant I/O time on large meshes.
    if viz_path != file_path:
        # ⚡ Bolt: Optimize PyVista surface copy for visualization.
        # Instead of deep copying the entire surface (which duplicates all heavy
        # simulation arrays like Pressure/Velocity) and then deleting them one by one,
        # we copy only the structural geometry/topology, then selectively carry over
        # the minimal rendering arrays. This drastically reduces CPU and Memory overhead.
        viz_surface = pv.PolyData()
        viz_surface.copy_structure(surface)

        for name in ['Normals', 'TCoords']:
            if name in surface.point_data:
                viz_surface.point_data[name] = surface.point_data[name]
            if name in surface.cell_data:
                viz_surface.cell_data[name] = surface.cell_data[name]

        # PyVista saves binary VTP by default which vtk.js can read
        viz_surface.save(viz_path)

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
        # ⚡ Bolt: Use return_counts=True to compute all counts in a single O(N log N) pass
        # instead of O(N*K) where we sum the boolean array for each unique ID.
        unique_ids, counts = np.unique(face_ids, return_counts=True)
        # Convert to list of dicts
        face_list = []
        for uid, count in zip(unique_ids, counts):
            face_list.append({
                "id": int(uid),
                "name": f"{face_array_name} {uid}",
                "count": int(count)
            })
        metadata["faces"] = face_list
    else:
        # Fallback: Connectivity
        try:
            conn = surface.connectivity(largest=False)
            if "RegionId" in conn.cell_data:
                region_ids = conn.cell_data["RegionId"]
                # ⚡ Bolt: Use return_counts=True for performance.
                unique_ids, counts = np.unique(region_ids, return_counts=True)
                face_list = []
                for uid, count in zip(unique_ids, counts):
                    face_list.append({
                        "id": int(uid),
                        "name": f"Region {uid}",
                        "count": int(count)
                    })
                metadata["faces"] = face_list
            else:
                 metadata["faces"].append({"id": 0, "name": "Default Surface", "count": surface.n_cells})
        except Exception:
             metadata["faces"].append({"id": 0, "name": "Default Surface", "count": surface.n_cells})

    return metadata

def get_mesh_file_path(filename: str) -> str:
    # Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(filename.replace('\\', '/'))
    return os.path.join(UPLOAD_DIR, safe_filename)
