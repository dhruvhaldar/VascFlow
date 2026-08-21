## 2023-10-27 - [Security Enhancement: Remove hardcoded backend API URLs]
**Vulnerability:** The frontend application hardcoded the backend API URL as `http://localhost:8000` in multiple components (`MeshUpload.svelte`, `XMLPreview.svelte`, `Viewer.svelte`).
**Learning:** Hardcoding local API URLs can lead to Information Disclosure (exposing internal configuration structures) and breaks functionality when the frontend is deployed to production or testing environments where the API resides at a different domain.
**Prevention:** Use environment variables (like `import.meta.env.VITE_API_URL` in Vite projects) to dynamically inject backend routes depending on the environment context.

## 2023-10-27 - [Security Enhancement: Harden Content-Security-Policy (CSP)]
**Vulnerability:** The CSP in `index.html` included the `'unsafe-eval'` keyword in the `script-src` directive.
**Learning:** Using `'unsafe-eval'` weakens the CSP and increases the attack surface for Cross-Site Scripting (XSS) by allowing execution of malicious strings as code via functions like `eval()` and `new Function()`. It should be omitted unless strictly required by a specific development workflow or legacy dependency.
**Prevention:** Strictly maintain CSP directives without `'unsafe-eval'` and only add it if completely unavoidable and well-justified.
## 2023-10-27 - [Security Enhancement: Add Permissions-Policy security header]
**Vulnerability:** The application was missing the `Permissions-Policy` security header. While the CSP was strong, defense in depth involves restricting access to browser APIs entirely, minimizing the impact of potential vulnerabilities like XSS.
**Learning:** Security headers should not only protect against content injection (CSP) and MIME sniffing (X-Content-Type-Options) but also restrict access to device features that the app doesn't need.
**Prevention:** Add a `Permissions-Policy` header to all backend HTTP responses to explicitly disable sensitive browser APIs like `geolocation`, `microphone`, and `camera`.

## 2025-03-01 - Avoid Hardcoding Local API URLs in Frontend Code
**Vulnerability:** The application was hardcoding `http://localhost:8000` as the fallback `API_URL` and directly into the Content Security Policy `connect-src` header. This could inadvertently expose internal network routes to attackers or result in Cross-Site Scripting (XSS) risks due to permissive local origin exposure, and causes application malfunctions when deployed outside of local development.
**Learning:** Development environments often bake-in convenience URLs. However, relying on these in production codebases leads to insecure configuration deployments and brittle routing logic.
**Prevention:** Always rely on dynamically injected environment configurations (like `import.meta.env.VITE_API_URL` without insecure fallbacks) and configure build-time proxies (e.g., Vite proxy) to seamlessly handle local development API routing instead of polluting production source files.
## 2024-05-24 - Enhance Security Headers for API
**Vulnerability:** Weak security headers
**Learning:** For backend APIs that solely serve data (e.g., JSON/XML) and do not render HTML, enforcing a strict Content-Security-Policy such as `default-src 'none'; frame-ancestors 'none'; sandbox` entirely blocks resource loading and script execution if the endpoint is directly accessed in a browser.
**Prevention:** Bolster backend API defense-in-depth against cross-origin information leaks by consistently adding `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Resource-Policy: cross-origin` headers.

## 2025-03-01 - Add Audit Logging to Sensitive Endpoints
**Vulnerability:** Lack of audit logging on sensitive endpoints (file uploads, complex generations) prevents tracking API usage, investigating abuse, or tracing Denial of Service (DoS) attempts.
**Learning:** Adding structured logging (like `logging.info`) that logs request attributes such as `request.client.host`, file names, and payload sizes is critical for defense-in-depth against resource abuse. When injecting the `Request` object into existing FastAPI signatures, setting a default of `None` preserves testability so synchronous mock tests won't break.
**Prevention:** Consistently inject the `Request` object (defaulting to `None`) into performance- or resource-intensive endpoints and implement structured logging for critical request attributes.
## 2024-05-27 - [Security Enhancement: Avoid Hardcoded Local Domains in CSP]
**Vulnerability:** The Content Security Policy in `frontend/index.html` contained `ws://localhost:5173` hardcoded in its `connect-src` directive.
**Learning:** Hardcoding local development URLs into production CSP headers leaks internal development details and excessively opens up cross-origin permissions if attackers can control or spoof DNS requests related to localhost.
**Prevention:** Remove hardcoded development URLs from production CSP headers. Environment specific setup should be handled appropriately at the infrastructure layer or via runtime environment injection.
## 2025-03-01 - Sanitize Filenames in Audit Logs
**Vulnerability:** The application logged user-uploaded filenames (`file.filename`) directly to `logging.info` without any sanitization in the `process_mesh` endpoint. This allowed attackers to perform Log Injection (CWE-117) by inserting newline (`\n`) and carriage return (`\r`) characters into the filename to forge fake log entries or trigger log exhaustion DoS.
**Learning:** Any user-controlled input that gets printed into application logs, particularly those tracking audit trails or security events, must be rigorously sanitized.
**Prevention:** Always strip or replace newline characters and enforce a strict length limit (e.g., 255 characters) on user-provided inputs such as filenames before passing them to logging frameworks.

