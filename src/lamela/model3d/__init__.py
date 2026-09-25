"""Eksport modelu 3D: IR → glTF 2.0 (.glb) i OBJ (+ .mtl). Patrz ``export.py``."""
from .export import export_glb, export_obj, ir_to_scene, load_glb_check  # noqa: F401
from .materials import PBR, pbr_for  # noqa: F401
