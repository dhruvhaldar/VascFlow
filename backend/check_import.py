import sys
sys.path.append('.')
try:
    import backend.mesh_service
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
