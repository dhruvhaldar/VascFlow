from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "svFSI Backend is running"}


def test_generate_input_endpoint_returns_xml():
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
    data = response.json()
    assert "<svFSIFile" in data["xml"]
    assert "<MeshFilePath>mesh.vtu</MeshFilePath>" in data["xml"]


def test_process_mesh_endpoint_returns_mocked_metadata(monkeypatch):
    def fake_save_upload_file(upload_file):
        assert upload_file.filename == "sample.vtu"
        return "uploads/sample.vtu"

    def fake_get_mesh_metadata(path):
        assert path == "uploads/sample.vtu"
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
    assert response.json()["viz_file"] == "sample_surface.vtp"
    assert response.json()["faces"][0]["name"] == "inlet"


def test_process_mesh_rejects_unsupported_extension():
    response = client.post(
        "/process_mesh",
        files={"file": ("bad.txt", b"plain-text", "text/plain")},
    )

    assert response.status_code == 500
    assert "Invalid file extension" in response.json()["detail"]
