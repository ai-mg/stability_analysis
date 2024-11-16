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
Magnetic field data loading and processing module.
"""
import numpy as np
import os
from typing import Tuple, Dict
from dataclasses import dataclass

@dataclass
class GridConfig:
    """Configuration for magnetic field grid."""
    nx: int
    ny: int 
    nz: int
    dx: float = 7.2e7  # cm

class MagneticField:
    """Handles loading and processing of magnetic field data."""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.config = None
        self.bx = None
        self.by = None
        self.bz = None
        
    def load_boundary_field(self, date_time_dir: str, resolution: str = 'bin2') -> Tuple[np.ndarray, ...]:
        """
        Load boundary magnetic field data (i.e., before preprocessing & NLFF processing)
        
        Args:
            date_time_dir: Directory containing time-specific data
            resolution: Data resolution ('orig', 'bin2', 'bin4')
            
        Returns:
            Tuple of (bx, by, bz) arrays at boundary
        """
        # Set resolution directory
        res_dir = '' if resolution == 'orig' else f"{resolution}/"
        dir_path = os.path.join(self.data_path, date_time_dir, res_dir)
        
        # Read grid configuration
        self.config = self._read_grid_config(dir_path)
        
        # Load boundary data
        boundary_data = np.loadtxt(os.path.join(dir_path, 'allboundaries_orig.dat'))
        
        nx, ny = self.config.nx, self.config.ny
        nxny = nx * ny
        
        # Reshape into component arrays
        bx = boundary_data[0:3*nxny:3].reshape(nx, ny)
        by = boundary_data[1:3*nxny:3].reshape(nx, ny)
        bz = boundary_data[2:3*nxny:3].reshape(nx, ny)
        
        self.bx = bx
        self.by = by 
        self.bz = bz
        
        return bx, by, bz
        
    def load_3d_field(self, date_time_dir: str, resolution: str = 'bin2', 
                     weight_param: int = 1) -> Dict[str, np.ndarray]:
        """
        Load 3D magnetic field data.
        
        Args:
            date_time_dir: Directory containing time-specific data
            resolution: Data resolution
            weight_param: Weight parameter for field calculation
            
        Returns:
            Dictionary containing field components and derived quantities
        """
        res_dir = '' if resolution == 'orig' else f"{resolution}/"
        element_dir = os.path.join(
            self.data_path, 
            date_time_dir, 
            res_dir,
            f'mu3_1e-3_mu4_1e-2_wa_1e0_wb_{weight_param}e0_nue_1e-3_msk_2'
        )
        
        # Load 3D field data
        field_data = np.fromfile(os.path.join(element_dir, 'Bout_orig.bin'))
        
        nx, ny, nz = self.config.nx, self.config.ny, self.config.nz
        nxnynz = nx * ny * nz
        
        # Split into components and reshape
        bx_3d = field_data[0:nxnynz].reshape((nx, ny, nz))
        by_3d = field_data[nxnynz:2*nxnynz].reshape((nx, ny, nz))
        bz_3d = field_data[2*nxnynz:3*nxnynz].reshape((nx, ny, nz))
        
        # Calculate horizontal field strength
        bh = np.sqrt(bx_3d**2 + by_3d**2)
        
        return {
            'bx': bx_3d,
            'by': by_3d,
            'bz': bz_3d,
            'bh': bh
        }
        
    def _read_grid_config(self, dir_path: str) -> GridConfig:
        """Read grid configuration from file."""
        with open(os.path.join(dir_path, 'grid_orig.ini'), 'r') as f:
            params = f.readlines()
        
        return GridConfig(
            nx=int(params[1]),
            ny=int(params[3]),
            nz=int(params[5])
        )