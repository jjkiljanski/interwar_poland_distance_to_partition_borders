import os
import geopandas as gpd
from shapely.ops import unary_union
from shapely.geometry import MultiLineString
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Input paths
EUROPE_PATH = r"E:\git_projects\mosaic_gis_europe_1900-2003\01 Europe Main\Europe_1900_v.1.1.shp"
POLAND_DISTRICTS_PATH = r"districts_1934_10_1.geojson"

# Output folder (relative)
OUTPUT_DIR = "output"

# Output paths (all relative to OUTPUT_DIR)
PARTITIONS_BORDERS_PATH = os.path.join(OUTPUT_DIR, "poland_partition_borders.shp")
DISTRICTS_WITH_DIST_CSV = os.path.join(OUTPUT_DIR, "districts_with_partition_distances.csv")

FIG_EMPIRES_EUROPE = os.path.join(OUTPUT_DIR, "empires_europe.png")
FIG_POLAND_PARTITIONS = os.path.join(OUTPUT_DIR, "poland_partitions.png")
FIG_DISTANCES = os.path.join(OUTPUT_DIR, "distances_to_borders.png")
FIG_DISTRICTS_PARTITIONS = os.path.join(OUTPUT_DIR, "districts_partitions.png")

# CRS in meters (for distance calculations)
TARGET_CRS = "EPSG:3035"  # ETRS89 / LAEA Europe


def to_multilines(geom):
    """
    Convert a geometry (possibly GeometryCollection) to a MultiLineString
    containing only line geometries. Returns None if there are no lines.
    """
    if geom is None or geom.is_empty:
        return None

    if geom.geom_type == "LineString":
        return MultiLineString([geom])

    if geom.geom_type == "MultiLineString":
        return geom

    if geom.geom_type == "GeometryCollection":
        lines = []
        for g in geom.geoms:
            if g.geom_type == "LineString":
                lines.append(g)
            elif g.geom_type == "MultiLineString":
                lines.extend(list(g.geoms))
        if not lines:
            return None
        return MultiLineString(lines)

    # For any other geometry type, return None
    return None


