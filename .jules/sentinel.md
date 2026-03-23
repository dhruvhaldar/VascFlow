## 2024-05-18 - [Path Traversal in File Uploads]
**Vulnerability:** Found a Path Traversal (Directory Traversal) vulnerability in `backend/mesh_service.py` within `save_upload_file` and `get_mesh_file_path`. The `upload_file.filename` and `filename` from the API input were concatenated directly to the `UPLOAD_DIR`, allowing attackers to pass paths like `../../../etc/passwd`.
**Learning:** Never trust raw user input for filenames or paths. Direct concatenation of user-provided paths with the base directory creates a path traversal vulnerability.
**Prevention:** Always sanitize the filename before using it in a path using functions like `os.path.basename` (or `werkzeug.utils.secure_filename` for web applications when available).
