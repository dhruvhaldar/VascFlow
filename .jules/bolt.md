
## 2025-04-26 - [Optimize PyVista Surface Extraction Algorithm]
**Learning:** By default, PyVista's `extract_surface()` on an `UnstructuredGrid` uses the `vtkDataSetSurfaceFilter` (algorithm `'dataset_surface'`). While passing `pass_pointid=False, pass_cellid=False` avoids computing original ID maps, switching the algorithm explicitly to `None` (`vtkGeometryFilter`) provides an additional ~10x to 30x performance speedup (e.g. from 0.9s to 0.02s on a 1M cell mesh) without losing necessary cell data mapping like `FaceID` arrays.
**Action:** When extracting outer surfaces from volumetric meshes using PyVista where maintaining volume cell and point ID mapping is unnecessary, explicitly set `algorithm=None` along with `pass_pointid=False, pass_cellid=False` for maximum performance.

## 2024-04-28 - [Optimize FastAPI GZipMiddleware compression level]
**Learning:** By default, FastAPI/Starlette's `GZipMiddleware` uses `compresslevel=9` (maximum compression). For typical responses like text and large binary meshes, setting `compresslevel=1` provides a massive speedup (e.g., 6x faster, from 4.67s to 0.77s for a 30MB mesh) while sacrificing almost no network compression ratio.
**Action:** When using `GZipMiddleware` in FastAPI for large payload delivery, explicitly configure `compresslevel=1` to optimize CPU usage and significantly reduce overall response latency.

## 2025-02-23 - FastAPI Threadpool Overhead for CPU Tasks
**Learning:** In FastAPI, endpoints defined with standard `def` (instead of `async def`) are automatically executed in an external threadpool. While this is crucial for preventing synchronous I/O from blocking the main event loop, it introduces context-switching overhead (~1-2ms per request). For fast, CPU-bound operations (like generating small XML configs or basic status returns), this overhead can exceed the execution time of the function itself, leading to suboptimal API throughput. Note that if the operation is slow, `def` should be used so it doesn't block the event loop.
**Action:** When implementing FastAPI endpoints that do not perform blocking I/O and are extremely fast, explicitly use `async def` to keep execution on the main thread and eliminate threadpool overhead.

## 2024-05-18 - [Optimize PyVista Normal Computation]
**Learning:** When using `mesh.compute_normals()` in PyVista to pre-compute point normals for visualization (e.g., for vtk.js), the default behavior of `auto_orient_normals=True` (or passing it explicitly) involves expensive topological traversals to ensure consistent global orientation. This can take a very long time (e.g. 33s on a 17M cell mesh). By setting both `auto_orient_normals=False` and `non_manifold_traversal=False`, PyVista only computes local triangle-based normals without the global traversal, speeding up the computation by 2-3x (e.g. 14s) without degrading the visual output in standard web viewers.
**Action:** When computing normals purely for basic 3D rendering where strict global normal orientation isn't mathematically required for simulation, always pass `auto_orient_normals=False` and `non_manifold_traversal=False` to `compute_normals()` to drastically reduce processing time on large meshes.

## 2024-05-18 - Optimize FastAPI File Upload Chunking
**Learning:** Python-level `while True:` chunked reading loops for FastAPI `UploadFile` introduce significant bytecode execution overhead, especially for large meshes. `shutil.copyfileobj` relies on highly optimized C implementations which eliminate this overhead.
**Action:** When saving an `UploadFile` where `upload_file.size` is populated and successfully validated against application thresholds (thereby making it safe to bypass memory checks in the loop), always use `shutil.copyfileobj(upload_file.file, buffer)` for a ~2-3x speedup, falling back to manual chunking only when size is unknown (e.g. chunked transfer encoding).
## 2024-05-09 - [File Traversal Optimization]
**Learning:** In Python, `os.listdir` followed by `os.path.getmtime` makes a separate `stat()` system call for every file, which is slow for directories with many files.
**Action:** Use `os.scandir` to iterate through directories, as it caches file attributes (like `is_file` and `st_mtime`) during traversal, eliminating redundant `stat()` calls and providing a significant speedup (e.g., 2.5x).
## 2024-05-18 - Avoid shutil.copyfileobj for file uploads
**Learning:** Using `shutil.copyfileobj` with `UploadFile.file` introduces a severe Disk Exhaustion (DoS) vulnerability. Relying on `upload_file.size` is unsafe because an attacker can spoof a small `Content-Length` header while uploading a massive file stream, completely bypassing size limits.
**Action:** Never use `shutil.copyfileobj` for FastAPI uploads; always use a chunked reading loop with explicit size tracking to safely terminate large uploads.

