## 2024-04-05 - Enforce File Size Limit
**Vulnerability:** Unrestricted File Upload Size
**Learning:** FastAPI's `UploadFile` does not automatically restrict file size, which can lead to memory exhaustion and DoS attacks if users upload very large files.
**Prevention:** Implement file size checking in the API endpoint by explicitly checking `file.size` and returning HTTP 413 (Payload Too Large) if the size exceeds a safe limit.

## 2024-04-08 - Enforce String Length Limits on Pydantic Models
**Vulnerability:** Memory Exhaustion / Denial of Service (DoS)
**Learning:** FastAPI's Pydantic models will eagerly consume unbounded string fields if limits are not explicitly set. This can allow attackers to crash the server or exhaust memory by passing massive strings in JSON requests.
**Prevention:** Always enforce strict `max_length` constraints on all string fields within Pydantic models using `Field(..., max_length=N)` to limit input sizes at the application layer.
