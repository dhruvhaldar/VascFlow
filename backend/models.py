from pydantic import BaseModel, Field
from typing import List, Optional, Union

class GeneralConfig(BaseModel):
    num_time_steps: int = Field(100, description="Number of time steps")
    time_step_size: float = Field(0.001, description="Time step size")
    save_results_frequency: int = Field(10, description="Frequency to save results")
    start_time_step: int = Field(0, description="Start time step (for restart)")

class MeshConfig(BaseModel):
    mesh_path: str = Field(..., max_length=1024, description="Path to the mesh file (.vtu/.vtp)")
    domain_type: str = Field("Fluid", max_length=100, description="Domain type: Fluid, Solid, etc.")

class BoundaryCondition(BaseModel):
    face_name: str = Field(..., max_length=255)
    bc_type: str = Field("Dirichlet", max_length=100, description="Type: Dirichlet, Neumann, Resistance, etc.")
    variable: str = Field("Velocity", max_length=100, description="Variable: Velocity, Pressure, Displacement")
    value: float = Field(0.0, description="Value for constant BC")
    profile: Optional[str] = Field("Flat", max_length=100, description="Profile: Flat, Parabolic, User_Defined")
    face_id: Optional[int] = None # Filled from mesh metadata

class MaterialProperty(BaseModel):
    name: str = Field(..., max_length=255)
    value: float

class PhysicsConfig(BaseModel):
    physics_type: str = Field("Fluid", max_length=100, description="Physics type: Fluid, Structure, FSI")
    density: float = 1.06
    viscosity: float = 0.04
    material_model: str = Field("Newtonian", max_length=100, description="Material model")
    properties: List[MaterialProperty] = Field([], max_length=1000, description="List of material properties")

class SimulationConfig(BaseModel):
    general: GeneralConfig
    mesh: MeshConfig
    physics: PhysicsConfig
    boundary_conditions: List[BoundaryCondition] = Field(..., max_length=1000, description="List of boundary conditions")
