"""
This file is part of stability_analysis.

stability_analysis is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stability_analysis is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with stability_analysis. If not, see <https://www.gnu.org/licenses/>.

Copyright 2024 M. Gupta, J. K. Thalmann, A. M. Veronig
"""

"""
Decay index calculation module.
"""
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class DecayIndexResult:
    """Container for decay index calculation results."""
    decay_index: np.ndarray
    critical_height: float
    critical_height_range: Tuple[float, float]

class DecayIndexCalculator:
    """Handles calculation of decay index and related quantities."""
    
    def __init__(self, magnetic_field_3d: dict, grid_spacing: float):
        """
        Initialize calculator with 3D magnetic field data.
        
        Args:
            magnetic_field_3d: Dict containing bx, by, bz, bh components
            grid_spacing: Grid spacing in Mm
        """
        self.field = magnetic_field_3d
        self.dx = grid_spacing
        self._setup_interpolators()
        
    def _setup_interpolators(self):
        """Setup interpolation functions for field components."""
        nx, ny, nz = self.field['bx'].shape
        x = np.arange(nx)
        y = np.arange(ny)
        z = np.arange(nz)
        
        self.bh_interpolator = RegularGridInterpolator(
            (x, y, z),
            self.field['bh']
        )
        
    def calculate_decay_index(self, x: float, y: float, 
                            z_range: Optional[Tuple[float, float]] = None,
                            n_points: int = 100) -> np.ndarray:
        """
        Calculate decay index along vertical line.
        
        Args:
            x, y: Horizontal coordinates
            z_range: Optional vertical range to evaluate
            n_points: Number of points for calculation
            
        Returns:
            Array of decay index values
        """
        if z_range is None:
            z_range = (0, self.field['bh'].shape[2]-1)
            
        z = np.linspace(z_range[0], z_range[1], n_points)
        
        # Evaluate horizontal field along vertical line
        points = np.column_stack([
            np.full_like(z, x),
            np.full_like(z, y),
            z
        ])
        bh = self.bh_interpolator(points)
        
        # Calculate decay index
        d_ln_bh = np.gradient(np.log(bh), z)
        decay_index = -z * d_ln_bh
        
        return decay_index
        
    def find_critical_height(self, x: float, y: float,
                           critical_index: float = 1.5,
                           uncertainty: float = 0.1) -> DecayIndexResult:
        """
        Find height where decay index reaches critical value.
        
        Args:
            x, y: Horizontal coordinates
            critical_index: Critical decay index value
            uncertainty: Uncertainty range for critical height
            
        Returns:
            DecayIndexResult containing critical height and range
        """
        decay_index = self.calculate_decay_index(x, y)
        z = np.arange(len(decay_index)) * self.dx
        
        # Find where decay index crosses critical value
        cross_points = np.where(
            (decay_index >= critical_index-uncertainty) & 
            (decay_index <= critical_index+uncertainty)
        )[0]
        
        if len(cross_points) == 0:
            return DecayIndexResult(
                decay_index=decay_index,
                critical_height=float('inf'),
                critical_height_range=(float('inf'), float('inf'))
            )
            
        critical_height = z[cross_points[0]]
        height_range = (
            z[cross_points[0]] - uncertainty * self.dx,
            z[cross_points[-1]] + uncertainty * self.dx
        )
        
        return DecayIndexResult(
            decay_index=decay_index,
            critical_height=critical_height,
            critical_height_range=height_range
        )