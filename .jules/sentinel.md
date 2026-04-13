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
