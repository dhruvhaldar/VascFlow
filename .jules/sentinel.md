## 2024-05-28 - [Fix Path Traversal in File Uploads]
**Vulnerability:** Path traversal risk found in `save_upload_file` and `get_mesh_file_path` endpoints in `backend/mesh_service.py` where uploaded files could be written outside the target directory if the filename contains `../` or similar sequences.
**Learning:** FastAPI's `UploadFile.filename` is provided by the client and is untrusted input. It needs to be explicitly sanitized.
**Prevention:** Use `os.path.basename` to extract just the filename from the path provided by the client, and explicitly replace backslashes (`\\`) with forward slashes (`/`) before doing so, as `os.path.basename` might not catch backslashes on POSIX systems while Windows clients might send them.

## 2026-03-25 - [Fix Unrestricted File Upload]
**Vulnerability:** Unrestricted file upload risk found in `save_upload_file` in `backend/mesh_service.py` where any file type could be uploaded.
**Learning:** Validating file extensions for untrusted uploads is critical to prevent attackers from uploading potentially harmful files (e.g. executable scripts) which might compromise the backend.
**Prevention:** Validate file extensions against an allowlist of expected types (e.g. `.vtu`, `.vtp`, `.vtk`) before processing or saving the file.

## 2026-03-29 - [Fix Information Leakage in Error Responses]
**Vulnerability:** Information exposure risk found in `backend/main.py` and `backend/mesh_service.py` where raw exception strings (`str(e)`) were being returned directly to the client in HTTP 500 responses.
**Learning:** Returning raw exception details in API responses can leak sensitive system internals, stack traces, or file paths to attackers, which could aid in further exploitation.
**Prevention:** Catch expected validation errors (like `ValueError` for invalid extensions) separately and return safe 400 Bad Request responses. For all other unexpected `Exception`s, log the detailed error internally using Python's `logging` module and return a generic, non-descriptive HTTP 500 error message to the client.