## 2025-05-11 - [Mesh Decimation for Large Visualization Surfaces]
**Learning:** Extracting and sending raw visualization surfaces (`.vtp`) of very large backend meshes (>100k cells) to the frontend creates severe network bandwidth bottlenecks and causes `vtk.js` WebGL rendering to freeze the browser tab. Because the frontend visualization is primarily for previewing boundary conditions (not exact node-level simulation fidelity), high triangle counts are unnecessary.
**Action:** Always dynamically decimate large visualization surfaces (e.g. `mesh.decimate(target_reduction)`) on the backend before saving/sending them to cap the total cell count (e.g. at 100,000 cells). This dramatically reduces network payloads (e.g. by 10x) and eliminates frontend rendering lag, drastically improving Time to Interactive.
## 2026-05-12 - [Optimize PyVista Mesh Operation Order]
**Learning:** PyVista operations like `compute_normals` scale linearly with the number of cells. By performing these operations before reducing the mesh size (e.g. `decimate`), we waste CPU time computing data for elements that will immediately be discarded. On large meshes, this causes significant delays (e.g., computing normals on a 2M cell mesh takes ~1.3s, while computing them on the decimated 200k cell mesh takes ~0.1s, yielding a >10x speedup).
**Action:** When preparing large meshes for visualization, always perform topological reduction (decimation) *before* computing rendering attributes like point normals to drastically reduce backend processing time.
## 2025-05-13 - [Optimize PyVista Surface Decimation]
**Learning:** PyVista's `decimate()` uses the `vtkQuadricDecimation` algorithm, which is highly accurate but slow. When simply capping cell counts for visual previews (e.g., `< 100k cells` for WebGL in vtk.js) where mathematically exact shape is not strictly necessary, `decimate_pro()` (which uses `vtkDecimatePro`) provides a >2x speedup (e.g. from 85s to 39s on a 4.5M cell mesh).
**Action:** When dynamically decimating very large backend meshes strictly for visualization/preview purposes, always use `decimate_pro()` instead of `decimate()` to minimize backend processing latency.
## 2025-05-14 - [Optimize np.bincount Unique Counting]
**Learning:** Using `np.bincount` to optimize unique counting of integer arrays (e.g., for mesh region/face IDs) from O(N log N) to O(N) requires OOM/DoS protection. Because `np.bincount` allocates memory based on `max(ids) - min(ids)`, it must be strictly enforced with a maximum allowed range (e.g., 10,000,000) before falling back to `np.unique`. Falling back too early at smaller sizes (like 100,000) creates unnecessary O(N log N) bottlenecks for typical large meshes.
**Action:** When using `np.bincount` on user-provided arrays, explicitly use a large but safe fallback threshold like 10,000,000 to maximize performance without allowing server OOM crashes.
## 2024-05-18 - [Optimize File IO]
**Learning:** Offloading non-essential, synchronous file system operations (like iterative cleanups via `os.scandir` in `_cleanup_old_uploads`) to FastAPI's `BackgroundTasks` rather than executing them in the main request-response path significantly optimizes the Time-To-First-Byte (TTFB) on critical API endpoints. It removes blocking execution delays for simple responses.
**Action:** Use `background_tasks.add_task(function)` to process non-essential IO tasks to prevent API delays.

