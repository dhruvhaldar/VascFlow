import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_audit_generate_input():
    payload = {
        "general": {
            "num_time_steps": 20,
            "time_step_size": 0.005,
            "save_results_frequency": 5,
            "start_time_step": 0,
        },
        "mesh": {"mesh_path": "mesh.vtu", "domain_type": "Fluid"},
        "physics": {
            "physics_type": "Fluid",
            "density": 1.06,
            "viscosity": 0.04,
            "material_model": "Newtonian",
            "properties": [],
        },
        "boundary_conditions": [
            {
                "face_name": "inlet",
                "bc_type": "Dirichlet",
                "variable": "Velocity",
                "value": 11.0,
                "profile": "Parabolic",
                "face_id": 1,
            }
        ],
    }
    response = client.post("/generate_input", json=payload)
    assert response.status_code == 200

def test_audit_process_mesh(monkeypatch):
    import main
    def fake_save_upload_file(upload_file):
        return "uploads/sample.vtu"

    def fake_get_mesh_metadata(path):
        return {
            "n_points": 42,
            "n_cells": 24,
            "bounds": [0, 1, 0, 1, 0, 1],
            "faces": [{"id": 1, "name": "inlet", "count": 6}],
            "viz_file": "sample_surface.vtp",
        }

    monkeypatch.setattr(main, "save_upload_file", fake_save_upload_file)
    monkeypatch.setattr(main, "get_mesh_metadata", fake_get_mesh_metadata)

    response = client.post(
        "/process_mesh",
        files={"file": ("sample.vtu", b"mesh-bytes", "application/octet-stream")},
    )
    assert response.status_code == 200
