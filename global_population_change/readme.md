# Global Population Change (2010–2020)

A geospatial workflow to classify and visualize global population change using raster analysis and cartographic styling in Python.

:[Final Output]<img width="4404" height="2535" alt="population_change_equal_earth (2)" src="https://github.com/user-attachments/assets/0704ec2b-b588-43bf-87f4-54f8af005721" />


## Overview

This project takes **Gridded Population of the World (GPW) v4** rasters for 2010 and 2020, computes the per-pixel difference, reclassifies the change into four categories, and produces a publication-ready thematic map in **Equal Earth projection**.

### Change Classes

| Class | Range | Color |
|-------|-------|-------|
| Decline | ≤ −100 | 🔵 Blue |
| Neutral | −100 to 100 | ⚪ Gray |
| Growth | 100 to 1,000 | 🟠 Orange |
| High Growth | > 1,000 | 🔴 Red |

## Outputs

| File | Description |
|------|-------------|
| `output/change_class.tif` | Classified raster (EPSG:4326) |
| `output/change_class_equal_earth.tif` | Classified raster (Equal Earth, ESRI:54035) |
| `output/population_change_equal_earth.png` | Final map (300 DPI PNG) |

## Quick Start

### Google Colab (recommended)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/130KXKFtH4VrtAyzrhHB4EBiDDV--gqx3?usp=sharing)

### Local Setu

```bash
git clone https://github.com/somdeepkundu/global-population-change.git
cd global-population-change
pip install -r requirements.txt
jupyter notebook global_population_change.ipynb
```

## Requirements

```
numpy
matplotlib
rioxarray
xarray-spatial
cartopy
geopandas
```

## Project Structure

```
global-population-change/
├── global_population_change.ipynb   # Main notebook
├── requirements.txt                 # Python dependencies
├── README.md
├── LICENSE
├── data/                            # Downloaded rasters (gitignored)
├── india_shp/                       # SOI boundary (gitignored)
└── output/                          # Generated outputs
    ├── change_class.tif
    ├── change_class_equal_earth.tif
    └── population_change_equal_earth.png
```

## Data Sources

- **Population**: [GPW v4 – Population Count, Rev. 11](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count-rev11/data-download) — CIESIN, Columbia University (2018). NASA SEDAC. [DOI: 10.7927/H4JW8BX5](https://doi.org/10.7927/H4JW8BX5)
- **India Boundary**: Survey of India (SOI) official boundary via [geoKosh](https://github.com/somdeepkundu/geoKosh/tree/main/IndiaShapes)

## Notes

- The India boundary uses the **official Survey of India shapefile** which includes J&K and Ladakh as per the official boundary.
- All data is downloaded automatically when running the notebook — no manual downloads needed.
- For poster-quality output, set `dpi=600` in the `savefig` call.

- Inspired by works of Ujaval Gandhi, [Spatial Thoughts](https://youtu.be/l1Q3gKnH5Ik?si=JC4TetFs7tHtS1nQ). 

## Author

**Somdeep Kundu**
RuDRA Lab, C-TARA, IIT Bombay

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

