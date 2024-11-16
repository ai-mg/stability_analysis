# Magnetic Field Stability Analysis

A Python package for analyzing the stability of solar magnetic fields, with a focus on detecting Polarity Inversion Lines (PILs) and calculating decay index and critical height for assessing potential solar eruptions.

## Overview

This package provides tools to:
- Detect and analyze Polarity Inversion Lines (PILs) in magnetogram data
- Calculate decay index and critical height for torus instability
- Analyze magnetic field stability around solar flares
- Visualize magnetic field configurations and stability metrics

## Installation

Install from source:

```bash
git clone https://github.com/ai-mg/stability-analysis
cd stability-analysis
pip install -e .
```

## Requirements

- Python >=3.8
- NumPy >=1.21.0
- SciPy >=1.7.0
- scikit-image >=0.18.0
- OpenCV >=4.5.0
- Astropy >=4.2
- Matplotlib >=3.4.0

## Quick Start

```python
from stability_analysis import StabilityAnalyzer
from stability_analysis.config import AnalysisConfig

# Initialize analyzer
config = AnalysisConfig.from_file('config.yaml')
analyzer = StabilityAnalyzer('data_path', config)

# Analyze time series
results = analyzer.analyze_time_series(date_time_dirs, flare_times)

# Visualize results
from stability_analysis.visualization import plot_results
plot_results(results)
```


## Scientific Background

This package implements methods for analyzing magnetic field stability in solar active regions, particularly focused on:

1. Detecting Polarity Inversion Lines (PILs) using the method of [Cai et al. (2020)](https://www.researchgate.net/profile/Berkay-Aydin/publication/350201132_A_Framework_for_Detecting_Polarity_Inversion_Lines_from_Longitudinal_Magnetograms/links/62f2aad64532247693906559/A-Framework-for-Detecting-Polarity-Inversion-Lines-from-Longitudinal-Magnetograms.pdf)
2. Calculating decay indices and critical heights for torus instability
3. Analyzing magnetic field configurations before solar flares


Publication: \
https://arxiv.org/pdf/2402.12254 \
https://ui.adsabs.harvard.edu/abs/2024A%26A...686A.115G/abstract

Note: Not all of the methods that were implemented in the paper are available in this package. Please contact the authors for further information.

For theoretical background, see:
- [Kliem & Török (2006)](https://arxiv.org/pdf/physics/0605217) - Torus instability theory
- [Gupta et al. (2024)](https://arxiv.org/pdf/2402.12254) - Stability analysis methodology

When using this software for scientific publications, please cite:

```bibtex
@ARTICLE{2024A&A...686A.115G,
       author = {{Gupta}, M. and {Thalmann}, J.~K. and {Veronig}, A.~M.},
        title = "{Stability of the coronal magnetic field around large confined and eruptive solar flares}",
      journal = {\aap},
     keywords = {methods: data analysis, methods: numerical, Sun: flares, Sun: magnetic fields, Astrophysics - Solar and Stellar Astrophysics},
         year = 2024,
        month = jun,
       volume = {686},
          eid = {A115},
        pages = {A115},
          doi = {10.1051/0004-6361/202346212},
archivePrefix = {arXiv},
       eprint = {2402.12254},
 primaryClass = {astro-ph.SR},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2024A&A...686A.115G},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
```
## License

This project is licensed under the GNU General Public License v3 (GPL-3.0) - see the LICENSE file for details.

This means that any project using this code must also be released under the GPL-3.0 license and make its source code available. This ensures that all derivative works remain free and open source.

The key terms of GPL-3.0 include:
- You can freely use, modify, and distribute this software
- Any modifications must also be licensed under GPL-3.0
- Source code must be made available when distributing the software
- Changes made to the code must be documented