## 2025-03-01 - Add Rate Limit Headers
**Vulnerability:** The rate limiting middleware was successfully rejecting requests over the limit with a `429 Too Many Requests` status, but it failed to include standard `Retry-After` or `X-RateLimit-*` headers.
**Learning:** Returning a bare 429 without standard headers forces well-behaved clients (or proxies) to guess when to back off, which can lead to continued aggressive polling. Adding these headers improves API reliability and standardizes the DoS protection response.
**Prevention:** When implementing or enhancing custom rate limiting middleware (e.g., in FastAPI), always include standard HTTP headers like `Retry-After` for 429 responses, and `X-RateLimit-Limit`/`X-RateLimit-Remaining` for successful responses to guide client backoff behavior.

## 2025-03-01 - Add Rate Limit Headers
**Vulnerability:** The rate limiting middleware was successfully rejecting requests over the limit with a 429 Too Many Requests status, but it failed to include standard Retry-After or X-RateLimit-* headers in the response.
**Learning:** Returning a bare 429 without standard headers forces well-behaved clients (or proxies) to guess when to back off, which can lead to continued aggressive polling. Adding these headers improves API reliability and standardizes the DoS protection response.
**Prevention:** When implementing or enhancing custom rate limiting middleware (e.g., in FastAPI), always include standard HTTP headers like Retry-After for 429 responses, and X-RateLimit-Limit/X-RateLimit-Remaining for successful responses to guide client backoff behavior.

