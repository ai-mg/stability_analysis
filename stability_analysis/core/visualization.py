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
Visualization module for magnetic field stability analysis.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates
from typing import Dict, Optional, Tuple

class StabilityVisualizer:
    """Class for visualizing magnetic field stability analysis results."""
    
    def __init__(self):
        """Initialize custom colormaps and plot settings."""
        self.cmap_j = LinearSegmentedColormap.from_list("", 
            ["white", "slateblue", "blue", "green", "yellow", "red"])
        self.cmap_decay = LinearSegmentedColormap.from_list("",
            ["blue", "white", "cyan", "green", "yellow", "red", "purple"])
        plt.rcParams.update({'font.size': 22})

    def plot_pil_detection(self, magnetogram: np.ndarray, 
                         pil_map: np.ndarray,
                         ribbon_map: Optional[np.ndarray] = None,
                         title: str = '',
                         save_path: Optional[str] = None) -> None:
        """
        Plot PIL detection results.
        
        Args:
            magnetogram: Vertical magnetic field component
            pil_map: Binary map of detected PIL
            ribbon_map: Optional binary map of flare ribbons
            title: Plot title
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        
        # Plot magnetogram background
        ax.imshow(magnetogram, cmap='gray')
        
        # Plot PIL
        pil_contour = ax.contour(pil_map, colors='yellow', linewidths=0.5)
        
        if ribbon_map is not None:
            # Create custom colormap for ribbons
            cmap_cf = LinearSegmentedColormap.from_list("", ["white", "red"])
            ribbon_map2 = np.ma.masked_where(ribbon_map < 1, ribbon_map)
            ax.contourf(ribbon_map2, cmap=cmap_cf, alpha=0.8)
            
        ax.set_title(title)
        ax.invert_yaxis()
        ax.set_xlabel('X (Mm)')
        ax.set_ylabel('Y (Mm)')
        
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            
    def plot_decay_index(self, decay_index: np.ndarray,
                        critical_height: float,
                        height_range: Tuple[float, float],
                        current_height: Optional[float] = None,
                        title: str = '',
                        save_path: Optional[str] = None) -> None:
        """
        Plot decay index map with critical height.
        
        Args:
            decay_index: 2D array of decay index values
            critical_height: Critical height for torus instability
            height_range: Uncertainty range for critical height
            current_height: Optional current height of structure
            title: Plot title
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        
        # Plot decay index map
        im = ax.imshow(decay_index.T, cmap=self.cmap_decay, 
                      origin='lower', vmin=-1, vmax=2.5)
        plt.colorbar(im, ax=ax, label='Decay Index')
        
        # Plot critical height
        ax.axhline(y=critical_height, color='gray', linestyle=':', linewidth=2)
        ax.axhspan(height_range[0], height_range[1], 
                  color='lightgray', alpha=0.3)
        
        if current_height is not None:
            ax.axhline(y=current_height, color='black', 
                      linestyle='--', linewidth=2)
            
        ax.set_title(title)
        ax.set_xlabel('Position along PIL (Mm)')
        ax.set_ylabel('Height (Mm)')
        
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            
    def plot_time_series(self, results: Dict,
                        save_path: Optional[str] = None) -> None:
        """
        Plot time evolution of critical heights.
        
        Args:
            results: Dictionary containing analysis results
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        
        times = results['times']
        heights = results['critical_heights']
        
        # Plot critical heights
        ax.errorbar(times, heights, yerr=results['preflare_std_height'],
                   fmt='o-', color='blue', label='Critical Height')
                   
        # Shade flare times if available
        if 'flare_times' in results:
            for flare_time in results['flare_times']:
                ax.axvspan(flare_time - np.timedelta64(5, 'm'),
                          flare_time + np.timedelta64(5, 'm'),
                          color='lightpink', alpha=0.3)
                
        ax.set_xlabel('Time (UT)')
        ax.set_ylabel('Height (Mm)')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.grid(True, linestyle='--', alpha=0.5)
        
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            
    def plot_current_map(self, current: np.ndarray,
                        field_lines: Optional[Tuple[np.ndarray, np.ndarray]] = None,
                        center_height: Optional[float] = None,
                        title: str = '',
                        save_path: Optional[str] = None) -> None:
        """
        Plot current density map with optional field lines.
        
        Args:
            current: Current density array
            field_lines: Optional tuple of (Bx, Bz) for field lines
            center_height: Optional height of current center
            title: Plot title
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        
        # Plot current density
        im = ax.imshow(current.T, cmap=self.cmap_j, origin='lower')
        plt.colorbar(im, ax=ax, label=r'$|\mathbf{J}|$ [$\times 10^{-4}$ A m$^{-2}$]')
        
        if field_lines is not None:
            Bx, Bz = field_lines
            # Create streamplot of magnetic field
            x = np.arange(0, Bx.shape[0])
            z = np.arange(0, Bx.shape[1])
            X, Z = np.meshgrid(x, z)
            ax.streamplot(X, Z, Bx.T, Bz.T, color='k', density=2)
            
        if center_height is not None:
            ax.axhline(y=center_height, color='white', 
                      linestyle='--', linewidth=2)
            
        ax.set_title(title)
        ax.set_xlabel('X (Mm)')
        ax.set_ylabel('Height (Mm)')
        
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')

def plot_results(results: Dict) -> None:
    """
    Convenience function to plot analysis results.
    
    Args:
        results: Dictionary containing analysis results
    """
    visualizer = StabilityVisualizer()
    visualizer.plot_time_series(results)
    plt.show()