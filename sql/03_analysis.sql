-- VEHICLE COMPLAINT ANALYTICS
-- Data source: NHTSA
-- Models: Camry, Accord, Altima
-- Model years: 2017-2019


-- 1. Complaint counts by vehicle and model year

SELECT
    UPPER(TRIM(make)) AS manufacturer,
    UPPER(TRIM(model)) AS vehicle_model,
    model_year,
    COUNT(*) AS complaint_count
FROM vehicle_complaints
WHERE model_year BETWEEN 2017 AND 2019
  AND (
       (UPPER(TRIM(make)) = 'TOYOTA'
        AND UPPER(TRIM(model)) = 'CAMRY')
    OR (UPPER(TRIM(make)) = 'HONDA'
        AND UPPER(TRIM(model)) = 'ACCORD')
    OR (UPPER(TRIM(make)) = 'NISSAN'
        AND UPPER(TRIM(model)) = 'ALTIMA')
  )
GROUP BY
    UPPER(TRIM(make)),
    UPPER(TRIM(model)),
    model_year
ORDER BY manufacturer, model_year;


-- 2. Top reported components by vehicle model

SELECT
    manufacturer,
    vehicle_model,
    component,
    SUM(complaint_count) AS complaint_mentions
FROM vw_component_analysis
WHERE model_year BETWEEN 2017 AND 2019
  AND (
       (manufacturer = 'TOYOTA' AND vehicle_model = 'CAMRY')
    OR (manufacturer = 'HONDA' AND vehicle_model = 'ACCORD')
    OR (manufacturer = 'NISSAN' AND vehicle_model = 'ALTIMA')
  )
  AND component <> 'UNKNOWN OR OTHER'
GROUP BY manufacturer, vehicle_model, component
ORDER BY complaint_mentions DESC;


-- 3. Component reporting percentages

SELECT
    manufacturer,
    vehicle_model,
    model_year,
    component,
    complaint_count,
    total_vehicle_complaints,
    component_percentage
FROM vw_component_share
WHERE model_year BETWEEN 2017 AND 2019
  AND (
       (manufacturer = 'TOYOTA' AND vehicle_model = 'CAMRY')
    OR (manufacturer = 'HONDA' AND vehicle_model = 'ACCORD')
    OR (manufacturer = 'NISSAN' AND vehicle_model = 'ALTIMA')
  )
ORDER BY manufacturer, model_year, component_percentage DESC;


-- 4. Data quality checks

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT odi_number) AS unique_ids,
    COUNT(*) FILTER (
        WHERE odi_number IS NULL
           OR TRIM(odi_number) = ''
    ) AS missing_ids
FROM vehicle_complaints;


-- 5. Detect duplicate ODI identifiers

SELECT
    odi_number,
    COUNT(*) AS occurrences
FROM vehicle_complaints
GROUP BY odi_number
HAVING COUNT(*) > 1;
