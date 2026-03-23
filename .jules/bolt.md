## 2026-03-23 - FastAPI Asyncio Event Loop Blocking Anti-pattern
**Learning:** In FastAPI, CPU-bound operations like PyVista `pv.read()` inside an `async def` endpoint block the main asyncio event loop, causing severe concurrency bottlenecks. This is easily solved by using a standard `def` endpoint which FastAPI automatically offloads to a threadpool.
**Action:** Use `def` instead of `async def` for endpoints containing heavy CPU-bound tasks or synchronous blocking IO unless using specific async-aware libraries.
