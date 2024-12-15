CREATE TEMPORARY TABLE IF NOT EXISTS temp_rookie_results AS
    WITH rookie_seasons AS (
        SELECT 
            r.id_driver, 
            MIN(r.year) AS rookie_year
        FROM 
            sessions.results r
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
            r.id_driver
    ),
    rookie_teams AS (
        SELECT DISTINCT
            r.id_driver, 
            r.year, 
            r.name_team
        FROM 
            sessions.results r
        INNER JOIN 
            rookie_seasons rs 
        ON 
            r.id_driver = rs.id_driver 
            AND r.year = rs.rookie_year
    ),
    team_rookie_season AS (
        SELECT DISTINCT
            r.*,
            CASE 
                WHEN r.id_driver = rt.id_driver THEN 'rookie'
                ELSE 'teammate'
            END AS ind_rookie
        FROM 
            sessions.results r
        INNER JOIN 
            rookie_teams rt 
        ON 
            r.year = rt.year
            AND r.name_team = rt.name_team
    ),
	filtered_results AS (
		SELECT DISTINCT
			trs.*
        FROM 
            team_rookie_season trs
        WHERE 
            NOT EXISTS (
                SELECT 1
                FROM sessions.results r
                WHERE r.year = trs.year
                  AND r.round = trs.round
                  AND r.session = trs.session
                  AND r.name_team = trs.name_team 
                  AND r.position = 'DNF'
            )
    )
    SELECT 
        fr.year,
        fr.round,
        c.name_circuit,
        c.country_circuit,
        fr.id_driver,
        d.name_driver_last,
        d.name_driver_first,
        fr.name_team,
        fr.session,
        fr.position,
        fr.time,
        fr.ind_rookie
    FROM 
        filtered_results fr
    INNER JOIN 
        sessions.events e ON fr.year = e.year AND fr.round = e.round
    INNER JOIN 
        sessions.circuits c ON e.name_circuit = c.name_circuit
    INNER JOIN 
        sessions.drivers d ON fr.id_driver = d.id_driver;

DROP TABLE temp_rookie_results;