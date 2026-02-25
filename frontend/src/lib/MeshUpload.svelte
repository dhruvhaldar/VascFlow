<script>
    import { meshMetadata, simulationConfig } from '../stores';

    let fileInput;
    let loading = false;
    let error = "";

    async function handleFileSelect() {
        if (!fileInput.files.length) return;
        const file = fileInput.files[0];

        loading = true;
        error = "";

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://localhost:8000/process_mesh", {
                method: "POST",
                body: formData
            });

            if (!response.ok) throw new Error("Failed to process mesh");

            const data = await response.json();
            meshMetadata.set(data);
            simulationConfig.update(c => {
                c.mesh.mesh_path = file.name;
                return c;
            });
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }
</script>

<div class="mesh-upload">
    <h3>Mesh Upload</h3>
    <input type="file" bind:this={fileInput} on:change={handleFileSelect} accept=".vtu,.vtp,.vtk" />
    {#if loading}
        <p>Processing mesh...</p>
    {/if}
    {#if error}
        <p style="color: red;">{error}</p>
    {/if}
    {#if $meshMetadata.n_cells > 0}
        <div class="mesh-info">
            <p>Loaded: {$simulationConfig.mesh.mesh_path}</p>
            <p>Cells: {$meshMetadata.n_cells}, Points: {$meshMetadata.n_points}</p>
            <p>Detected Faces: {$meshMetadata.faces.length}</p>
        </div>
    {/if}
</div>

<style>
    .mesh-upload {
        border: 1px solid #ccc;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