## 2026-05-19 - [Optimize Decimation of Massive Meshes]
**Learning:** PyVista's `decimate_pro()` (which uses `vtkDecimatePro`) scales extremely poorly on massive meshes. For example, decimating an 8M cell mesh down to 100k cells can take over 60 seconds, which severely blocks the backend API and causes timeouts. By switching to `vtkQuadricClustering`, the decimation uses a fast spatial grid binning approach rather than iterative edge-collapsing, completing the same reduction in ~1.5s (>40x speedup). This algorithm is safe to use for frontend visual previews where mathematical topology isn't required.
**Action:** Always use `vtkQuadricClustering` instead of `decimate_pro()` or `decimate()` when capping the cell count of massive backend visualization meshes (>100k cells). Ensure `cluster.SetCopyCellData(True)` is enabled so the output preserves necessary Face/Region ID arrays for rendering.

## 2026-05-20 - [Frontend File Size Optimization]
**Learning:** While the backend correctly validates file size limits (e.g. 50MB) and returns a 413 response, relying solely on this for large uploads is extremely inefficient. The browser will still allocate massive amounts of memory to read the file into a `FormData` object and block the network connection trying to stream the payload, leading to delayed feedback and wasted bandwidth.
**Action:** Always implement an early return check for `file.size` on the frontend before generating `FormData` or calling `fetch`. This avoids freezing the browser tab, saves significant network overhead, and instantly surfaces the validation error to the user without any backend latency.

## 2024-05-25 - Debounce High-Frequency Background Tasks
**Learning:** Running full directory traversals (`os.scandir`) combined with `stat()` on every execution of a high-frequency endpoint (like file uploads) creates severe I/O bottlenecks and CPU exhaustion under concurrent load. Even though `os.scandir` is fast, `st_mtime` access triggers expensive system calls.
**Action:** Debounce expensive background cleanup tasks (e.g., using a global timestamp check) so they run periodically (e.g., once every 5 minutes) rather than strictly linearly per-request.

## 2025-05-15 - [Optimize PyVista Memory Usage with Inplace Operations]
**Learning:** By default, PyVista operations like `compute_normals()` allocate and return a completely new copy of the dataset. On large meshes (e.g., millions of cells), this creates severe memory pressure and triggers garbage collection overhead.
**Action:** When performing geometric operations on PyVista meshes where preserving the original, pre-operation state is not required (like final preparation of a visualization surface), always pass `inplace=True`. This modifies the existing C++ VTK data structures directly, eliminating the memory allocation overhead and providing a small CPU speedup.

## 2024-05-31 - [Optimize PyVista Mesh Bounds Computation]
**Learning:** Calling `mesh.bounds` on a PyVista/VTK mesh dataset forces an implicit O(N) traversal over all points if the bounding box has not already been cached. When generating metadata for frontend visualizers (like vtk.js), computing these bounds on the backend is completely redundant because the client-side WebGL engine computes its own viewport bounds natively (e.g., via `renderer.resetCamera()`). On massive meshes, this single attribute access creates a measurable, blocking CPU delay (e.g., ~20ms on a 4M point mesh).
**Action:** When extracting PyVista mesh metadata strictly for frontend rendering that handles its own camera bounding, do not access `mesh.bounds`. Pass an empty array `[]` instead to instantly bypass the O(N) traversal.
## 2026-05-21 - [Optimize WebGL Canvas Resizing]
**Learning:** Using `requestAnimationFrame` inside a `ResizeObserver` callback to trigger WebGL canvas resizes (e.g., `genericRenderWindow.resize()` in vtk.js) forces the browser to synchronously re-allocate massive WebGL framebuffers and recalculate layout 60 times per second during a continuous window resize, causing severe browser stutter and UI lockups.
**Action:** Always debounce heavy WebGL canvas resizes using `setTimeout` (e.g., 100ms) rather than `requestAnimationFrame`. This waits for the user to pause resizing before triggering the expensive WebGL update, providing a smooth UI resize experience.

