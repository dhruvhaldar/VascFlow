
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
