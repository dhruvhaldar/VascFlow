from models import SimulationConfig, GeneralConfig, MeshConfig, PhysicsConfig, BoundaryCondition
from xml_generator import generate_svfsi_xml
import xml.etree.ElementTree as ET

def test_xml_generation():
    config = SimulationConfig(
        general=GeneralConfig(num_time_steps=100, time_step_size=0.01),
        mesh=MeshConfig(mesh_path="test.vtu", domain_type="Fluid"),
        physics=PhysicsConfig(physics_type="Fluid", density=1.0, viscosity=0.04),
        boundary_conditions=[
            BoundaryCondition(face_name="Inflow", bc_type="Dirichlet", variable="Velocity", value=10.0, profile="Parabolic")
        ]
    )

    xml_str = generate_svfsi_xml(config)

    # Check basic structure
    root = ET.fromstring(xml_str)
    assert root.tag == "svFSIFile"

    gen_sim = root.find("GeneralSimulationParameters")
    assert gen_sim is not None
    assert gen_sim.find("NumberOfTimeSteps").text == "100"

    mesh = root.find("Add_mesh")
    assert mesh.attrib["name"] == "msh"
    assert mesh.find("MeshFilePath").text == "test.vtu"

    eqn = root.find("Add_equation")
    assert eqn.attrib["type"] == "Fluid"

    bc = eqn.find("Add_BC")
    assert bc.attrib["name"] == "Inflow"
    assert bc.find("Type").text == "Dirichlet"
    assert bc.find("Value").text == "10.0"
