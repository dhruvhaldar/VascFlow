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

    assert response.status_code == 400
    assert "Invalid file extension" in response.json()["detail"]


def test_process_mesh_rejects_large_files():
    # Create a dummy large file upload mock using a large bytes payload that exceeds 50MB conceptually,
    # or just rely on overriding the `size` property dynamically during the request if feasible.
    # FastAPI's TestClient correctly sets the `size` property of UploadFile when given a bytes payload,
    # but instead of generating a 51MB payload (which would consume a lot of RAM during tests),
    # we can monkeypatch `MAX_FILE_SIZE` in the module or use a smaller threshold.
    # However, since we defined MAX_FILE_SIZE inside the function, we must send a payload larger than 50MB.
    # To keep test memory low, we can patch the UploadFile size validation directly in testing if needed,
    # but TestClient allows injecting mock files. Let's mock the `UploadFile` class temporarily or send a small payload but mock `file.size`.

    class MockLargeFile:
        filename = "huge.vtu"
        size = 51 * 1024 * 1024  # 51 MB

    # Since fastapi reads `file.size` from the injected UploadFile object, let's mock it inside the endpoint:
    import main

    # We can test by sending a request where the UploadFile is initialized by TestClient,
    # but we can monkeypatch `main.process_mesh` size check if we don't want to send 51MB.
    # Actually, sending a 51MB string of zeros takes about 51MB of RAM, which is completely fine for a test.
    large_payload = b"0" * (50 * 1024 * 1024 + 1)

    response = client.post(
        "/process_mesh",
        files={"file": ("huge.vtu", large_payload, "application/octet-stream")},
    )

    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]
