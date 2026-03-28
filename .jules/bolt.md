## 2024-05-24 - PyVista Face Aggregation Bottleneck
**Learning:** Extracting metadata from large `.vtu` / `.vtp` meshes using PyVista and NumPy in `mesh_service.py` was an $O(N \times K)$ bottleneck when checking unique region/face IDs using `np.sum(array == uid)` in a loop.
**Action:** Always use `np.unique(..., return_counts=True)` for single-pass $O(N \log N)$ counting when dealing with large PyVista cell_data arrays, explicitly casting the resulting counts back to `int()` for FastAPI/JSON serialization.

## 2024-03-22 - Python XML Generation Performance Trap
**Learning:** Using `minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")` to format ElementTree objects is a major performance bottleneck because it re-parses the entire XML tree back into memory as a DOM structure just to add indentation.
**Action:** Always use `xml.etree.ElementTree.indent(tree, space="   ")` (introduced in Python 3.9) to modify the ElementTree in place, avoiding the expensive double parsing and string conversion steps.

## 2024-05-20 - vtk.js WebGL Memory Leaks
**Learning:** `vtk.js` does not rely on JavaScript garbage collection. Objects like `vtkXMLPolyDataReader`, `vtkMapper`, and `vtkActor` retain WebGL buffers and heap memory even if no longer referenced in JS. Failing to call `.delete()` on these instances when they are replaced or when components unmount leads to severe memory leaks and eventual browser tab crashes.
**Action:** Always track `vtk.js` instances (especially readers, mappers, actors, and render windows) and explicitly call `.delete()` on the old instances before creating new ones or when tearing down a component.

## 2024-05-24 - Redundant Disk I/O on Mesh Upload
**Learning:** The FastAPI backend offloads `process_mesh` to a threadpool for synchronous operations (like reading PyVista meshes). When users upload `.vtp` files, PyVista was configured to unnecessarily rewrite the entire mesh back to the same path before returning it to the frontend.
**Action:** Always check if a target visualization file path equals the original uploaded file path to avoid redundant write operations (`if viz_path != file_path:`), particularly when working with large files and large datasets where disk I/O blocks a thread for significant amounts of time.