def main():
    # Make sure output folder exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load data
    europe = gpd.read_file(EUROPE_PATH)
    poland_districts = gpd.read_file(POLAND_DISTRICTS_PATH)

    # Ensure CRS is defined and reproject both to a metric CRS
    if europe.crs is None:
        raise ValueError("Europe shapefile has no CRS defined – set it manually before running the script.")
    if poland_districts.crs is None:
        raise ValueError("Polish districts layer has no CRS defined – set it manually before running the script.")

    europe = europe.to_crs(TARGET_CRS)
    poland_districts = poland_districts.to_crs(TARGET_CRS)

    # ----------------------------------------------------------------------
    # 1. SELECT THREE EMPIRES AND PLOT THEM (EACH IN A DIFFERENT COLOR)
    # ----------------------------------------------------------------------

    # Austria-Hungary: COUNTRY = 10 and 240
    ah = europe[europe["COUNTRY"].isin([10, 240])].copy()
    # Germany: COUNTRY = 80
    germany = europe[europe["COUNTRY"] == 80].copy()
    # Russia: COUNTRY = 160 or 140
    russia = europe[europe["COUNTRY"].isin([140, 160])].copy()

    # Union (single polygon) for each empire
    ah_union = unary_union(ah.geometry)
    germany_union = unary_union(germany.geometry)
    russia_union = unary_union(russia.geometry)

    ah_gdf = gpd.GeoDataFrame({"name": ["Austria-Hungary"]}, geometry=[ah_union], crs=europe.crs)
    germany_gdf = gpd.GeoDataFrame({"name": ["Germany"]}, geometry=[germany_union], crs=europe.crs)
    russia_gdf = gpd.GeoDataFrame({"name": ["Russia"]}, geometry=[russia_union], crs=europe.crs)

    # Plot three empires in Europe and save figure
    fig, ax = plt.subplots(figsize=(10, 10))
    ah_gdf.plot(ax=ax, linewidth=0.8, edgecolor="black", facecolor="#D9D9D9", label="Austria-Hungary")
    germany_gdf.plot(ax=ax, linewidth=0.8, edgecolor="black", facecolor="#A6A6A6", label="Germany")
    russia_gdf.plot(ax=ax, linewidth=0.8, edgecolor="black", facecolor="#737373", label="Russia")

    ax.set_title("Austria-Hungary, Germany and Russia in Europe (ca. 1900)", fontsize=14)
    ax.legend()
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(FIG_EMPIRES_EUROPE, dpi=300)
    plt.close(fig)

    # ----------------------------------------------------------------------
    # 2. POLAND UNION, CLIP EMPIRES TO POLAND, AND PLOT PARTITIONS
    # ----------------------------------------------------------------------

    # Union of districts to get a single Poland geometry
    poland_union_geom = unary_union(poland_districts.geometry)
    poland_union_gdf = gpd.GeoDataFrame(geometry=[poland_union_geom], crs=poland_districts.crs)

    # Clip empire polygons to Poland's outline -> partition polygons within Poland
    ah_in_pl = gpd.clip(ah_gdf, poland_union_geom)
    germany_in_pl = gpd.clip(germany_gdf, poland_union_geom)
    russia_in_pl = gpd.clip(russia_gdf, poland_union_geom)

    # Build single-part polygons (union) for each partition inside Poland
    ah_part_poly = ah_in_pl.unary_union
    germany_part_poly = germany_in_pl.unary_union
    russia_part_poly = russia_in_pl.unary_union

    ah_part_gdf = gpd.GeoDataFrame({"empire": ["Austria-Hungary"]},
                                   geometry=[ah_part_poly], crs=poland_districts.crs)
    germany_part_gdf = gpd.GeoDataFrame({"empire": ["Germany"]},
                                        geometry=[germany_part_poly], crs=poland_districts.crs)
    russia_part_gdf = gpd.GeoDataFrame({"empire": ["Russia"]},
                                       geometry=[russia_part_poly], crs=poland_districts.crs)

    # Plot Poland (union of all districts) with partitions filled in three colors
    fig, ax = plt.subplots(figsize=(10, 10))

    # Poland outline
    poland_union_gdf.boundary.plot(ax=ax, linewidth=0.8, edgecolor="black")

    # Partition polygons in different colors (three greys)
    germany_part_gdf.plot(ax=ax, alpha=0.6, edgecolor="black",
                          facecolor="#A6A6A6", label="Germany")
    russia_part_gdf.plot(ax=ax, alpha=0.6, edgecolor="black",
                         facecolor="#737373", label="Russia")
    ah_part_gdf.plot(ax=ax, alpha=0.6, edgecolor="black",
                     facecolor="#D9D9D9", label="Austria-Hungary")

    ax.set_title("Poland partitioned between Austria-Hungary, Germany and Russia", fontsize=14)
    ax.legend()
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(FIG_POLAND_PARTITIONS, dpi=300)
    plt.close(fig)

    # ----------------------------------------------------------------------
    # 2a. ASSIGN EACH DISTRICT TO A PARTITION (BY CENTROID)
    # ----------------------------------------------------------------------
    centroids = poland_districts.geometry.centroid

    poland_districts["former_german_partition"] = centroids.within(germany_part_poly)
    poland_districts["former_russian_partition"] = centroids.within(russia_part_poly)
    poland_districts["former_ah_partition"] = centroids.within(ah_part_poly)

    # ----------------------------------------------------------------------
    # 3. INTERNAL PARTITION BORDERS (LINES ONLY) - FULL
    # ----------------------------------------------------------------------

    # Borders (line geometries) of each partition polygon inside Poland
    ah_border_poly = ah_part_gdf.boundary.unary_union
    germany_border_poly = germany_part_gdf.boundary.unary_union
    russia_border_poly = russia_part_gdf.boundary.unary_union

    # Pairwise intersections of empire borders inside Poland -> internal partition lines
    ah_ge_raw = ah_border_poly.intersection(germany_border_poly).intersection(poland_union_geom)
    ah_ru_raw = ah_border_poly.intersection(russia_border_poly).intersection(poland_union_geom)
    ge_ru_raw = germany_border_poly.intersection(russia_border_poly).intersection(poland_union_geom)

    ah_ge_ml = to_multilines(ah_ge_raw)
    ah_ru_ml = to_multilines(ah_ru_raw)
    ge_ru_ml = to_multilines(ge_ru_raw)

    # GeoDataFrame with internal partition borders (lines only) - FULL
    rows = []
    if ah_ge_ml is not None:
        rows.append({"between": "Austria-Hungary–Germany", "geometry": ah_ge_ml})
    if ah_ru_ml is not None:
        rows.append({"between": "Austria-Hungary–Russia", "geometry": ah_ru_ml})
    if ge_ru_ml is not None:
        rows.append({"between": "Germany–Russia", "geometry": ge_ru_ml})

    if not rows:
        raise RuntimeError("No internal partition borders were generated – check country codes and clipping.")

    partitions_borders_full = gpd.GeoDataFrame(rows, crs=TARGET_CRS)

    # ----------------------------------------------------------------------
    # 3a. TRIM PARTITION BORDERS NEAR EXTERNAL POLAND BORDER (5 KM BUFFER)
    # ----------------------------------------------------------------------
    poland_border_full = poland_union_gdf.boundary.unary_union
    buffer_5km = poland_border_full.buffer(5000)  # CRS is in meters

    trimmed_geoms = []
    between_vals = []

    for between, geom in zip(partitions_borders_full["between"], partitions_borders_full.geometry):
        if geom is None or geom.is_empty:
            continue
        diff = geom.difference(buffer_5km)
        diff_ml = to_multilines(diff)
        if diff_ml is None or diff_ml.is_empty:
            continue
        trimmed_geoms.append(diff_ml)
        between_vals.append(between)

    if not trimmed_geoms:
        raise RuntimeError("After trimming, no internal partition borders remain. Check buffer size or geometries.")

    partitions_borders_trimmed = gpd.GeoDataFrame(
        {"between": between_vals, "geometry": trimmed_geoms},
        crs=TARGET_CRS
    )

    # Save only the trimmed internal partition borders (lines) to a shapefile
    partitions_borders_trimmed.to_file(PARTITIONS_BORDERS_PATH)
    print(f"Saved trimmed partition borders within Poland (lines only) to: {PARTITIONS_BORDERS_PATH}")

    # ----------------------------------------------------------------------
    # 3b. PREPARE LINES FOR DISTANCE CALCULATIONS (USING TRIMMED BORDERS)
    # ----------------------------------------------------------------------
    germany_line_geoms = partitions_borders_trimmed.loc[
        partitions_borders_trimmed["between"].isin(["Austria-Hungary–Germany", "Germany–Russia"]),
        "geometry"
    ].tolist()
    germany_border_lines = unary_union(germany_line_geoms) if germany_line_geoms else None

    russia_line_geoms = partitions_borders_trimmed.loc[
        partitions_borders_trimmed["between"].isin(["Germany–Russia", "Austria-Hungary–Russia"]),
        "geometry"
    ].tolist()
    russia_border_lines = unary_union(russia_line_geoms) if russia_line_geoms else None

    ah_line_geoms = partitions_borders_trimmed.loc[
        partitions_borders_trimmed["between"].isin(["Austria-Hungary–Germany", "Austria-Hungary–Russia"]),
        "geometry"
    ].tolist()
    ah_border_lines = unary_union(ah_line_geoms) if ah_line_geoms else None

    # ----------------------------------------------------------------------
    # DISTANCE TO INTERNAL BORDERS (USING CENTROIDS AND TRIMMED LINES)
    # ----------------------------------------------------------------------
    poland_districts["distance_to_german_border"] = np.nan
    poland_districts["distance_to_russian_border"] = np.nan
    poland_districts["distance_to_AH_border"] = np.nan

    if germany_border_lines is not None:
        poland_districts["distance_to_german_border"] = centroids.distance(germany_border_lines) / 1000.0
    if russia_border_lines is not None:
        poland_districts["distance_to_russian_border"] = centroids.distance(russia_border_lines) / 1000.0
    if ah_border_lines is not None:
        poland_districts["distance_to_AH_border"] = centroids.distance(ah_border_lines) / 1000.0

    # ----------------------------------------------------------------------
    # 4. PLOT DISTANCE MAPS AND SAVE
    # ----------------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    poland_districts.plot(
        column="distance_to_german_border",
        ax=axes[0],
        legend=True,
    )
    axes[0].set_title("Distance to German partition border (km)")
    axes[0].set_axis_off()

    poland_districts.plot(
        column="distance_to_russian_border",
        ax=axes[1],
        legend=True,
    )
    axes[1].set_title("Distance to Russian partition border (km)")
    axes[1].set_axis_off()

    poland_districts.plot(
        column="distance_to_AH_border",
        ax=axes[2],
        legend=True,
    )
    axes[2].set_title("Distance to Austro-Hungarian partition border (km)")
    axes[2].set_axis_off()

    plt.tight_layout()
    fig.savefig(FIG_DISTANCES, dpi=300)
    plt.close(fig)

    # ----------------------------------------------------------------------
    # 5. MAP: DISTRICTS COLORED BY PARTITION +
    #         BLACK FULL BORDER + RED TRIMMED BORDER
    # ----------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 10))

    german_districts = poland_districts[poland_districts["former_german_partition"]]
    russian_districts = poland_districts[poland_districts["former_russian_partition"]]
    ah_districts = poland_districts[poland_districts["former_ah_partition"]]

    ah_districts.plot(ax=ax, facecolor="#D9D9D9", edgecolor="black", linewidth=0.3)
    german_districts.plot(ax=ax, facecolor="#A6A6A6", edgecolor="black", linewidth=0.3)
    russian_districts.plot(ax=ax, facecolor="#737373", edgecolor="black", linewidth=0.3)

    # Full internal partition borders in bold black (background)
    partitions_borders_full.plot(ax=ax, color="black", linewidth=2.0)

    # Trimmed partition borders in bold red (on top)
    partitions_borders_trimmed.plot(ax=ax, color="red", linewidth=2.0)

    ax.set_title("Districts by former partition with full and trimmed partition borders", fontsize=14)
    ax.set_axis_off()

    # Custom legend (no geopandas warnings)
    legend_handles = [
        Patch(facecolor="#D9D9D9", edgecolor="black", label="Austria-Hungary"),
        Patch(facecolor="#A6A6A6", edgecolor="black", label="Germany"),
        Patch(facecolor="#737373", edgecolor="black", label="Russia"),
        Line2D([0], [0], color="black", linewidth=2, label="Partition borders (full)"),
        Line2D([0], [0], color="red", linewidth=2, label="Partition borders (>5 km away from Polish borders)"),
    ]
    ax.legend(handles=legend_handles, loc="lower left")

    plt.tight_layout()
    fig.savefig(FIG_DISTRICTS_PARTITIONS, dpi=300)
    plt.close(fig)

    # ----------------------------------------------------------------------
    # 6. Save districts with distance variables and partition flags (CSV)
    # ----------------------------------------------------------------------
    poland_districts.drop(columns="geometry").to_csv(
        DISTRICTS_WITH_DIST_CSV,
        index=False,
        encoding="utf-8"
    )
    print(f"Saved districts with distance variables and partition flags to: {DISTRICTS_WITH_DIST_CSV}")


if __name__ == "__main__":
    main()
