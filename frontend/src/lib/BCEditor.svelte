<script>
    import { simulationConfig, meshMetadata } from '../stores';

    let selectedFace = "";
    let bcType = "Dirichlet";
    let variable = "Velocity";
    let value = 0.0;
    let profile = "Flat";

    function addBC() {
        if (!selectedFace) return;
        simulationConfig.update(c => {
            const newBC = {
                face_name: selectedFace,
                bc_type: bcType,
                variable: variable,
                value: parseFloat(value),
                profile: profile,
                face_id: $meshMetadata.faces.find(f => f.name === selectedFace)?.id
            };
            c.boundary_conditions = [...c.boundary_conditions, newBC];
            return c;
        });
    }

    function removeBC(index) {
        simulationConfig.update(c => {
            c.boundary_conditions = c.boundary_conditions.filter((_, i) => i !== index);
            return c;
        });
    }
</script>

<div class="bc-editor">
    <h3>Boundary Conditions</h3>

    {#if $meshMetadata.faces.length > 0}
        <div class="add-bc">
            <select bind:value={selectedFace} aria-label="Select Face" title="Select Face">
                <option value="" disabled selected>Select Face</option>
                {#each $meshMetadata.faces as face}
                    <option value={face.name}>{face.name} (ID: {face.id})</option>
                {/each}
            </select>

            <select bind:value={bcType} aria-label="Boundary Condition Type" title="Boundary Condition Type">
                <option value="Dirichlet">Dirichlet</option>
                <option value="Neumann">Neumann</option>
                <option value="Resistance">Resistance</option>
            </select>

            <input type="text" bind:value={variable} aria-label="Variable Name" title="Variable Name" placeholder="Variable (e.g. Velocity)" />
            <input type="number" bind:value={value} aria-label="Value" title="Value" step="0.1" />

            <select bind:value={profile} aria-label="Profile" title="Profile">
                <option value="Flat">Flat</option>
                <option value="Parabolic">Parabolic</option>
            </select>

            <button on:click={addBC} disabled={!selectedFace} title={!selectedFace ? "Select a face first to add a boundary condition" : "Add boundary condition"}>Add BC</button>
        </div>

        {#if $simulationConfig.boundary_conditions.length === 0}
            <p class="empty-state">No boundary conditions added yet. Select a face and configure parameters above to add one.</p>
        {:else}
            <ul>
                {#each $simulationConfig.boundary_conditions as bc, i}
                    <li>
                        {bc.face_name}: {bc.bc_type} {bc.variable}={bc.value} ({bc.profile})
                        <button on:click={() => removeBC(i)} aria-label="Remove boundary condition" title="Remove boundary condition">x</button>
                    </li>
                {/each}
            </ul>
        {/if}
    {:else}
        <p class="empty-state" role="alert">Please upload a mesh file first to detect faces and configure boundary conditions.</p>
    {/if}
</div>

<style>
    .bc-editor {
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .add-bc {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .empty-state {
        color: #b8c5ef;
        font-style: italic;
        margin-top: 1rem;
    }

    ul {
        padding-left: 1rem;
    }
</style>
