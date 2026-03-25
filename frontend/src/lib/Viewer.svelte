<script>
    import { onMount } from 'svelte';
    import { meshMetadata } from '../stores';
    import vtkGenericRenderWindow from '@kitware/vtk.js/Rendering/Misc/GenericRenderWindow';
    import vtkXMLPolyDataReader from '@kitware/vtk.js/IO/XML/XMLPolyDataReader';
    import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
    import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';

    let container;
    let genericRenderWindow;
    let renderer;
    let renderWindow;
    let currentVizFile = "";

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
        };
    });

    async function loadMesh(filename) {
        if (!renderer) return;

        const url = `http://localhost:8000/files/${filename}`;
        const reader = vtkXMLPolyDataReader.newInstance();

        try {
            await reader.setUrl(url);
            await reader.loadData();

            const mapper = vtkMapper.newInstance();
            mapper.setInputConnection(reader.getOutputPort());

            const actor = vtkActor.newInstance();
            actor.setMapper(mapper);

            renderer.removeAllViewProps();
            renderer.addActor(actor);
            renderer.resetCamera();
            renderWindow.render();
        } catch (e) {
            console.error("Failed to load mesh", e);
        }
    }
</script>

<div class="viewer-wrap">
    <div class="viewer-header">
        <h3>3D Visualizer</h3>
        <span>{$meshMetadata.viz_file ? `Previewing ${$meshMetadata.viz_file}` : 'Upload a mesh to render it'}</span>
    </div>
    <div class="viewer-container" data-testid="viewer-canvas" bind:this={container}></div>
</div>

<style>
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
</style>
