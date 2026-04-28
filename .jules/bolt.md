
## 2025-04-26 - [Optimize PyVista Surface Extraction Algorithm]
**Learning:** By default, PyVista's `extract_surface()` on an `UnstructuredGrid` uses the `vtkDataSetSurfaceFilter` (algorithm `'dataset_surface'`). While passing `pass_pointid=False, pass_cellid=False` avoids computing original ID maps, switching the algorithm explicitly to `None` (`vtkGeometryFilter`) provides an additional ~10x to 30x performance speedup (e.g. from 0.9s to 0.02s on a 1M cell mesh) without losing necessary cell data mapping like `FaceID` arrays.
**Action:** When extracting outer surfaces from volumetric meshes using PyVista where maintaining volume cell and point ID mapping is unnecessary, explicitly set `algorithm=None` along with `pass_pointid=False, pass_cellid=False` for maximum performance.

## 2024-04-28 - [Optimize FastAPI GZipMiddleware compression level]
**Learning:** By default, FastAPI/Starlette's `GZipMiddleware` uses `compresslevel=9` (maximum compression). For typical responses like text and large binary meshes, setting `compresslevel=1` provides a massive speedup (e.g., 6x faster, from 4.67s to 0.77s for a 30MB mesh) while sacrificing almost no network compression ratio.
**Action:** When using `GZipMiddleware` in FastAPI for large payload delivery, explicitly configure `compresslevel=1` to optimize CPU usage and significantly reduce overall response latency.
