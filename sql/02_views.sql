-- View 1: Complaint counts by vehicle and year

CREATE OR REPLACE VIEW vw_complaints_by_vehicle_year AS

SELECT
    UPPER(TRIM(make)) AS manufacturer,
    UPPER(TRIM(model)) AS vehicle_model,
    model_year,
    COUNT(*) AS complaint_count

FROM vehicle_complaints

GROUP BY
    UPPER(TRIM(make)),
    UPPER(TRIM(model)),
    model_year;



-- View 2: Component complaint counts

CREATE OR REPLACE VIEW vw_component_analysis AS

WITH separated_components AS (
    SELECT
        vc.odi_number,
        UPPER(TRIM(vc.make)) AS manufacturer,
        UPPER(TRIM(vc.model)) AS vehicle_model,
        vc.model_year,
        UPPER(TRIM(c.component_name)) AS component

    FROM vehicle_complaints AS vc

    CROSS JOIN LATERAL
        regexp_split_to_table(
            COALESCE(vc.component, ''),
            ','
        ) AS c(component_name)
)

SELECT
    manufacturer,
    vehicle_model,
    model_year,
    component,
    COUNT(DISTINCT odi_number) AS complaint_count

FROM separated_components

WHERE component <> ''

GROUP BY
    manufacturer,
    vehicle_model,
    model_year,
    component;

-- View 3: Component reporting percentages

CREATE OR REPLACE VIEW vw_component_share AS

SELECT
    c.manufacturer,
    c.vehicle_model,
    c.model_year,
    c.component,
    c.complaint_count,
    v.complaint_count AS total_vehicle_complaints,

    ROUND(
        100.0 * c.complaint_count / v.complaint_count,
        1
    ) AS component_percentage

FROM vw_component_analysis AS c

JOIN vw_complaints_by_vehicle_year AS v
    ON c.manufacturer = v.manufacturer
    AND c.vehicle_model = v.vehicle_model
    AND c.model_year = v.model_year;

-- View 4: Individual complaint components

CREATE OR REPLACE VIEW vw_complaint_components_detail AS

SELECT DISTINCT
    vc.odi_number,
    UPPER(TRIM(c.component_name)) AS component

FROM vehicle_complaints AS vc

CROSS JOIN LATERAL
    regexp_split_to_table(
        COALESCE(vc.component, ''),
        ','
    ) AS c(component_name)

WHERE vc.odi_number IS NOT NULL
  AND TRIM(vc.odi_number) <> ''
  AND TRIM(c.component_name) <> '';    