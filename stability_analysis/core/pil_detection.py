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
Polarity Inversion Line (PIL) detection module.
"""
import numpy as np
from scipy import ndimage
from skimage import feature
from skimage.morphology import square, dilation, thin
import cv2

class PILDetector:
    """Handles detection of Polarity Inversion Lines in magnetogram data."""
    
    def __init__(self, magnetogram_data):
        self.data = magnetogram_data
        self.pos_map = None
        self.neg_map = None
        self.pil_map = None
        
    def identify_polarity_regions(self, pos_thresh=100, neg_thresh=-100, 
                                apply_gaussian=False, sigma=3):
        """
        Identify positive and negative polarity regions in magnetogram.
        
        Args:
            pos_thresh: Threshold for positive polarity (Gauss)
            neg_thresh: Threshold for negative polarity (Gauss) 
            apply_gaussian: Whether to apply Gaussian smoothing
            sigma: Gaussian smoothing parameter
        """
        data = self.data
        if apply_gaussian:
            data = ndimage.gaussian_filter(data, sigma=sigma, truncate=3)
            
        pos_map = np.zeros(data.shape)
        neg_map = np.zeros(data.shape)
        
        pos_indices = np.where(data >= pos_thresh)
        neg_indices = np.where(data <= neg_thresh)
        
        pos_map[pos_indices] = 1
        neg_map[neg_indices] = 1
        
        self.pos_map = pos_map
        self.neg_map = neg_map
        
    def detect_edges(self, sigma=1):
        """Detect edges in polarity maps using Canny edge detector."""
        pos_edges = feature.canny(self.pos_map, sigma=sigma)
        neg_edges = feature.canny(self.neg_map, sigma=sigma)
        return pos_edges, neg_edges
        
    def dilate_edges(self, edges, size=6):
        """Dilate detected edges."""
        struct_elem = square(size)
        return dilation(edges, struct_elem)
        
    def extract_pil(self, thinning=True):
        """
        Extract PIL from intersection of dilated edges.
        
        Args:
            thinning: Whether to apply thinning to get 1-pixel wide PIL
        """
        pos_edges, neg_edges = self.detect_edges()
        dil_pos = self.dilate_edges(pos_edges)
        dil_neg = self.dilate_edges(neg_edges)
        
        # Find intersection
        pil_mask = ~np.isnan(self.data)
        pil_indices = np.where(dil_pos & dil_neg & pil_mask)
        
        pil_map = np.zeros(self.data.shape)
        pil_map[pil_indices] = 1
        
        if thinning:
            pil_map = thin(pil_map)
            
        self.pil_map = pil_map
        return pil_map

    def find_flare_pil(self, ribbon_map):
        """
        Extract flare-relevant PIL using ribbon map overlap.
        
        Args:
            ribbon_map: Binary map of flare ribbons
        Returns:
            Binary map of flare-relevant PIL
        """
        if self.pil_map is None:
            self.extract_pil()
            
        contours, _ = cv2.findContours(
            self.pil_map.astype(np.uint8), 
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_NONE
        )
        
        def count_ribbon_overlap(contour):
            """Count pixels overlapping with ribbon."""
            mask = np.zeros_like(self.pil_map)
            mask[contour[:,0,1], contour[:,0,0]] = 1
            return np.sum(mask * ribbon_map)
            
        if not contours:
            return np.zeros_like(self.pil_map)
            
        # Find contour with maximum ribbon overlap
        fpil_contour = max(contours, key=count_ribbon_overlap)
        
        fpil_map = np.zeros_like(self.pil_map)
        fpil_map[fpil_contour[:,0,1], fpil_contour[:,0,0]] = 1
        
        return thin(fpil_map)