<script>
    import { onMount, onDestroy } from 'svelte';
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

    // React to mesh changes in metadata
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

        // Handle resize
        const resizeObserver = new ResizeObserver(() => {
            genericRenderWindow.resize();
        });
        resizeObserver.observe(container);

        renderer = genericRenderWindow.getRenderer();
        renderWindow = genericRenderWindow.getRenderWindow();

        renderer.setBackground(0.1, 0.2, 0.3); // Dark blue-ish
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

        // Always assume PolyData (.vtp) as backend converts/extracts surface
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

<div class="viewer-container" bind:this={container}></div>

<style>
    .viewer-container {
        width: 100%;
        height: 500px;
        background: #000;
        border: 1px solid #444;
        position: relative;
    }
</style>
