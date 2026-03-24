## 2024-05-24 - PyVista Face Aggregation Bottleneck
**Learning:** Extracting metadata from large `.vtu` / `.vtp` meshes using PyVista and NumPy in `mesh_service.py` was an $O(N \times K)$ bottleneck when checking unique region/face IDs using `np.sum(array == uid)` in a loop.
**Action:** Always use `np.unique(..., return_counts=True)` for single-pass $O(N \log N)$ counting when dealing with large PyVista cell_data arrays, explicitly casting the resulting counts back to `int()` for FastAPI/JSON serialization.
