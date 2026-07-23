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
