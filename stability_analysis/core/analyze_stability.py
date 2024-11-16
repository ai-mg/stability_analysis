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
Main script for magnetic field stability analysis.
"""
from pathlib import Path
import numpy as np
from datetime import datetime
import logging
from typing import List, Dict, Optional

from stability_analysis.core.pil_detection import PILDetector
from stability_analysis.core.magnetic_field import MagneticField
from stability_analysis.core.decay_index import DecayIndexCalculator
from stability_analysis.core.visualization import plot_results
from stability_analysis.config import AnalysisConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StabilityAnalyzer:
    """Main class for magnetic field stability analysis."""
    
    def __init__(self, data_path: str, config: Optional[AnalysisConfig] = None):
        """
        Initialize stability analyzer.
        
        Args:
            data_path: Path to magnetic field data
            config: Analysis configuration parameters
        """
        self.data_path = Path(data_path)
        self.config = config or AnalysisConfig()
        self.magnetic_field = MagneticField(data_path)
        
    def analyze_time_series(self, 
                          date_time_dirs: List[str],
                          flare_times: List[datetime]) -> Dict:
        """
        Analyze stability for a time series of magnetic field data.
        
        Args:
            date_time_dirs: List of data directories for each time
            flare_times: List of flare occurrence times
            
        Returns:
            Dictionary containing analysis results
        """
        results = []
        
        for date_time_dir in date_time_dirs:
            logger.info(f"Processing {date_time_dir}")
            
            try:
                result = self.analyze_single_time(date_time_dir)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {date_time_dir}: {str(e)}")
                continue
                
        return self.compile_results(results, flare_times)
        
    def analyze_single_time(self, date_time_dir: str) -> Dict:
        """Analyze stability for a single time."""
        # Load magnetic field data
        bx, by, bz = self.magnetic_field.load_boundary_field(date_time_dir)
        field_3d = self.magnetic_field.load_3d_field(date_time_dir)
        
        # Detect PIL
        pil_detector = PILDetector(bz)
        pil_detector.identify_polarity_regions(
            pos_thresh=self.config.pil_detection.pos_threshold,
            neg_thresh=self.config.pil_detection.neg_threshold
        )
        pil_map = pil_detector.extract_pil()
        
        # Calculate decay index
        calculator = DecayIndexCalculator(field_3d, self.config.grid_spacing)
        
        decay_indices = []
        critical_heights = []
        
        # Calculate along PIL points
        pil_points = np.where(pil_map)
        for x, y in zip(*pil_points):
            decay_result = calculator.find_critical_height(
                x, y,
                critical_index=self.config.critical_decay_index,
                uncertainty=self.config.height_uncertainty
            )
            decay_indices.append(decay_result.decay_index)
            critical_heights.append(decay_result.critical_height)
            
        return {
            'time': self._parse_time(date_time_dir),
            'pil_map': pil_map,
            'decay_indices': decay_indices,
            'critical_heights': critical_heights,
            'field_3d': field_3d
        }
        
    def compile_results(self, results: List[Dict], 
                       flare_times: List[datetime]) -> Dict:
        """Compile and analyze time series results."""
        times = [r['time'] for r in results]
        critical_heights = [r['critical_heights'] for r in results]
        
        # Find pre-flare periods
        preflare_indices = []
        for flare_time in flare_times:
            mask = [(t < flare_time) and 
                   (t > flare_time - self.config.preflare_window)
                   for t in times]
            preflare_indices.extend([i for i, m in enumerate(mask) if m])
            
        # Calculate statistics
        preflare_heights = [critical_heights[i] for i in preflare_indices]
        mean_height = np.mean(preflare_heights)
        std_height = np.std(preflare_heights)
        
        return {
            'times': times,
            'critical_heights': critical_heights,
            'preflare_mean_height': mean_height,
            'preflare_std_height': std_height,
            'individual_results': results
        }
        
    def _parse_time(self, date_time_dir: str) -> datetime:
        """Parse datetime from directory name."""
        try:
            return datetime.strptime(date_time_dir, '%Y%m%d_%H%M')
        except ValueError:
            logger.warning(f"Could not parse time from {date_time_dir}")
            return None
            
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze magnetic field stability'
    )
    parser.add_argument('data_path', help='Path to magnetic field data')
    parser.add_argument('--config', help='Path to configuration file')
    args = parser.parse_args()
    
    config = AnalysisConfig.from_file(args.config) if args.config else None
    analyzer = StabilityAnalyzer(args.data_path, config)
    
    # Example usage
    date_time_dirs = [
        '20170906_0900',
        '20170906_0930',
        '20170906_1000'
    ]
    flare_times = [
        datetime(2017, 9, 6, 9, 10),
        datetime(2017, 9, 6, 12, 2)
    ]
    
    results = analyzer.analyze_time_series(date_time_dirs, flare_times)
    plot_results(results)