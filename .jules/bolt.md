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

## 2024-06-03 - PyVista Copy Optimization
**Learning:** Calling `surface.copy()` on a large PyVista mesh copies all point and cell data arrays, taking significant memory and time ($O(N)$ with respect to data size), even if the data arrays are subsequently deleted. For meshes with extensive simulation results, this can be a major performance bottleneck during file processing.
**Action:** When extracting geometry for visualization and only specific arrays are needed (like 'Normals' and 'TCoords'), use `pv.PolyData().copy_structure(surface)` to copy only the geometry and topology. Then explicitly copy only the required arrays over. This approach dramatically improves performance and reduces memory usage compared to copying everything and then deleting unneeded arrays.

## 2024-03-29 - [Massive vtk.js Bundle Code Splitting]
**Learning:** Svelte synchronously importing heavy 3D rendering libraries like `vtk.js` in root components blocks initial load, turning an SPA into a massive 1MB+ monolithic download.
**Action:** Use Svelte's `{#await import('./Component.svelte')}...{:then {default: Component}}...{/await}` syntax to lazily load and code-split the 3D Viewer. This cleanly separates visualization logic into async chunks while maintaining UI layout with loading placeholders.
