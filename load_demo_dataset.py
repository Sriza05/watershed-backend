import pandas as pd
from database import SessionLocal, engine, Base
import models


# Make sure database tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Load CSV files
    watersheds_df = pd.read_csv("demo_dataset/watersheds.csv")
    images_df = pd.read_csv("demo_dataset/geo_coded_images.csv")
    interventions_df = pd.read_csv("demo_dataset/interventions.csv")
    analysis_df = pd.read_csv("demo_dataset/satellite_analysis.csv")
    changes_df = pd.read_csv("demo_dataset/change_detection.csv")

    # Check whether this demo dataset is already loaded
    watershed_names = watersheds_df["name"].tolist()

    existing_count = (
        db.query(models.Watershed)
        .filter(models.Watershed.name.in_(watershed_names))
        .count()
    )

    if existing_count == len(watershed_names):
        print("Demo dataset is already loaded.")
        print(f"Watersheds: {existing_count}")
        exit()

    # Map CSV watershed IDs to actual database IDs
    watershed_id_map = {}

    # -------------------------------------------------
    # 1. WATERSHEDS
    # -------------------------------------------------
    for _, row in watersheds_df.iterrows():

        existing = (
            db.query(models.Watershed)
            .filter(models.Watershed.name == row["name"])
            .first()
        )

        if existing:
            watershed_id_map[int(row["id"])] = existing.id

        else:
            watershed = models.Watershed(
                name=row["name"],
                district=row["district"],
                state=row["state"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                area=float(row["area_sq_km"])
            )

            db.add(watershed)
            db.flush()

            watershed_id_map[int(row["id"])] = watershed.id

    # -------------------------------------------------
    # 2. GEO-CODED IMAGES
    # -------------------------------------------------
    for _, row in images_df.iterrows():

        image = models.Image(
            watershed_id=watershed_id_map[int(row["watershed_id"])],
            image_path=row["image_path"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            capture_date=pd.to_datetime(row["capture_date"]).date()
        )

        db.add(image)

    # -------------------------------------------------
    # 3. INTERVENTIONS
    # -------------------------------------------------
    for _, row in interventions_df.iterrows():

        intervention = models.Intervention(
            watershed_id=watershed_id_map[int(row["watershed_id"])],
            type=row["type"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            date=pd.to_datetime(row["date"]).date(),
            status=row["status"],
            description=row["description"]
        )

        db.add(intervention)

    # -------------------------------------------------
    # 4. SATELLITE ANALYSIS
    # -------------------------------------------------
    for _, row in analysis_df.iterrows():

        analysis = models.SatelliteAnalysis(
            watershed_id=watershed_id_map[int(row["watershed_id"])],
            ndvi=float(row["ndvi"]),
            water_area=float(row["water_area"]),
            vegetation_area=float(row["vegetation_area"]),
            soil_area=float(row["soil_area"]),
            analysis_date=pd.to_datetime(row["analysis_date"]).date()
        )

        db.add(analysis)

    # -------------------------------------------------
    # 5. CHANGE DETECTION
    # -------------------------------------------------
    for _, row in changes_df.iterrows():

        change = models.ChangeDetection(
            watershed_id=watershed_id_map[int(row["watershed_id"])],
            previous_date=pd.to_datetime(row["previous_date"]).date(),
            current_date=pd.to_datetime(row["current_date"]).date(),
            vegetation_change=float(row["vegetation_change"]),
            water_change=float(row["water_change"]),
            land_change=float(row["land_change"]),
            change_percentage=float(row["change_percentage"])
        )

        db.add(change)

    # Save everything
    db.commit()

    print()
    print("==========================================")
    print("JalDrishti Demo Dataset Loaded Successfully")
    print("==========================================")
    print(f"Watersheds: {len(watersheds_df)}")
    print(f"Geo-coded images: {len(images_df)}")
    print(f"Interventions: {len(interventions_df)}")
    print(f"Satellite analyses: {len(analysis_df)}")
    print(f"Change detection records: {len(changes_df)}")
    print("==========================================")

except Exception as e:
    db.rollback()
    print("ERROR while loading dataset:")
    print(e)

finally:
    db.close()