from datetime import date
from database import engine, SessionLocal, Base
import models


# Create all database tables
Base.metadata.create_all(bind=engine)


def seed_database():
    db = SessionLocal()

    try:
        # -------------------------------------------------
        # 1. CHECK WHETHER DEMO DATA ALREADY EXISTS
        # -------------------------------------------------
        existing = db.query(models.Watershed).first()

        if existing:
            print("Demo data already exists.")
            print("Nothing to seed.")
            return

        # -------------------------------------------------
        # 2. WATERSHED
        # -------------------------------------------------
        watershed = models.Watershed(
            name="Demo Watershed",
            district="Howrah",
            state="West Bengal",
            latitude=22.5958,
            longitude=88.2636,
            area=125.50
        )

        db.add(watershed)
        db.commit()
        db.refresh(watershed)

        print(f"Created watershed: {watershed.name}")
        print(f"Watershed ID: {watershed.id}")

        # -------------------------------------------------
        # 3. GEO-CODED IMAGE METADATA
        # -------------------------------------------------
        image = models.Image(
            watershed_id=watershed.id,
            image_path="uploads/demo_watershed.jpg",
            latitude=22.5958,
            longitude=88.2636,
            capture_date=date(2026, 8, 15)
        )

        db.add(image)

        # -------------------------------------------------
        # 4. WATERSHED INTERVENTION
        # -------------------------------------------------
        intervention = models.Intervention(
            watershed_id=watershed.id,
            type="Farm Pond",
            latitude=22.5965,
            longitude=88.2642,
            date=date(2026, 8, 20),
            status="Completed",
            description="Farm pond constructed for rainwater harvesting and irrigation support."
        )

        db.add(intervention)

        # -------------------------------------------------
        # 5. SATELLITE ANALYSIS
        # -------------------------------------------------
        analysis = models.SatelliteAnalysis(
            watershed_id=watershed.id,
            ndvi=0.62,
            water_area=18.40,
            vegetation_area=72.30,
            soil_area=34.80,
            analysis_date=date(2026, 8, 25)
        )

        db.add(analysis)

        # -------------------------------------------------
        # 6. CHANGE DETECTION
        # -------------------------------------------------
        change = models.ChangeDetection(
            watershed_id=watershed.id,
            previous_date=date(2026, 7, 25),
            current_date=date(2026, 8, 25),
            vegetation_change=8.50,
            water_change=12.30,
            land_change=-5.20,
            change_percentage=9.70
        )

        db.add(change)

        # -------------------------------------------------
        # 7. SAVE EVERYTHING
        # -------------------------------------------------
        db.commit()

        print()
        print("========================================")
        print(" DEMO DATABASE CREATED SUCCESSFULLY")
        print("========================================")
        print()
        print("Watershed:")
        print("  Name: Demo Watershed")
        print("  District: Howrah")
        print("  State: West Bengal")
        print()
        print("Created:")
        print("  ✓ Watershed")
        print("  ✓ Geo-coded image metadata")
        print("  ✓ Farm pond intervention")
        print("  ✓ Satellite analysis")
        print("  ✓ Change detection")
        print()
        print("Database is ready for the backend.")
        print("========================================")

    except Exception as e:
        db.rollback()
        print("ERROR while creating demo data:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()