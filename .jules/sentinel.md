## 2024-04-05 - Enforce File Size Limit
**Vulnerability:** Unrestricted File Upload Size
**Learning:** FastAPI's `UploadFile` does not automatically restrict file size, which can lead to memory exhaustion and DoS attacks if users upload very large files.
**Prevention:** Implement file size checking in the API endpoint by explicitly checking `file.size` and returning HTTP 413 (Payload Too Large) if the size exceeds a safe limit.

## 2024-04-08 - Enforce String Length Limits on Pydantic Models
**Vulnerability:** Memory Exhaustion / Denial of Service (DoS)
**Learning:** FastAPI's Pydantic models will eagerly consume unbounded string fields if limits are not explicitly set. This can allow attackers to crash the server or exhaust memory by passing massive strings in JSON requests.
**Prevention:** Always enforce strict `max_length` constraints on all string fields within Pydantic models using `Field(..., max_length=N)` to limit input sizes at the application layer.

## 2024-05-24 - Enforce Array Length Limits on Pydantic Models
**Vulnerability:** Memory Exhaustion / Denial of Service (DoS)
**Learning:** Just like strings, unbounded array fields (`List[...]`) in FastAPI Pydantic models can lead to memory exhaustion and server crashes if an attacker submits an excessive number of elements.
**Prevention:** Always enforce strict `max_length` constraints on all list/array fields within Pydantic models using `Field(max_length=N)` to limit the maximum number of items the application processes.

## 2024-06-15 - Enforce File Size Limit During Stream Read
**Vulnerability:** Disk Exhaustion / Denial of Service (DoS) via Chunked Uploads
**Learning:** Checking `upload_file.size` in FastAPI is insufficient for enforcing file size limits because it relies on the client-provided `Content-Length` header. If a client omits the header or uses streaming chunked uploads, `upload_file.size` evaluates to `None`. Relying solely on this allows attackers to bypass size limits and exhaust disk space by streaming unlimited data directly to disk.
**Prevention:** Do not rely exclusively on the `Content-Length` header (`upload_file.size`). Read the uploaded file stream in chunks, keeping an accumulated count of total bytes written. If the total exceeds the allowed limit during the transfer, immediately raise an error (HTTP 413) and delete the partially written file to ensure limits are strictly enforced on disk.
## 2024-10-25 - Enforce Numerical Input Limits (Bounds)
**Vulnerability:** Integer Overflow / Resource Exhaustion (DoS)
**Learning:** While string and array length limits are enforced, numerical fields (int, float) in Pydantic models lack bounds by default. Massive inputs can cause integer overflows or exhaust memory when passed to downstream C++ physics solvers.
**Prevention:** Always apply strict numerical bounds (`ge`, `le`, `gt`, `lt`) to integer and float fields in Pydantic models using `Field(..., ge=1, le=10000000)` to fail securely at the API layer.
## 2024-04-13 - Enforce Numerical Input Limits (Bounds)
**Vulnerability:** Integer Overflow / Resource Exhaustion (DoS)
**Learning:** While string and array length limits are enforced, numerical fields (int, float) in Pydantic models lack bounds by default. Massive inputs can cause integer overflows or exhaust memory when passed to downstream C++ physics solvers.
**Prevention:** Always apply strict numerical bounds (`ge`, `le`, `gt`, `lt`) to integer and float fields in Pydantic models using `Field(..., ge=1, le=10000000)` to fail securely at the API layer.

## 2025-02-28 - [500 Error via Unhandled Null Filename in FastAPI]
**Vulnerability:** FastAPIs `UploadFile.filename` can be `None` or an empty string, leading to unhandled `AttributeError` exceptions (causing 500 errors) when string manipulation functions like `.replace()` or `os.path.basename()` are called on it.
**Learning:** This specific unhandled exception can easily lead to a Denial of Service or information exposure if not caught, and often happens natively when files are uploaded without standard browser-supplied filenames (e.g. from a script).
**Prevention:** Always validate that `upload_file.filename` exists before calling string methods or path operations on it to ensure graceful handling (returning a 400 Bad Request instead of 500 Internal Server Error).

## 2024-04-16 - Prevent Hardcoded Bind All Interfaces (B104)
**Vulnerability:** Hardcoded Bind All Interfaces (`0.0.0.0`)
**Learning:** Hardcoding `host="0.0.0.0"` in `uvicorn.run()` unconditionally binds the server to all available network interfaces. In local development or misconfigured environments, this can unintentionally expose the application to the local network or the public internet, violating the principle of least privilege.
**Prevention:** Default to local loopback (`127.0.0.1`) and use environment variables (e.g., `os.environ.get("HOST", "127.0.0.1")`) to explicitly control the bind address. This allows secure local development while still enabling `0.0.0.0` bindings when explicitly required (e.g., inside Docker containers).

## 2025-02-28 - [Disk Exhaustion / DoS via Uncleaned Invalid Files]
**Vulnerability:** Disk Exhaustion / Denial of Service (DoS)
**Learning:** Returning an HTTP error inside an exception handler (e.g. `except ValueError: raise HTTPException(...)`) does not automatically clean up physical resources like temporary files that were already saved to disk. When uploading mesh files, if PyVista parsing failed, the endpoint threw a 400 Bad Request error but left the 50MB uploaded mesh file orphaned in the `uploads/` directory indefinitely.
**Prevention:** Always ensure that temporary files generated during an API request are explicitly cleaned up (e.g. `os.remove(file_path)`) within exception handlers (or a `finally` block) if the subsequent validation or processing fails.

## 2025-02-28 - [Disk Exhaustion / DoS via Uncleaned Derived Visualization Files]
**Vulnerability:** Disk Exhaustion / Denial of Service (DoS)
**Learning:** During mesh processing, generating derived visualization files (like `_surface.vtp` from `.vtu` files) creates secondary artifacts on disk. If subsequent validation fails or an unhandled exception occurs after the visualization file is generated, merely cleaning up the original uploaded file leaves the derived visualization file orphaned indefinitely, leading to Disk Exhaustion DoS over time.
**Prevention:** Implement a unified cleanup function (e.g., `cleanup_mesh_files`) that tracks and securely deletes *both* the original uploaded file and any expected derived visualization files when an exception is thrown in the endpoint.

## 2025-02-28 - Restrict CORS Methods and Headers
**Vulnerability:** Overly Permissive CORS Configuration
**Learning:** Using wildcards (`allow_methods=["*"]`, `allow_headers=["*"]`) in FastAPI's `CORSMiddleware` violates the principle of least privilege. This can potentially allow attackers to execute unexpected HTTP methods or send malicious headers from unauthorized origins, increasing the attack surface for Cross-Site Scripting (XSS) or Cross-Site Request Forgery (CSRF).
**Prevention:** Always explicitly define the required HTTP methods (e.g., `["GET", "POST", "OPTIONS"]`) and headers (e.g., `["Content-Type", "Accept", "Origin", "X-Requested-With"]`) based on the application's actual needs to enforce strict access control boundaries.
