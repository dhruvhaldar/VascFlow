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

## 2024-05-24 - Restrict Referrer Policy in Security Headers
**Vulnerability:** Information Leakage via Referer Header
**Learning:** By default, browsers may send the full URL of the referring page in the `Referer` header when navigating away or making cross-origin requests. This can inadvertently leak sensitive path parameters, tokens, or query strings to third-party domains.
**Prevention:** Always include `Referrer-Policy: strict-origin-when-cross-origin` (or similar restrictive policies) in backend HTTP security headers. This ensures that only the origin is sent for cross-origin requests, protecting sensitive URL paths from being leaked to external systems.

## 2024-04-26 - Prevent Application-Level DoS from ElementTree Serialization
**Vulnerability:** Application-Layer DoS via `TypeError` on `xml.etree.ElementTree` serialization.
**Learning:** In Python's `xml.etree.ElementTree`, passing a `None` value to an attribute (e.g., `ET.SubElement(parent, "tag", attr=None)`) is syntactically valid but throws a `TypeError: cannot serialize None` during `ET.tostring()` execution. Since Pydantic allows `Optional` fields to be `None`, directly mapping Pydantic fields to XML attributes as keyword arguments creates a crash vector.
**Prevention:** Always use dictionary unpacking for XML attributes (`**attribs`) and conditionally add keys only if their value is not `None` before passing to `ET.SubElement()`.

## 2025-02-28 - Prevent Caching of Sensitive API Responses
**Vulnerability:** Information Leakage via Browser/Proxy Caching
**Learning:** If an API endpoint returns sensitive information (like simulation configurations, mesh processing results, or XML data), intermediate proxies or user browsers might cache the response. If caching is not strictly disabled, attackers might retrieve sensitive data from a shared computer or a misconfigured proxy cache.
**Prevention:** Always add explicit `Cache-Control` headers (e.g. `Cache-Control: no-store, no-cache, must-revalidate, max-age=0` and `Pragma: no-cache`) to API endpoints that handle sensitive or user-specific data to prevent unintended caching.

## 2024-05-04 - Secure IP Resolution for Rate Limiting Behind Proxies
**Vulnerability:** IP Spoofing / Rate Limit Bypass
**Learning:** When implementing rate limiting middleware, manually parsing `X-Forwarded-For` or `X-Real-IP` headers allows attackers to easily spoof their IP address. This enables them to bypass rate limits or intentionally block legitimate users (targeted DoS) by sending fake IPs.
**Prevention:** Rely on `request.client.host` and configure the underlying ASGI server (e.g., Uvicorn with `--proxy-headers` or `ProxyHeadersMiddleware`) to securely resolve the real client IP based on trusted proxy configurations, rather than writing custom header-parsing logic.

## 2026-05-05 - Fix CPU Exhaustion DoS in Custom Rate Limiter
**Vulnerability:** CPU Exhaustion / Denial of Service (DoS)
**Learning:** In-memory dictionary cleanup loops that run conditionally on the store size (e.g. `if len(store) > 10000: cleanup()`) can create an O(N) CPU vulnerability. If an attacker floods unique items so that none expire before the size limit is reached, the condition remains true, and the O(N) loop executes on *every single subsequent request*. This quickly starves the CPU.
**Prevention:** When performing periodic O(N) cleanup on data structures, always implement a failsafe hard limit (e.g. `store.clear()`) if the threshold is still exceeded after cleanup, or throttle the cleanup execution using timestamps instead of size thresholds.

## 2025-02-28 - [Disk Exhaustion / DoS via Unbounded File Accumulation]
**Vulnerability:** Disk Exhaustion / Denial of Service (DoS)
**Learning:** Even if individual file sizes are restricted, allowing uploaded or generated files to accumulate indefinitely in a static directory (like `uploads/`) creates a vector for Disk Exhaustion attacks over time.
**Prevention:** Implement a mechanism to periodically prune old files from upload directories (e.g., deleting files older than 1 hour) to enforce bounded disk usage and mitigate this form of DoS.

## 2024-10-26 - [Disk Exhaustion / DoS via `shutil.copyfileobj` Bypass]
**Vulnerability:** Disk Exhaustion / Denial of Service (DoS)
**Learning:** Using `upload_file.size` to conditionally bypass chunked reading and use `shutil.copyfileobj(upload_file.file, buffer)` is dangerous. An attacker can spoof the `Content-Length` header to a small value (e.g., 100 bytes) but upload a massive payload (e.g., 50GB). `shutil.copyfileobj` will blindly copy the entire stream, bypassing application-layer size limits and exhausting the server's disk space.
**Prevention:** Never use `shutil.copyfileobj` or rely on `upload_file.size` to enforce file limits securely. Always read the file stream in chunks (e.g., `chunk = upload_file.file.read(chunk_size)`) and accumulate the bytes actually written. If the accumulated total exceeds the maximum allowed size, immediately raise an error (HTTP 413) and delete the partial file.

## 2024-05-28 - [Information Disclosure Prevention via Server Header]
**Vulnerability:** Information Disclosure (Server Implementation Leaks). FastAPI applications running on Uvicorn by default expose the server implementation and version via the `Server: uvicorn` HTTP response header.
**Learning:** This information can aid an attacker in targeting known vulnerabilities specifically related to the server implementation. Standard FastAPI middleware executes before Uvicorn sends the response, meaning middleware cannot easily remove this header as it's appended later at the protocol level.
**Prevention:** Always hide or disable this default header to enforce information hiding. When starting the application using `uvicorn.run()`, pass the argument `server_header=False` (e.g., `uvicorn.run(app, host=host, port=port, server_header=False)`) to prevent Uvicorn from appending it.
