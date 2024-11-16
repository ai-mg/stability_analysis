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

"""Configuration settings for stability analysis."""
from dataclasses import dataclass
from datetime import timedelta
import yaml
from typing import Optional

@dataclass
class PILDetectionConfig:
    """Configuration for PIL detection."""
    pos_threshold: float = 100  # Gauss
    neg_threshold: float = -100 # Gauss
    gaussian_sigma: float = 3
    dilation_size: int = 6

@dataclass
class AnalysisConfig:
    """Main configuration class."""
    grid_spacing: float = 0.72  # Mm
    critical_decay_index: float = 1.5
    height_uncertainty: float = 0.1
    preflare_window: timedelta = timedelta(hours=5)
    pil_detection: PILDetectionConfig = PILDetectionConfig()
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AnalysisConfig':
        """Load configuration from YAML file."""
        with open(config_path) as f:
            config_dict = yaml.safe_load(f)
            
        pil_config = PILDetectionConfig(
            **config_dict.get('pil_detection', {})
        )
        
        return cls(
            grid_spacing=config_dict.get('grid_spacing', 0.72),
            critical_decay_index=config_dict.get('critical_decay_index', 1.5),
            height_uncertainty=config_dict.get('height_uncertainty', 0.1),
            preflare_window=timedelta(
                hours=config_dict.get('preflare_window_hours', 5)
            ),
            pil_detection=pil_config
        )