<script>
    import MeshUpload from './lib/MeshUpload.svelte';
    import BCEditor from './lib/BCEditor.svelte';
    import XMLPreview from './lib/XMLPreview.svelte';
    import Viewer from './lib/Viewer.svelte';
    import { simulationConfig } from './stores';

    // Simple state for tabs
    let activeTab = 'mesh';
</script>

<div class="app-container">
    <header>
        <h1>svFSI Configurator</h1>
    </header>

    <div class="main-layout">
        <aside class="sidebar">
            <nav>
                <button class:active={activeTab === 'mesh'} on:click={() => activeTab = 'mesh'}>Mesh</button>
                <button class:active={activeTab === 'physics'} on:click={() => activeTab = 'physics'}>Physics</button>
                <button class:active={activeTab === 'bcs'} on:click={() => activeTab = 'bcs'}>Boundary Conditions</button>
                <button class:active={activeTab === 'general'} on:click={() => activeTab = 'general'}>General</button>
            </nav>

            <div class="config-panel">
                {#if activeTab === 'mesh'}
                    <MeshUpload />
                    <div class="note">
                        <p>Upload a .vtu or .vtp file to visualize and assign BCs.</p>
                    </div>
                {:else if activeTab === 'physics'}
                    <div class="physics-config">
                        <h3>Physics</h3>
                        <label>
                            Type:
                            <select bind:value={$simulationConfig.physics.physics_type}>
                                <option value="Fluid">Fluid</option>
                                <option value="Structure">Structure</option>
                            </select>
                        </label>
                        <!-- Simple props -->
                        <label>Density: <input type="number" bind:value={$simulationConfig.physics.density} step="0.1"/></label>
                        <label>Viscosity: <input type="number" bind:value={$simulationConfig.physics.viscosity} step="0.01"/></label>
                    </div>
                {:else if activeTab === 'bcs'}
                    <BCEditor />
                {:else if activeTab === 'general'}
                    <div class="general-config">
                        <h3>General Settings</h3>
                        <label>Time Steps: <input type="number" bind:value={$simulationConfig.general.num_time_steps}/></label>
                        <label>Step Size: <input type="number" bind:value={$simulationConfig.general.time_step_size} step="0.001"/></label>
                    </div>
                {/if}
            </div>
        </aside>

        <main class="content">
            <div class="top-pane">
                <Viewer />
            </div>
            <div class="bottom-pane">
                <XMLPreview />
            </div>
        </main>
    </div>
</div>

<style>
    :global(body) {
        margin: 0;
        font-family: sans-serif;
    }
    .app-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    header {
        background: #333;
        color: white;
        padding: 0.5rem 1rem;
    }
    .main-layout {
        display: flex;
        flex: 1;
        overflow: hidden;
    }
    .sidebar {
        width: 300px;
        background: #f5f5f5;
        border-right: 1px solid #ccc;
        display: flex;
        flex-direction: column;
        padding: 1rem;
        overflow-y: auto;
    }
    nav {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    nav button {
        text-align: left;
        padding: 0.5rem;
        background: #ddd;
        border: none;
        cursor: pointer;
    }
    nav button.active {
        background: #007bff;
        color: white;
    }
    .content {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 1rem;
        gap: 1rem;
        overflow-y: auto;
    }
    .top-pane {
        flex: 1;
        min-height: 400px;
    }
    .bottom-pane {
        flex: 1;
        min-height: 300px;
    }
    label {
        display: block;
        margin-bottom: 0.5rem;
    }
    input, select {
        width: 100%;
        padding: 0.3rem;
        margin-top: 0.2rem;
    }
</style>
