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

    // ⚡ Bolt: Remove by unique ID instead of array index.
    // By passing faceName instead of the array index, we remove the
    // index dependency from the rendered DOM elements.
    function removeBC(faceName) {
        if (window.confirm(`Are you sure you want to remove the boundary condition for ${faceName}?`)) {
            simulationConfig.update(c => {
                c.boundary_conditions = c.boundary_conditions.filter(bc => bc.face_name !== faceName);
                return c;
            });
        }
    }
</script>

<div class="bc-editor">
    <h3>Boundary Conditions</h3>

    {#if $meshMetadata.faces.length > 0}
        <form class="add-bc" on:submit|preventDefault={addBC}>
            <label>
                <span>Face<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <select bind:value={selectedFace} aria-label="Select Face" title="Select Face" required>
                    <option value="" disabled selected>Select Face</option>
                    <!-- ⚡ Bolt: Use a keyed each block for face options. -->
                    {#each $meshMetadata.faces as face (face.id)}
                        <option
                            value={face.name}
                            disabled={usedFaceNames.has(face.name)}
                        >
                            {face.name} (ID: {face.id}) {usedFaceNames.has(face.name) ? '(Already Added)' : ''}
                        </option>
                    {/each}
                </select>
            </label>

            <label>
                <span>Type<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <select bind:value={bcType} aria-label="Boundary Condition Type" title="Boundary Condition Type" required>
                    <option value="Dirichlet">Dirichlet</option>
                    <option value="Neumann">Neumann</option>
                    <option value="Resistance">Resistance</option>
                </select>
            </label>

            <label>
                <span>Variable<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <input type="text" bind:value={variable} aria-label="Variable Name" title="Variable Name" placeholder="Variable (e.g. Velocity)" required />
            </label>

            <label>
                <span>Value<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <input type="number" bind:value={value} aria-label="Value" title="Value" step="0.1" required />
            </label>

            <label>
                <span>Profile<span class="required-indicator" aria-hidden="true" title="Required">*</span></span>
                <select bind:value={profile} aria-label="Profile" title="Profile" required>
                    <option value="Flat">Flat</option>
                    <option value="Parabolic">Parabolic</option>
                </select>
            </label>

            <div class="submit-action">
                <button type="submit" disabled={!selectedFace} title={!selectedFace ? "Select a face first to add a boundary condition" : "Add boundary condition"}>Add BC</button>
            </div>
        </form>

        <div aria-live="polite">
            {#if $simulationConfig.boundary_conditions.length === 0}
                <p class="empty-state">No boundary conditions added yet. Select a face and configure parameters above to add one.</p>
            {:else}
                <ul>
                    <!-- ⚡ Bolt: Use a keyed each block based on face_name.
                         Combined with removing the index dependency in removeBC,
                         this guarantees O(1) DOM updates when removing an item,
                         rather than triggering an O(N) cascade update to re-bind
                         shifted array indices for all subsequent sibling elements. -->
                    {#each $simulationConfig.boundary_conditions as bc (bc.face_name)}
                        <li class="bc-item">
                            <span>{bc.face_name}: {bc.bc_type} {bc.variable}={bc.value} ({bc.profile})</span>
                            <button class="remove-btn" on:click={() => removeBC(bc.face_name)} aria-label="Remove boundary condition for {bc.face_name}" title="Remove boundary condition for {bc.face_name}">&times;</button>
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
        align-items: flex-end;
    }

    .add-bc label {
        display: flex;
        flex-direction: column;
        font-size: 0.85rem;
        color: #b8c5ef;
        gap: 0.25rem;
    }

    .add-bc input, .add-bc select {
        padding: 0.45rem 0.55rem;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 10px;
        background: rgba(12, 18, 40, 0.45);
        color: #f3f6ff;
    }

    .submit-action {
        display: flex;
        align-items: flex-end;
        padding-bottom: 0.1rem;
    }

    .required-indicator {
        color: #ffc2c2;
        margin-left: 0.2rem;
    }

    .empty-state {
        color: #b8c5ef;
        font-style: italic;
        margin-top: 1rem;
    }

    ul {
        padding-left: 1rem;
    }

    .bc-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.25rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .bc-item:last-child {
        border-bottom: none;
    }

    .remove-btn {
        background: transparent;
        border: 1px solid transparent;
        color: #ffc2c2;
        cursor: pointer;
        font-size: 1.2rem;
        line-height: 1;
        padding: 0.1rem 0.4rem;
        border-radius: 6px;
        transition: all 0.2s ease;
    }

    .remove-btn:hover {
        background: rgba(255, 77, 77, 0.15);
        color: #ff4d4d;
        border-color: rgba(255, 77, 77, 0.3);
    }

    .remove-btn:focus-visible {
        outline: 2px solid #ff4d4d;
        outline-offset: 2px;
    }
</style>
