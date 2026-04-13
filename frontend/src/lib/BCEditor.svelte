<script>
    import { simulationConfig, meshMetadata } from '../stores';

    let selectedFace = "";
    let bcType = "Dirichlet";
    let variable = "Velocity";
    let value = 0.0;
    let profile = "Flat";

    // ⚡ Bolt: Cache used face names in a reactive Set for O(1) lookups.
    // Calling array.some() twice per option inside an #each loop creates an
    // O(N*M) rendering bottleneck for meshes with many faces. Using a Set
    // reduces this to O(N+M), significantly improving UI responsiveness when
    // opening the dropdown or adding new boundary conditions.
    $: usedFaceNames = new Set($simulationConfig.boundary_conditions.map(bc => bc.face_name));

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
        selectedFace = "";
    }

    function removeBC(index, faceName) {
        if (window.confirm(`Are you sure you want to remove the boundary condition for ${faceName}?`)) {
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
        <form class="add-bc" on:submit|preventDefault={addBC}>
            <select bind:value={selectedFace} aria-label="Select Face" title="Select Face">
                <option value="" disabled selected>Select Face</option>
                {#each $meshMetadata.faces as face}
                    <option
                        value={face.name}
                        disabled={usedFaceNames.has(face.name)}
                    >
                        {face.name} (ID: {face.id}) {usedFaceNames.has(face.name) ? '(Already Added)' : ''}
                    </option>
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

            <button type="submit" disabled={!selectedFace} title={!selectedFace ? "Select a face first to add a boundary condition" : "Add boundary condition"}>Add BC</button>
        </form>

        <div aria-live="polite">
            {#if $simulationConfig.boundary_conditions.length === 0}
                <p class="empty-state">No boundary conditions added yet. Select a face and configure parameters above to add one.</p>
            {:else}
                <ul>
                    {#each $simulationConfig.boundary_conditions as bc, i}
                        <li>
                            {bc.face_name}: {bc.bc_type} {bc.variable}={bc.value} ({bc.profile})
                            <button on:click={() => removeBC(i, bc.face_name)} aria-label="Remove boundary condition for {bc.face_name}" title="Remove boundary condition for {bc.face_name}">&times;</button>
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>
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
