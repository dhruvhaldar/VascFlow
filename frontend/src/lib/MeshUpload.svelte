<script>
    import { tick } from 'svelte';
    import { slide } from 'svelte/transition';
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

        // ⚡ Bolt: Add an early return for files larger than 50MB.
        // This prevents the browser from allocating memory for the file in a FormData
        // object and initiating a network request that the backend will inevitably
        // reject. This saves massive network bandwidth and provides instant UI feedback.
        if (file.size > 50 * 1024 * 1024) {
            error = "File too large. Maximum size is 50MB.";
            if (fileInput) fileInput.value = "";
            return;
        }

        loading = true;
        error = "";

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://localhost:8000/process_mesh", {
                method: "POST",
                body: formData,
                signal: AbortSignal.timeout(60000)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                let errMsg = "Failed to process mesh";
                if (errData.detail) {
                    errMsg = Array.isArray(errData.detail)
                        ? errData.detail.map(d => `${d.loc ? d.loc[d.loc.length - 1] + ': ' : ''}${d.msg}`).join(", ")
                        : errData.detail;
                }
                throw new Error(errMsg);
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
            if (e.name === 'TimeoutError') {
                error = "Upload timed out. The server took too long to respond.";
            } else {
                error = e.message;
            }
            if (fileInput) fileInput.value = "";
        } finally {
            loading = false;

            // 🎨 Palette: Manage focus after async operation
            // The file input is disabled during upload, which causes it to lose focus.
            // Wait for it to be re-enabled and explicitly restore focus so keyboard navigation can continue.
            await tick();
            if (fileInput) fileInput.focus();
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
    <input type="file" bind:this={fileInput} on:change={handleFileSelect} accept=".vtu,.vtp,.vtk" aria-label="Upload Mesh File" title={loading ? "Processing upload, please wait..." : "Choose a mesh file to upload"} disabled={loading} aria-invalid={!!error} aria-describedby={error ? "mesh-upload-error" : undefined} />
    {#if !loading}
        <p class="drop-hint" aria-hidden="true">{isDragging ? 'Drop file to upload...' : 'or drag and drop a file here'}</p>
    {/if}
    {#if loading}
        <div class="loading-state" role="status" aria-live="polite" transition:slide|local>
            <span class="inline-spinner" aria-hidden="true"></span>
            <p>Processing mesh...</p>
        </div>
    {/if}
    {#if error}
        <p id="mesh-upload-error" class="error" role="alert" aria-live="assertive" transition:slide|local>{error}</p>
    {/if}
    {#if $meshMetadata.n_cells > 0}
        <div class="mesh-info" role="status" aria-live="polite" transition:slide|local>
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

    .mesh-upload:focus-within {
        border-color: #6093ff;
        background: rgba(96, 147, 255, 0.08);
    }

    .drop-hint {
        font-size: 0.85rem;
        color: #b8c5ef;
        opacity: 0.8;
        margin: 0.5rem 0 0 0;
        font-style: italic;
    }

    .loading-state {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.5rem;
        color: #9fb0e6;
    }

    .loading-state p {
        margin: 0;
    }

    .inline-spinner {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.25);
        border-top-color: #6093ff;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        display: inline-block;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
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
