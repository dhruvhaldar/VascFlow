import xml.etree.ElementTree as ET
from xml.dom import minidom
from models import SimulationConfig

def generate_svfsi_xml(config: SimulationConfig) -> str:
    """Generates an svFSI input XML from the given configuration."""

    root = ET.Element("svFSIFile", version="0.1")

    # --- General Simulation Parameters ---
    gen_sim = ET.SubElement(root, "GeneralSimulationParameters")
    ET.SubElement(gen_sim, "NumberOfTimeSteps").text = str(config.general.num_time_steps)
    ET.SubElement(gen_sim, "TimeStepSize").text = str(config.general.time_step_size)
    ET.SubElement(gen_sim, "SaveResultsInFolder").text = "results"

    # --- Add Mesh ---
    mesh = ET.SubElement(root, "Add_mesh", name="msh")
    ET.SubElement(mesh, "MeshFilePath").text = config.mesh.mesh_path

    # --- Add Equation ---
    eqn = ET.SubElement(root, "Add_equation", type=config.physics.physics_type)
    ET.SubElement(eqn, "Coupled").text = "true"
    ET.SubElement(eqn, "Min_iterations").text = "3"
    ET.SubElement(eqn, "Max_iterations").text = "10"
    ET.SubElement(eqn, "Tolerance").text = "1e-3"

    # --- Material Model ---
    mat_model = ET.SubElement(eqn, "Constitutive_model", type=config.physics.material_model)
    # Add fluid properties if fluid
    if config.physics.physics_type == "Fluid":
        ET.SubElement(mat_model, "Density").text = str(config.physics.density)
        ET.SubElement(mat_model, "Viscosity").text = str(config.physics.viscosity)

    # --- Boundary Conditions ---
    for bc in config.boundary_conditions:
        bc_elem = ET.SubElement(eqn, "Add_BC", name=bc.face_name, profile=bc.profile)
        ET.SubElement(bc_elem, "Type").text = bc.bc_type
        # Add value based on type/variable - simplification for now
        ET.SubElement(bc_elem, "Value").text = str(bc.value)
        if bc.face_id is not None:
             # svFSI usually uses FaceID or FaceName depending on format.
             # Assuming FaceName matches the mesh face names for now.
             pass

    # Pretty print
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    return xml_str
