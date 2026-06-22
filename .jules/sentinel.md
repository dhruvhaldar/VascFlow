## 2025-02-14 - Add Client-Side Timeouts to Prevent Resource Starvation

**Vulnerability:** External API calls (`fetch()`) in the Svelte frontend lacked explicit timeouts. By default, `fetch()` operations do not timeout. If the backend FastAPI server hung or if network connectivity dropped, the UI would remain indefinitely stuck in a "Processing..." or "Generating..." state, leading to client-side resource exhaustion and poor resilience against DoS conditions.
**Learning:** Modern `fetch()` calls require manual timeout implementation to ensure application resilience. Relying solely on server-side timeouts (or expecting immediate TCP resets) leaves the client vulnerable to infinite hanging states.
**Prevention:** Always implement explicit timeouts on frontend `fetch()` requests using the modern `AbortSignal.timeout(ms)` API, and explicitly catch and handle `TimeoutError` to fail securely and provide actionable feedback to the user.

## 2025-02-14 - Enforce HTTP-Layer File Size Limits for FastAPI UploadFile

**Vulnerability:** A Denial of Service (DoS) vulnerability via Disk Exhaustion was found in the FastAPI backend. The `/process_mesh` endpoint enforced a 50MB file size limit internally. However, because it accepts `UploadFile`, FastAPI's underlying parsing mechanism spools the entire incoming multipart payload to disk *before* the endpoint code is even executed. By bypassing the HTTP middleware limits (which explicitly excluded `/process_mesh`), an attacker could upload massive files that would exhaust the server's disk space before the endpoint's internal limit could reject them.
**Learning:** Pydantic and `UploadFile` eagerly consume or spool massive request bodies before executing endpoint logic. Relying on application-layer logic inside an endpoint to limit file sizes is insufficient against DoS attacks.
**Prevention:** Always cap file sizes at the HTTP middleware layer, before the request reaches the routing or parsing layers. Prevent bypasses by also denying `Transfer-Encoding: chunked` requests where `Content-Length` isn't provided.

## 2026-06-22 - Rate Limit Static File Endpoints

**Vulnerability:** The `StaticFiles` endpoint (`/files`) was excluded from the global application rate limiter. While serving static files is generally fast, unprotected endpoints can still be abused to cause Denial of Service (DoS) or exhaust server bandwidth via repeated bulk requests for large files (like 3D meshes).
**Learning:** Rate limiters should apply not just to dynamic API routes but also to routes serving potentially large static assets to prevent bandwidth exhaustion or basic DoS attempts.
**Prevention:** Ensure static asset mounts (like `/files/`) are explicitly included in the paths covered by global rate-limiting middleware.
