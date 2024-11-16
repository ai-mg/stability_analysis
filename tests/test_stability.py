"""
Tests for stability analysis package.
Place this in tests/test_stability.py
"""
import pytest
import numpy as np
from pathlib import Path
from stability_analysis.core.pil_detection import PILDetector
from stability_analysis.core.magnetic_field import MagneticField
from stability_analysis.core.decay_index import DecayIndexCalculator

# Test data paths - update these to match your input file locations
TEST_DATA_DIR = Path("test_data")
TEST_MAGNETOGRAM = TEST_DATA_DIR / "magnetogram.fits"
TEST_TIME_DIR = "20170906_0900"

@pytest.fixture
def test_magnetogram():
    """Load test magnetogram data."""
    from astropy.io import fits
    with fits.open(TEST_MAGNETOGRAM) as hdul:
        return hdul[0].data

@pytest.fixture
def magnetic_field():
    """Initialize MagneticField with test data."""
    return MagneticField(TEST_DATA_DIR)

class TestPILDetection:
    def test_polarity_identification(self, test_magnetogram):
        detector = PILDetector(test_magnetogram)
        detector.identify_polarity_regions()
        
        # Check that polarity maps are binary
        assert np.array_equal(detector.pos_map, detector.pos_map.astype(bool))
        assert np.array_equal(detector.neg_map, detector.neg_map.astype(bool))
        
        # Check that there are both positive and negative regions
        assert detector.pos_map.sum() > 0
        assert detector.neg_map.sum() > 0
        
    def test_pil_extraction(self, test_magnetogram):
        detector = PILDetector(test_magnetogram)
        detector.identify_polarity_regions()
        pil_map = detector.extract_pil()
        
        # Check PIL properties
        assert pil_map.dtype == bool
        assert pil_map.sum() > 0
        assert pil_map.sum() < (test_magnetogram.size / 4)  # PIL should be thin

class TestMagneticField:
    def test_load_boundary_field(self, magnetic_field):
        bx, by, bz = magnetic_field.load_boundary_field(TEST_TIME_DIR)
        
        # Check field components
        assert bx.shape == by.shape == bz.shape
        assert not np.all(np.isnan(bx))
        assert not np.all(np.isnan(by))
        assert not np.all(np.isnan(bz))
        
    def test_load_3d_field(self, magnetic_field):
        field_3d = magnetic_field.load_3d_field(TEST_TIME_DIR)
        
        required_keys = ['bx', 'by', 'bz', 'bh']
        assert all(key in field_3d for key in required_keys)
        
        # Check field dimensions
        shape = field_3d['bx'].shape
        assert len(shape) == 3
        assert all(s > 0 for s in shape)

class TestDecayIndex:
    @pytest.fixture
    def calculator(self, magnetic_field):
        field_3d = magnetic_field.load_3d_field(TEST_TIME_DIR)
        return DecayIndexCalculator(field_3d, grid_spacing=0.72)
    
    def test_decay_index_calculation(self, calculator):
        # Test at center point
        nx, ny = calculator.field['bx'].shape[:2]
        x, y = nx//2, ny//2
        
        decay_index = calculator.calculate_decay_index(x, y)
        
        assert len(decay_index) > 0
        assert not np.all(np.isnan(decay_index))
        
    def test_critical_height_finding(self, calculator):
        nx, ny = calculator.field['bx'].shape[:2]
        x, y = nx//2, ny//2
        
        result = calculator.find_critical_height(x, y)
        
        assert hasattr(result, 'critical_height')
        assert hasattr(result, 'critical_height_range')
        assert result.critical_height >= 0

if __name__ == "__main__":
    pytest.main([__file__])