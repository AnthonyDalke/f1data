CREATE TEMPORARY TABLE IF NOT EXISTS temp_rookie_results AS
	WITH rookie_seasons AS (
	    SELECT 
	        id_driver, 
	        MIN("year") AS rookie_year
	    FROM 
	        sessions.events_denormalized
	    WHERE
	    	id_driver NOT IN (
	    		'alonso',
	    		'button',
	    		'coulthard',
	    		'fisichella',
	    		'frentzen',
	    		'gene',
	    		'heidfeld',
	    		'montoya',
	    		'panis',
	    		'pizzonia',
	    		'raikkonen',
	    		'ralf_schumacher',
	    		'sato',
	    		'trulli',
	    		'verstappen',
	    		'webber',
	    		'michael_schumacher',
	    		'barrichello',
	    		'villeneuve'
	    	)
	    GROUP BY 
	        id_driver
	), rookie_teams AS (
	    SELECT DISTINCT
	        e.id_driver, 
	        e."year", 
	        e.name_team
	    FROM 
	        sessions.events_denormalized e
	    INNER JOIN 
	        rookie_seasons r 
	    ON 
	        e.id_driver = r.id_driver 
	        AND e."year" = r.rookie_year
	), team_rookie_season AS (
	    SELECT DISTINCT
	        e.*,
	        CASE 
	            WHEN e.id_driver = rt.id_driver THEN 'rookie'
	            ELSE 'teammate'
	        END AS ind_rookie
	    FROM 
	        sessions.events_denormalized e
	    INNER JOIN 
	        rookie_teams rt 
	    ON 
	        e."year" = rt."year"
	        AND e.name_team = rt.name_team
	), filtered_results AS (
		SELECT DISTINCT
			trs.*
	    FROM 
	        team_rookie_season trs
	    WHERE 
	        NOT EXISTS (
	            SELECT 1
	            FROM sessions.events_denormalized e
	            WHERE e."year" = trs."year"
	              AND e."round" = trs."round"
	              AND e."session" = trs."session"
	              AND e.name_team = trs.name_team 
	              AND e."position" = 'DNF'
        	)
		)
	SELECT 
	    *
	FROM 
	    filtered_results;

WITH session_max_rookie AS (
    SELECT
        "year",
        "round",
        name_circuit,
        country_circuit,
        name_team,
        id_driver AS id_rookie,
        name_driver_last AS name_rookie_last,
        name_driver_first AS name_rookie_first,
        "session",
        "position",
        EXTRACT(EPOCH FROM "time") AS time_rookie,
        ROW_NUMBER() OVER (PARTITION BY "year", "round", name_team, id_driver ORDER BY 
            CASE 
                WHEN "session" = 'Q3' THEN 3
                WHEN "session" = 'Q2' THEN 2
                WHEN "session" = 'Q1' THEN 1
            END DESC) AS rn
    FROM
        temp_rookie_results
    WHERE 
        "session" LIKE 'Q%'
        AND "position" <> 'DNQ'
        AND ind_rookie = 'rookie'
),
session_max_teammate AS (
    SELECT
        "year",
        "round",
        name_circuit,
        country_circuit,
        name_team,
        id_driver AS id_teammate,
        name_driver_last AS name_teammate_last,
        name_driver_first AS name_teammate_first,
        "session",
        "position",
        EXTRACT(EPOCH FROM "time") AS time_teammate,
        ROW_NUMBER() OVER (PARTITION BY "year", "round", name_team, id_driver ORDER BY 
            CASE 
                WHEN "session" = 'Q3' THEN 3
                WHEN "session" = 'Q2' THEN 2
                WHEN "session" = 'Q1' THEN 1
            END DESC) AS rn
    FROM
        temp_rookie_results
    WHERE 
        "session" LIKE 'Q%'
        AND "position" <> 'DNQ'
        AND ind_rookie = 'teammate'
),
rookie_final AS (
    SELECT
        r."year",
        r."round",
        r.name_circuit,
        r.country_circuit,
        r.name_team,
        r.id_rookie,
        r.name_rookie_last,
        r.name_rookie_first,
        r."session" AS session_final_rookie,
        r."position" AS position_rookie,
        r.time_rookie
    FROM
        session_max_rookie r
    WHERE
        r.rn = 1
),
teammate_final AS (
    SELECT
        t."year",
        t."round",
        t.name_circuit,
        t.country_circuit,
        t.name_team,
        t.id_teammate,
        t.name_teammate_last,
        t.name_teammate_first,
        t."session" AS session_final_teammate,
        t."position" AS position_teammate,
        t.time_teammate
    FROM
        session_max_teammate t
    WHERE
        t.rn = 1
),
results_full AS (
    SELECT 
        r."year",
        r."round",
        r.name_circuit,
        r.country_circuit,
        r.name_team,
        r.id_rookie,
        r.name_rookie_last,
        r.name_rookie_first,
        r.session_final_rookie,
        r.position_rookie,
        r.time_rookie,
        t.id_teammate,
        t.name_teammate_last,
        t.name_teammate_first,
        t.session_final_teammate,
        t.position_teammate,
        t.time_teammate,
        CASE 
            WHEN r.session_final_rookie = t.session_final_teammate THEN ROUND(r.time_rookie / t.time_teammate * 100, 2)
            ELSE NULL
        END AS time_relative,
        CASE
            WHEN r.session_final_rookie > t.session_final_teammate THEN 1
            WHEN r.session_final_rookie = t.session_final_teammate
                AND r.time_rookie < t.time_teammate THEN 1
            ELSE 0
        END AS quali_win
    FROM
        rookie_final r
    INNER JOIN
        teammate_final t
	    ON r."year" = t."year"
	    AND r."round" = t."round"
	    AND r.name_team = t.name_team
)
SELECT 
    id_rookie,
    name_rookie_last,
    name_rookie_first,
    name_team,
    id_teammate,
    name_teammate_last,
    name_teammate_first,
    "year",
    ROUND(AVG(time_relative), 2) AS time_relative_avg,
    SUM(quali_win) AS quali_win_total,
    ROUND(SUM(quali_win) * 1.0 / COUNT(*) * 100, 2) AS quali_win_pct
