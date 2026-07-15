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
