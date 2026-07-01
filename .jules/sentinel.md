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