FROM
    results_full
WHERE 
	id_rookie <> id_teammate
GROUP BY
    id_rookie,
    name_rookie_last,
    name_rookie_first,
    name_team,
    id_teammate,
    name_teammate_last,
    name_teammate_first,
    "year";

WITH results_rookie AS (
	SELECT 
		"year",
		"round",
		name_circuit,
		country_circuit,
		name_team,
		id_driver AS id_rookie,
        name_driver_last AS name_rookie_last,
        name_driver_first AS name_rookie_first,
        "position" AS position_rookie,
        EXTRACT(EPOCH FROM "time") AS time_rookie
	FROM
		temp_rookie_results
	WHERE 
		"session" = 'Race'
		AND ind_rookie = 'rookie'
		AND "position" <> 'DNF'
), results_teammate AS (
	SELECT 
		"year",
		"round",
		name_circuit,
		country_circuit,
		name_team,
		id_driver AS id_teammate,
        name_driver_last AS name_teammate_last,
        name_driver_first AS name_teammate_first,
        "position" AS position_teammate,
        EXTRACT(EPOCH FROM "time") AS time_teammate
	FROM
		temp_rookie_results
	WHERE 
		"session" = 'Race'
		AND ind_rookie = 'teammate'
		AND "position" <> 'DNF'
), results_full AS (
    SELECT 
        r."year",
        r."round",
        r.name_circuit,
        r.country_circuit,
        r.name_team,
        r.id_rookie,
        r.name_rookie_last,
        r.name_rookie_first,
        r.position_rookie,
        r.time_rookie,
        t.id_teammate,
        t.name_teammate_last,
        t.name_teammate_first,
        t.position_teammate,
        t.time_teammate, 
        ROUND(r.time_rookie / t.time_teammate * 100, 2) AS time_relative,
        CASE
            WHEN r.position_rookie::INT < t.position_teammate::INT THEN 1
            ELSE 0
        END AS race_win
    FROM
        results_rookie r
    INNER JOIN
        results_teammate t
	    ON r."year" = t."year"
	    AND r."round" = t."round"
	    AND r.name_team = t.name_team
)
SELECT 
    id_rookie,
    name_rookie_last,
    name_rookie_first,
    name_team,
    id_teammate,
    name_teammate_last,
    name_teammate_first,
    "year",
    ROUND(AVG(time_relative), 2) AS time_relative_avg,
    SUM(race_win) AS race_win_total,
    ROUND(SUM(race_win) * 1.0 / COUNT(*) * 100, 2) AS race_win_pct
FROM
    results_full
WHERE 
	id_rookie <> id_teammate
GROUP BY
    id_rookie,
    name_rookie_last,
    name_rookie_first,
    name_team,
    id_teammate,
    name_teammate_last,
    name_teammate_first,
    "year";

DROP TABLE temp_rookie_results;