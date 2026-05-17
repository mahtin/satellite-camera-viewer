"""
BrownConradyCoeffs.py

Brown-Conrady distortion coefficients model
"""

from dataclasses import dataclass
import numpy as np

@dataclass
class BrownConradyCoeffs:
    """
    Stores Brown-Conrady lens distortion coefficients.
    Ref: https://docs.nvidia.com/vpi/2.0/algo_ldc.html
    """
    # Lens distortion parameters k1, k2, k3 (radial) and p1, p2 (tangential) are Brown-Conrady coefficients
    # used in computer vision to model and correct imperfections, such as barrel or pincushion effects.
    # They map distorted pixel locations to ideal rectilinear coordinates, crucial for applications like
    # robotic vision, AR, and 3D reconstruction.

    k1: float = 0.0
    k2: float = 0.0
    p1: float = 0.0
    p2: float = 0.0
    k3: float = 0.0

    # Optional higher-order radial coefficients for advanced models
    k4: float = 0.0
    k5: float = 0.0
    k6: float = 0.0

    # Center of distortion (usually pixel coordinates)
    cx: float = 0.0
    cy: float = 0.0

    def to_array(self):
        """Returns coefficients as an OpenCV-compatible array [k1, k2, p1, p2, k3]."""
        return np.array([self.k1, self.k2, self.p1, self.p2, self.k3])
