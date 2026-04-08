## 2025-04-06 - [Optimize PyVista mesh processing]
**Learning:** PyVista's `surface.copy()` performs a deep copy, which is very inefficient when only the topology/geometry is needed (e.g. for generating visualization meshes from large simulation meshes with heavy point/cell data arrays). Copying only the required attributes via `CopyStructure()` and selectively attaching visualization arrays reduces processing time by a factor of >1000x for large meshes and saves considerable memory.
**Action:** When deriving structural visualization meshes from rich VTK/VTU data with PyVista, use `pv.PolyData().CopyStructure(surface)` instead of `.copy()` and selectively transfer only necessary visualization arrays like 'Normals' or 'TCoords'.

## 2025-04-06 - [Avoid tracking original IDs in extract_surface]
**Learning:** By default, PyVista's `extract_surface()` computes and passes arrays containing the original point and cell IDs from the volume mesh to the extracted surface mesh. For large meshes, calculating and passing these IDs is computationally expensive (can take ~30s on a 15M cell mesh vs ~5s without it).
**Action:** When extracting a surface from a volume mesh where tracking original point/cell IDs is unnecessary, explicitly pass `pass_pointid=False, pass_cellid=False` to `extract_surface()` to skip this work and significantly speed up processing.
