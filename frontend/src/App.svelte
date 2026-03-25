<script>
    import MeshUpload from './lib/MeshUpload.svelte';
    import BCEditor from './lib/BCEditor.svelte';
    import XMLPreview from './lib/XMLPreview.svelte';
    import Viewer from './lib/Viewer.svelte';
    import { simulationConfig } from './stores';

    let activeTab = 'mesh';

    const tabs = [
        { key: 'mesh', label: 'Mesh' },
        { key: 'physics', label: 'Physics' },
        { key: 'bcs', label: 'Boundary Conditions' },
        { key: 'general', label: 'General' }
    ];
</script>

<div class="app-container">
    <div class="ambient ambient-1"></div>
    <div class="ambient ambient-2"></div>

    <header class="glass-shell">
        <div>
            <p class="eyebrow">svFSI Studio</p>
            <h1>svFSI Configurator</h1>
        </div>
    </header>

    <div class="main-layout">
        <aside class="sidebar glass-shell">
            <nav>
                {#each tabs as tab}
                    <button
                        class:active={activeTab === tab.key}
                        on:click={() => activeTab = tab.key}
                    >
                        {tab.label}
                    </button>
                {/each}
            </nav>

            <div class="config-panel">
                {#if activeTab === 'mesh'}
                    <MeshUpload />
                    <div class="note glass-inline">
                        <p>Upload a .vtu or .vtp file to visualize and assign BCs.</p>
                    </div>
                {:else if activeTab === 'physics'}
                    <div class="physics-config">
                        <h3>Physics</h3>
                        <label>
                            Type
                            <select bind:value={$simulationConfig.physics.physics_type}>
                                <option value="Fluid">Fluid</option>
                                <option value="Structure">Structure</option>
                            </select>
                        </label>
                        <label>Density <input type="number" bind:value={$simulationConfig.physics.density} step="0.1" /></label>
                        <label>Viscosity <input type="number" bind:value={$simulationConfig.physics.viscosity} step="0.01" /></label>
                    </div>
                {:else if activeTab === 'bcs'}
                    <BCEditor />
                {:else if activeTab === 'general'}
                    <div class="general-config">
                        <h3>General Settings</h3>
                        <label>Time Steps <input type="number" bind:value={$simulationConfig.general.num_time_steps} /></label>
                        <label>Step Size <input type="number" bind:value={$simulationConfig.general.time_step_size} step="0.001" /></label>
                    </div>
                {/if}
            </div>
        </aside>

        <main class="content">
            <div class="top-pane glass-shell">
                <Viewer />
            </div>
            <div class="bottom-pane glass-shell">
                <XMLPreview />
            </div>
        </main>
    </div>
</div>

<style>
    :global(body) {
        margin: 0;
        font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        color: #eef2ff;
        background: radial-gradient(circle at 20% 20%, #1f3f80 0%, #101325 40%, #080911 100%);
    }

    .app-container {
        min-height: 100vh;
        padding: 1rem;
        position: relative;
        overflow: hidden;
    }

    .ambient {
        position: absolute;
        border-radius: 50%;
        filter: blur(70px);
        opacity: 0.35;
        pointer-events: none;
    }

    .ambient-1 {
        width: 300px;
        height: 300px;
        background: #3eb5ff;
        top: -80px;
        left: -80px;
    }

    .ambient-2 {
        width: 360px;
        height: 360px;
        background: #8f68ff;
        bottom: -130px;
        right: -100px;
    }

    .glass-shell {
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 18px;
        background: rgba(14, 19, 40, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
    }

    header {
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
    }

    .eyebrow {
        margin: 0;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #b7c3ff;
    }

    h1 {
        margin: 0.2rem 0 0;
        font-size: 1.45rem;
    }

    .main-layout {
        display: flex;
        height: calc(100vh - 122px);
        gap: 1rem;
        position: relative;
        z-index: 2;
    }

    .sidebar {
        width: 320px;
        display: flex;
        flex-direction: column;
        padding: 1rem;
        overflow-y: auto;
    }

    nav {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.6rem;
        margin-bottom: 1rem;
    }

    nav button {
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.08);
        color: #dbe3ff;
        border-radius: 12px;
        padding: 0.55rem 0.75rem;
        cursor: pointer;
        transition: 0.2s ease;
    }

    nav button:hover {
        transform: translateY(-1px);
        border-color: rgba(255, 255, 255, 0.35);
    }

    nav button.active {
        background: linear-gradient(135deg, rgba(96, 147, 255, 0.65), rgba(155, 116, 255, 0.65));
        color: #fff;
    }

    .content {
        flex: 1;
        display: grid;
        grid-template-rows: 1fr 1fr;
        gap: 1rem;
        min-width: 0;
    }

    .top-pane,
    .bottom-pane {
        padding: 1rem;
        overflow: hidden;
    }

    .glass-inline {
        border: 1px solid rgba(255, 255, 255, 0.16);
        background: rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 0.75rem;
        margin-top: 0.75rem;
    }

    label {
        display: block;
        margin-bottom: 0.65rem;
        color: #dbe4ff;
    }

    input, select {
        width: 100%;
        margin-top: 0.3rem;
        padding: 0.45rem 0.55rem;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 10px;
        background: rgba(12, 18, 40, 0.45);
        color: #f3f6ff;
    }
</style>
