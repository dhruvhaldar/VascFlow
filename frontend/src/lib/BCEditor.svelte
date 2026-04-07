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
        const bcName = $simulationConfig.boundary_conditions[index].face_name;
        if (confirm(`Are you sure you want to remove the boundary condition for ${bcName}?`)) {
            simulationConfig.update(c => {
                c.boundary_conditions = c.boundary_conditions.filter((_, i) => i !== index);
                return c;
            });
        }
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
                        <span class="bc-info">{bc.face_name}: {bc.bc_type} {bc.variable}={bc.value} ({bc.profile})</span>
                        <button class="delete-btn" on:click={() => removeBC(i)} aria-label="Remove boundary condition for {bc.face_name}" title="Remove boundary condition">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                        </button>
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
        list-style: none;
        padding: 0;
        margin-top: 1rem;
    }

    li {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }

    .bc-info {
        font-size: 0.95rem;
    }

    .delete-btn {
        background: rgba(255, 100, 100, 0.1);
        color: #ffb3b3;
        border: 1px solid rgba(255, 100, 100, 0.2);
        padding: 0.3rem 0.4rem;
        border-radius: 6px;
        cursor: pointer;
        display: flex;
        align-items: center;
        transition: 0.2s ease;
    }

    .delete-btn:hover {
        background: rgba(255, 100, 100, 0.2);
    }
</style>
