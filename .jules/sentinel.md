## 2024-04-05 - Enforce File Size Limit
**Vulnerability:** Unrestricted File Upload Size
**Learning:** FastAPI's `UploadFile` does not automatically restrict file size, which can lead to memory exhaustion and DoS attacks if users upload very large files.
**Prevention:** Implement file size checking in the API endpoint by explicitly checking `file.size` and returning HTTP 413 (Payload Too Large) if the size exceeds a safe limit.
## 2024-05-15 - Enforce Input Length Limits
**Vulnerability:** Denial of Service (DoS) risk via unconstrained string lengths.
**Learning:** Pydantic models mapping directly to client requests must strictly constrain string field lengths (e.g. `Field(..., max_length=...)`) to prevent excessive memory allocation or computational delays during payload processing (such as XML generation).
**Prevention:** Always define `max_length` constraints for arbitrary string inputs in the FastAPI `models.py` schema.
