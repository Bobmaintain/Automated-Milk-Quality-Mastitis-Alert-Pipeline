import pandas as pd
import sqlite3


def trigger_vet_alert(cow_id, scc_value, conductivity):
    # Simulates sending an automated email/SMS alert to the herd manager
    print(f"🚨 [ALERT DISPATCHED] Cow #{cow_id} flagged for subclinical mastitis risk SCC: {scc_value:,} cells/ml "
          f"| Conductivity* {conductivity} mS/cm")


def run_milk_quality_pipeline():
    print("1. Ingesting automated milking parlor robot logs...")
    raw_milking_logs = pd.DataFrame({
        "session_id": list(range(501, 507)),
        "cow_id": list((104, 108, 112, 115, 119, 122)),
        "milk_yield_liters": list((14.5, -2.0, 16.2, 11.8, 0.0, 15.1)),             # -2.0 and 0.0 are sensor glitches
        "somatic_cell_count": list((120000, 145000, 380000, 95000, 110000, 410000)),  # >200,000 indicates mastitis risk
        "milk_conductivity_ms": list((4.8, 4.9, 6.4, 4.7, 5.1, 6.8))           # >6.0 indicates infection/inflammation

    })

    # 2. Data Quality Gate (Validation Rules)
    # Rule: Milk yield must be greater than 1.0 liter, and SCC cannot be negative
    valid_mask = (raw_milking_logs['milk_yield_liters'] > 1.0) & (raw_milking_logs['somatic_cell_count'] > 0)

    clean_logs = raw_milking_logs[valid_mask].copy()
    quarantined_logs = raw_milking_logs[~valid_mask].copy()
    quarantined_logs['error_reason'] = "Invalid milk yield sensor reading (<= 1.0L)"

    # 3. Route to separate SQL tables
    conn = sqlite3.connect("dairy_parlor_quality.db")
    clean_logs.to_sql("clean_milking_session", conn, if_exists="replace", index=False)
    quarantined_logs.to_sql("quarantined_sensor_errors", conn, if_exists="replace", index=False)
    print(f"Routing complete: {len(clean_logs)} cleaned records loaded | {len(quarantined_logs)} "
          f"bad records quarantined. \n")

    # 4. Automated Health Threshold Monitoring (Mastitis Detection)
    print("2. Scanning clean records for biological health alerts...")
    mastitis_cases = clean_logs[(clean_logs['somatic_cell_count'] > 25000) | (clean_logs['milk_conductivity_ms'] > 6.0)]

    for _, cow in mastitis_cases.iterrows():
        trigger_vet_alert(int(cow['cow_id']), int(cow['somatic_cell_count']), cow['milk_conductivity_ms'])

    print("\n--- Quarantined Records Table (Saved for Engineering Audit) ---")
    print(pd.read_sql("SELECT * FROM quarantined_sensor_errors", conn))
    conn.close()


if __name__ == "__main__":
    run_milk_quality_pipeline()
