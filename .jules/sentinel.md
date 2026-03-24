## 2024-05-28 - [Fix Path Traversal in File Uploads]
**Vulnerability:** Path traversal risk found in `save_upload_file` and `get_mesh_file_path` endpoints in `backend/mesh_service.py` where uploaded files could be written outside the target directory if the filename contains `../` or similar sequences.
**Learning:** FastAPI's `UploadFile.filename` is provided by the client and is untrusted input. It needs to be explicitly sanitized.
**Prevention:** Use `os.path.basename` to extract just the filename from the path provided by the client, and explicitly replace backslashes (`\\`) with forward slashes (`/`) before doing so, as `os.path.basename` might not catch backslashes on POSIX systems while Windows clients might send them.
