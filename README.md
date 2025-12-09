## Partition Borders of Interwar Poland — Reproducible Workflow

This repository provides a simple Python workflow for researchers who need **the borders of the Austrian, German, and Russian partitions within interwar Poland**.

![Partition borders](output/districts_partitions.png?v=2)

![Distances to partition borders](output/distances_to_borders.png?v=2)

The repo includes:

* A script that reconstructs the three partition areas using historical GIS data
* Export of partition polygons, partition border lines, and district-level distances
* Verification plots
* **No restricted data** is included

---

## Required Data (user-supplied)

Download the **Europe 1900** shapefile from:

**IPUMS MOSAIC**
[https://mosaic.ipums.org/historical-gis-datafiles](https://mosaic.ipums.org/historical-gis-datafiles)

File needed:

```
Europe_1900_v.1.1.shp
```

Due to IPUMS licensing, the dataset is **not** redistributed here.

---

## How to Run

1. Install dependencies:

```bash
pip install geopandas shapely matplotlib
```

2. Edit paths in `partition_borders.py` to point to:

   * your IPUMS Europe 1900 shapefile
   * the Polish district layer (1934)

3. Run the script:

```bash
python partition_borders.py
```

Outputs will appear in `output/`:

* Partition polygons
* Partition borders (lines)
* District distances
* Maps

---

## Citation

Please cite **IPUMS Mosaic** when using the generated borders.

---
