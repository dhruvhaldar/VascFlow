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

    <div class="add-bc">
        <select bind:value={selectedFace}>
            <option value="" disabled selected>Select Face</option>
            {#each $meshMetadata.faces as face}
                <option value={face.name}>{face.name} (ID: {face.id})</option>
            {/each}
        </select>

        <select bind:value={bcType}>
            <option value="Dirichlet">Dirichlet</option>
            <option value="Neumann">Neumann</option>
            <option value="Resistance">Resistance</option>
        </select>

        <input type="text" bind:value={variable} placeholder="Variable (e.g. Velocity)" />
        <input type="number" bind:value={value} step="0.1" />

        <select bind:value={profile}>
            <option value="Flat">Flat</option>
            <option value="Parabolic">Parabolic</option>
        </select>

        <button on:click={addBC} disabled={!selectedFace}>Add BC</button>
    </div>

    <ul>
        {#each $simulationConfig.boundary_conditions as bc, i}
            <li>
                {bc.face_name}: {bc.bc_type} {bc.variable}={bc.value} ({bc.profile})
                <button on:click={() => removeBC(i)}>x</button>
            </li>
        {/each}
    </ul>
</div>

<style>
    .bc-editor {
        border: 1px solid #ccc;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .add-bc {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
</style>
