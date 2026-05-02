<script>
    import { onMount } from 'svelte';
    import { meshMetadata, simulationConfig } from '../stores';
    import vtkGenericRenderWindow from '@kitware/vtk.js/Rendering/Misc/GenericRenderWindow';
    import vtkXMLPolyDataReader from '@kitware/vtk.js/IO/XML/XMLPolyDataReader';
    import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
    import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';

    let container;
    let genericRenderWindow;
    let renderer;
    let renderWindow;
    let currentVizFile = "";
    let isLoading = false;

    // ⚡ Bolt: Track vtk.js objects for explicit memory management
    let currentReader = null;
    let currentMapper = null;
    let currentActor = null;

    $: {
        if ($meshMetadata.viz_file && $meshMetadata.viz_file !== currentVizFile) {
            currentVizFile = $meshMetadata.viz_file;
            loadMesh(currentVizFile);
        }
    }

    onMount(() => {
        if (!container) return;

        genericRenderWindow = vtkGenericRenderWindow.newInstance();
        genericRenderWindow.setContainer(container);

        let resizeTimeout;
        const resizeObserver = new ResizeObserver(() => {
            if (resizeTimeout) cancelAnimationFrame(resizeTimeout);
            resizeTimeout = requestAnimationFrame(() => {
                if (genericRenderWindow) {
                    genericRenderWindow.resize();
                }
            });
        });
        resizeObserver.observe(container);

        renderer = genericRenderWindow.getRenderer();
        renderWindow = genericRenderWindow.getRenderWindow();

        renderer.setBackground(0.03, 0.05, 0.12);
        renderWindow.render();

        return () => {
            resizeObserver.disconnect();
            if (genericRenderWindow) {
                genericRenderWindow.delete();
            }
            if (currentActor) currentActor.delete();
            if (currentMapper) currentMapper.delete();
            if (currentReader) currentReader.delete();
        };
    });

    async function loadMesh(filename) {
        if (!renderer) return;

        isLoading = true;

        // ⚡ Bolt: Handle both external backend URLs and local Blob URLs.
        // If it's a blob: URL (from MeshUpload bypass), we load it directly without
        // prefixing the backend address.
        const url = filename.startsWith('blob:')
            ? filename
            : `http://localhost:8000/files/${filename}`;

        // ⚡ Bolt: Reuse the vtk.js rendering pipeline instead of recreating it.
        // Destroying and recreating vtkActor, vtkMapper, and vtkReader on every file load
        // forces WebGL to constantly discard and reallocate heavy GPU buffers. By reusing
        // the existing pipeline, we significantly reduce memory fragmentation, garbage
        // collection pauses, and mesh switching latency.
        if (!currentReader) {
            currentReader = vtkXMLPolyDataReader.newInstance();
            currentMapper = vtkMapper.newInstance();
            currentMapper.setInputConnection(currentReader.getOutputPort());
            currentActor = vtkActor.newInstance();
            currentActor.setMapper(currentMapper);
            renderer.addActor(currentActor);
        }

        try {
            await currentReader.setUrl(url);
            await currentReader.loadData();

            renderer.resetCamera();
            renderWindow.render();
        } catch (e) {
            console.error("Failed to load mesh", e);
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="viewer-wrap">
    <div class="viewer-header">
        <h3>3D Visualizer</h3>
        <span role="status" aria-live="polite">
            {#if isLoading}
                Loading 3D model...
            {:else if $meshMetadata.viz_file}
                Previewing {$simulationConfig.mesh.mesh_path || 'Mesh'}
            {:else}
                Upload a mesh to render it
            {/if}
        </span>
    </div>
    <div class="viewer-container" data-testid="viewer-canvas">
        {#if !$meshMetadata.viz_file && !isLoading}
            <div class="empty-state">
                <p>No mesh uploaded yet.</p>
                <p class="subtext">Upload a .vtu or .vtp file from the Mesh tab to visualize it here.</p>
            </div>
        {/if}
        {#if isLoading}
            <div class="loading-overlay" aria-hidden="true">
                <div class="spinner"></div>
                <p>Loading 3D model...</p>
            </div>
        {/if}
        <div class="canvas-mount" bind:this={container}></div>
    </div>
</div>

<style>
    .empty-state {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #b8c5ef;
        text-align: center;
        pointer-events: none;
        z-index: 10;
    }

    .empty-state p {
        margin: 0.25rem 0;
    }

    .empty-state .subtext {
        font-size: 0.85rem;
        opacity: 0.8;
    }

    .canvas-mount {
        width: 100%;
        height: 100%;
    }
    .viewer-wrap {
        height: 100%;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .viewer-header h3 {
        margin: 0;
    }

    .viewer-header span {
        color: #9fb0e6;
        font-size: 0.85rem;
    }

    .viewer-container {
        width: 100%;
        flex: 1;
        min-height: 330px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 14px;
        background: radial-gradient(circle at 10% 10%, rgba(59, 94, 176, 0.35), rgba(4, 5, 14, 0.8));
        position: relative;
        overflow: hidden;
    }

    .loading-overlay {
        position: absolute;
        inset: 0;
        background: rgba(4, 5, 14, 0.65);
        backdrop-filter: blur(4px);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10;
        color: #b8c5ef;
    }

    .spinner {
        width: 30px;
        height: 30px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top-color: #6093ff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 0.75rem;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
