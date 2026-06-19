## 2025-02-14 - Add Client-Side Timeouts to Prevent Resource Starvation

**Vulnerability:** External API calls (`fetch()`) in the Svelte frontend lacked explicit timeouts. By default, `fetch()` operations do not timeout. If the backend FastAPI server hung or if network connectivity dropped, the UI would remain indefinitely stuck in a "Processing..." or "Generating..." state, leading to client-side resource exhaustion and poor resilience against DoS conditions.
**Learning:** Modern `fetch()` calls require manual timeout implementation to ensure application resilience. Relying solely on server-side timeouts (or expecting immediate TCP resets) leaves the client vulnerable to infinite hanging states.
**Prevention:** Always implement explicit timeouts on frontend `fetch()` requests using the modern `AbortSignal.timeout(ms)` API, and explicitly catch and handle `TimeoutError` to fail securely and provide actionable feedback to the user.
