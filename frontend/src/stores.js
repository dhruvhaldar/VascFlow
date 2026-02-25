import { writable } from 'svelte/store';

export const simulationConfig = writable({
    general: {
        num_time_steps: 100,
        time_step_size: 0.001,
        save_results_frequency: 10,
        start_time_step: 0
    },
    mesh: {
        mesh_path: "",
        domain_type: "Fluid"
    },
    physics: {
        physics_type: "Fluid",
        density: 1.06,
        viscosity: 0.04,
        material_model: "Newtonian",
        properties: []
    },
    boundary_conditions: []
});

export const meshMetadata = writable({
    n_points: 0,
    n_cells: 0,
    faces: [], // {id, name, count}
    bounds: [],
    viz_file: ""
});

export const generatedXML = writable("");
