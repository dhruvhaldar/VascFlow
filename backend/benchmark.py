import pyvista as pv
import time

# Create a large sphere to simulate a large mesh
print("Generating large mesh...")
mesh = pv.Sphere(theta_resolution=1000, phi_resolution=1000)
mesh.clear_data() # remove normals
print(f"Mesh generated with {mesh.n_cells} cells.")

# Time compute_normals on large mesh
start = time.time()
mesh.compute_normals(cell_normals=False, point_normals=True, auto_orient_normals=False, non_manifold_traversal=False)
t_large = time.time() - start
print(f"compute_normals on large mesh: {t_large:.4f}s")

# Decimate
target_reduction = 1.0 - (100000 / mesh.n_cells)
if target_reduction > 0.9:
    target_reduction = 0.9
decimated = mesh.decimate(target_reduction)
print(f"Decimated mesh has {decimated.n_cells} cells.")

# Time compute_normals on decimated mesh
decimated.clear_data()
start = time.time()
decimated.compute_normals(cell_normals=False, point_normals=True, auto_orient_normals=False, non_manifold_traversal=False)
t_small = time.time() - start
print(f"compute_normals on decimated mesh: {t_small:.4f}s")
print(f"Speedup for compute_normals: {t_large/t_small:.2f}x")
