# stability_analysis/__init__.py
"""
Stability Analysis Package for Solar Magnetic Fields.

This package provides tools for analyzing magnetic field stability,
including PIL detection and decay index calculation.
"""

__version__ = '0.1.0'
__author__ = 'Manu Gupta'

# Import main classes
from .core.pil_detection import PILDetector
from .core.magnetic_field import MagneticField
from .core.decay_index import DecayIndexCalculator
from .core.visualization import StabilityVisualizer

# Define package exports
__all__ = [
    'PILDetector',
    'MagneticField',
    'DecayIndexCalculator',
    'StabilityVisualizer'
]

# Package-level configuration
default_config = {
    'grid_spacing': 0.72,
    'critical_index': 1.5,
    'height_uncertainty': 0.1
}