## 2025-03-01 - Add CSRF Origin Validation for Simple Requests
**Vulnerability:** The application relied solely on CORS middleware to restrict cross-origin requests. However, CORS does not trigger preflight OPTIONS requests for "simple" cross-origin POSTs (such as those using `multipart/form-data`, common in file uploads). This means the browser executes the POST request and sends the data (e.g. from a malicious form) before the server can reject the response via CORS headers, opening the door to CSRF-driven Denial of Service (DoS) attacks on state-changing endpoints.
**Learning:** Standard CORS middleware is insufficient to fully mitigate CSRF when dealing with simple requests. The request is still processed by the backend. Explicit validation of the `Origin` header is required to block these requests before they execute state-changing logic or consume server resources.
**Prevention:** Implement custom HTTP middleware to explicitly check the `Origin` header for state-changing requests (POST, PUT, DELETE, PATCH). If the origin is present and not explicitly whitelisted, reject the request with a 403 Forbidden status code.
## 2025-02-21 - Fix Log Injection in CSRF Middleware
**Vulnerability:** The CSRF middleware in `backend/main.py` logged the user-supplied `Origin` header directly without sanitization. Attackers could exploit this by sending a malformed `Origin` header containing carriage return (`\r`) or newline (`\n`) characters, injecting fake log entries or disrupting log analysis (CWE-117).
**Learning:** Even internal security mechanisms like CSRF blockades can become vulnerability vectors if they trust incoming data implicitly. When logging untrusted headers, sanitization is paramount.
**Prevention:** Always sanitize strings derived from user input before passing them to logging frameworks. Standardizing a `replace("\n", "_").replace("\r", "_")[:MAX_LEN]` pattern on logged headers and filenames mitigates injection risks.
## 2025-02-27 - Fix Log Injection via spoofed client IP
**Vulnerability:** The backend application logged the `client_ip` obtained from the ASGI scope directly to `logging.info` in `generate_input` and `process_mesh` endpoints without any sanitization. This allowed attackers to perform Log Injection (CWE-117) by injecting newline (`\n`) and carriage return (`\r`) characters through spoofed headers (e.g. `X-Forwarded-For`).
**Learning:** Even fields usually thought of as safe, like client IP, need sanitization before logging if they can be manipulated by malicious requests.
**Prevention:** Always sanitize user-supplied or network-derived data (like IPs, origins, or filenames) by replacing newline and carriage return characters before feeding them into logging statements.
## 2023-10-27 - Fix HTTP Header Smuggling / DoS Bypass
**Vulnerability:** The `limit_request_size` middleware checked for `chunked` encoding by iterating through the `request.scope.get("headers")`. When it encountered multiple `Transfer-Encoding` headers, it overwrote the previous value instead of concatenating them. An attacker could bypass the `chunked` check (which is meant to prevent unbounded memory/disk exhaustion DoS on most endpoints) by sending `Transfer-Encoding: chunked` followed by `Transfer-Encoding: identity`. The middleware would only see `identity` and allow the request, while the ASGI server (or upstream proxies) might still process it as `chunked`.
**Learning:** HTTP headers can appear multiple times in a request. When inspecting headers for security policies (like `Transfer-Encoding`, `Content-Length`, or `X-Forwarded-For`), you must either strictly reject duplicates or safely concatenate/aggregate them to prevent Request Smuggling and policy bypasses.
**Prevention:** When parsing headers from the raw ASGI scope byte tuples, concatenate duplicate header values (e.g., using a comma delimiter) rather than blindly overwriting the variable.
## 2025-03-10 - Fix Content-Length Header Smuggling / DoS Bypass
**Vulnerability:** The `limit_request_size` middleware checked for `Content-Length` by iterating through the `request.scope.get("headers")`. When it encountered multiple `Content-Length` headers, it overwrote the previous value instead of rejecting the request. An attacker could bypass the `Content-Length` limit (which is meant to prevent unbounded memory/disk exhaustion DoS on most endpoints) by sending a large payload with a fake, small `Content-Length` header appearing after the real one. The middleware would only see the small length and allow the request, while the ASGI server (or upstream proxies) might still spool the massive payload.
**Learning:** HTTP headers can appear multiple times in a request. When inspecting headers for security policies (like `Transfer-Encoding`, `Content-Length`, or `X-Forwarded-For`), you must either strictly reject duplicates or safely concatenate/aggregate them to prevent Request Smuggling and policy bypasses. According to RFC 7230, requests with multiple differing `Content-Length` headers must be rejected.
**Prevention:** When parsing headers from the raw ASGI scope byte tuples, reject requests that contain multiple `Content-Length` headers with a `400 Bad Request` status code.
## 2024-05-30 - Fix HTTP Request Smuggling via TE/CL combination
**Vulnerability:** The application was vulnerable to classic TE.CL and CL.TE HTTP Request Smuggling because the `limit_request_size` middleware didn't explicitly reject requests containing both a `Transfer-Encoding` header and a `Content-Length` header. An attacker could use this combination to desync the proxy and backend on the boundaries of a request.
**Learning:** According to RFC 7230, if a message is received with both a Transfer-Encoding and a Content-Length header field, the Transfer-Encoding overrides the Content-Length, but it opens up ambiguity for proxies that process differently. A secure default is to explicitly reject requests presenting both headers.
**Prevention:** Always include a check in HTTP request ingestion layers (or middlewares performing size/header validation) that rejects requests if both `Transfer-Encoding` and `Content-Length` are present, returning a 400 Bad Request status code.
## 2025-03-24 - [Security Enhancement: Remove unsafe-inline from CSP script-src]
**Vulnerability:** The Content Security Policy in `frontend/index.html` contained `'unsafe-inline'` in its `script-src` directive. This allows execution of inline scripts and opens the application to Cross-Site Scripting (XSS) attacks.
**Learning:** Hardcoding `'unsafe-inline'` inside production CSP headers significantly weakens the CSP protection by allowing any inline scripts injected by an attacker to execute. Modern frontend frameworks like Svelte rarely need `'unsafe-inline'` for `script-src` in production.
**Prevention:** Strictly maintain CSP directives and do not use `'unsafe-inline'` for `script-src` unless absolutely necessary and well-justified. Rely entirely on the external script sources that can be securely handled.
## 2025-03-24 - [Security Enhancement: Explicitly disable legacy XSS Auditor]
**Vulnerability:** The application did not explicitly set `X-XSS-Protection: 0`. While the CSP was strong, older browsers that still implemented the deprecated XSS Auditor could be manipulated by attackers to selectively block valid scripts on the page, introducing new vulnerabilities or bypassing existing security controls.
**Learning:** The `X-XSS-Protection: 1; mode=block` header is deprecated in modern browsers. Security experts and modern standards recommend disabling it entirely (`0`) and relying instead on a robust Content-Security-Policy (CSP) to defend against Cross-Site Scripting (XSS).
**Prevention:** Always include `X-XSS-Protection: 0` alongside your CSP headers to ensure consistent security behavior across browsers and to prevent XSS Auditor-based manipulation attacks.