## 2026-05-21 - [Svelte Reactivity Equality Checks]
**Learning:** In Svelte, trying to optimize frequent event handlers (like `dragover`) by manually wrapping primitive state assignments in equality checks (e.g., `if (!isDragging) isDragging = true;`) is a redundant micro-optimization. Svelte's compiler automatically injects strict equality checks (e.g., `not_equal`) under the hood and safely bails out of rendering cycles.
**Action:** Do not manually guard primitive assignments in Svelte with equality checks to "save renders", as it provides zero measurable performance benefit and adds unnecessary clutter.
## 2024-05-16 - Svelte Reactive Blocks and Global Stores Over-Triggering
**Learning:** In Svelte, a reactive statement (`$:`) that depends on a deeply nested object inside a global store (like `$simulationConfig.boundary_conditions`) will be triggered every time *any* property within that store updates (e.g., typing in a "Density" field). This can lead to severe O(N) rendering bottlenecks, especially when reconstructing objects or parsing arrays (like instantiating a new Set inside an `#each` loop's scope).
**Action:** Always memoize derived states in reactive blocks when depending on large global stores. A clean idiomatic way in Svelte is splitting the reactive block, letting Svelte automatically skip updates if the reference hasn't changed (e.g., `$: bcs = $simulationConfig.boundary_conditions; $: usedFaceNames = new Set(bcs.map(bc => bc.face_name));`). This ensures Svelte only recomputes and re-renders when the exact slice of state changes, preventing global keystroke lag.

## 2024-05-24 - Svelte Store Reactivity Memoization
**Learning:** In Svelte, reactive statements (`$:`) depending on deeply nested objects inside a global store (like `$store.property`) will re-trigger whenever *any* property within that store updates. Svelte's `safe_not_equal` considers objects/arrays as always changed upon assignment, leading to unnecessary expensive computations like mapping and Set creation for O(N) operations when unrelated fields are edited.
**Action:** Memoize derived states by explicitly tracking changes to the specific reference (e.g., `if (localRef !== $store.arrayRef)`) before running expensive mapping operations to prevent rendering bottlenecks.

## 2026-05-22 - [Optimize Connectivity on Massive Meshes]
**Learning:** Running `surface.connectivity()` on PyVista meshes with millions of cells creates a severe CPU bottleneck, blocking the thread for >10 seconds. When this is used as a fallback mechanism for finding mesh regions, the entire API becomes unresponsive.
**Action:** Always implement a cell count threshold (e.g., `surface.n_cells < 500_000`) to bypass computationally expensive connectivity calculations on massive meshes, falling back to a default surface instead.
## 2024-05-30 - Hardware-accelerating CSS filters
**Learning:** Indiscriminate use of `will-change: filter` on static elements without active animations is a premature optimization that can actually harm performance by consuming excessive VRAM and creating unnecessary composite layers.
**Action:** When optimizing CSS rendering for static elements with expensive filters (like `blur`), rely on `transform: translateZ(0)` to promote them to a hardware-accelerated layer to prevent main thread repaints, and reserve `will-change` only for properties that actively animate or change state.
## 2026-05-23 - [Optimize Request URL Parsing in FastAPI Middleware]
**Learning:** In FastAPI/Starlette middleware, repeatedly accessing `request.url.path` is an anti-pattern. Accessing `request.url` lazily instantiates an expensive `URL` object which requires parsing all headers and the underlying `request.scope` dictionary. In high-frequency middlewares (like rate limiting, size limits, and security headers), doing this multiple times per request creates a measurable CPU overhead. Accessing the raw string via `request.scope.get("path", "")` is roughly 10x faster.
**Action:** Always use `request.scope.get("path", "")` instead of `request.url.path` in Starlette/FastAPI middleware to instantly access the request path without expensive URL string parsing.
