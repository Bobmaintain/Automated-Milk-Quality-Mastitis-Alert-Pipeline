# Automated Milk Quality & Mastitis Alert Pipeline (Data Quality)

## The Scenario
Automated milking robots record somatic cell counts (SOC), milk conductivity, and yield for every cow at every milking.
Bad data can cause missed illness alerts.

## The Engineering Goal:
Build a pipeline focused heavily on **Data Quality and Quarantine**. Bad records are routed to an error table,
while critical health spikes trigger an automated alert.

## What it Does:
**Data Validation:** Strict Python checks to ensure metrics fall within valid ranges before entering the main database.

**Quarantine Routing:** Splitting data into two SQL tables (`clean_milk_logs` and `quarantined_sensor_errors`)
so no raw data is ever lost.:

**Automated Alerting:** Using Python's built-in `smtplib` to send automated email alerts whenever 
a cow's somatic cell count crosses a mastitis threshold.
