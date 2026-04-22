<script>
    import { meshMetadata, simulationConfig } from '../stores';

    let fileInput;
    let loading = false;
    let error = "";
    let isDragging = false;

    function handleDragOver() {
        if (!loading) isDragging = true;
    }

    function handleDragLeave() {
        isDragging = false;
    }

    function handleDrop(e) {
        isDragging = false;
        if (loading) return;
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect();
        }
    }

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

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || "Failed to process mesh");
            }

            const data = await response.json();

            // ⚡ Bolt: Eliminate redundant network download for .vtp files.
            // If the user uploads a surface mesh (.vtp), the backend returns it as-is.
            // By passing a local Blob URL instead of the filename, we prevent the Viewer
            // from re-downloading the exact same file from the server, saving huge amounts
            // of network bandwidth and instantly rendering the mesh.
            if (file.name.toLowerCase().endsWith('.vtp')) {
                // ⚡ Bolt: Revoke the old Blob URL to prevent memory leaks.
                // Creating a new blob URL for every upload without revoking the old one
                // leaves large mesh files in memory indefinitely.
                if ($meshMetadata.viz_file && $meshMetadata.viz_file.startsWith('blob:')) {
                    URL.revokeObjectURL($meshMetadata.viz_file);
                }
                data.viz_file = URL.createObjectURL(file);
            }

            meshMetadata.set(data);
            simulationConfig.update(c => {
                c.mesh.mesh_path = file.name;
                return c;
            });
        } catch (e) {
            error = e.message;
            if (fileInput) fileInput.value = "";
        } finally {
            loading = false;
        }
    }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
    class="mesh-upload"
    class:dragging={isDragging}
    on:dragover|preventDefault={handleDragOver}
    on:dragleave={handleDragLeave}
    on:drop|preventDefault={handleDrop}
>
    <h3>Mesh Upload</h3>
    <input type="file" bind:this={fileInput} on:change={handleFileSelect} accept=".vtu,.vtp,.vtk" aria-label="Upload Mesh File" disabled={loading} />
    <p class="drop-hint">or drag and drop a file here</p>
    {#if loading}
        <p role="status" aria-live="polite">Processing mesh...</p>
    {/if}
    {#if error}
        <p class="error" role="alert" aria-live="assertive">{error}</p>
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
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }

    .mesh-upload.dragging {
        border-color: #6093ff;
        background: rgba(96, 147, 255, 0.1);
    }

    .drop-hint {
        font-size: 0.85rem;
        color: #b8c5ef;
        opacity: 0.8;
        margin: 0.5rem 0 0 0;
        font-style: italic;
    }

    .error {
        color: #ffc2c2;
    }

    .mesh-info {
        margin-top: 0.65rem;
        font-size: 0.93rem;
        color: #dbe4ff;
    }
</style>
