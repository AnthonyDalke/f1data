UPDATE
	sessions.events_denormalized ed 
SET
	name_team = 'Marussia'
WHERE 
	name_team LIKE 'Manor Marussia';


UPDATE
	sessions.events_denormalized ed 
SET
	name_team = 'Alfa Romeo'
WHERE 
	name_team LIKE 'Alfa Romeo Racing';


UPDATE
	sessions.events_denormalized ed 
SET
	name_team = 'Red Bull'
WHERE 
	name_team LIKE 'Red Bull Racing';

UPDATE
	sessions.events_denormalized ed 
SET
	name_team = 'Spyker'
WHERE 
	name_team LIKE 'Spyker MF1';


UPDATE
	sessions.events_denormalized ed 
SET
	name_team = 'Spyker'
WHERE 
	name_team LIKE 'MF1';


UPDATE
	sessions.events_denormalized ed 
SET
	name_team = 'Lotus'
WHERE 
	name_team LIKE 'Lotus F1';


UPDATE
	sessions.events_denormalized ed 
SET 
	name_driver_last = 'Perez'
WHERE 
	name_driver_last = 'Pérez';


UPDATE
	sessions.events_denormalized ed 
SET 
	name_driver_last = 'Hulkenberg'
WHERE 
	name_driver_last = 'Hülkenberg';


UPDATE
	sessions.events_denormalized ed 
SET 
	id_driver = 'albon'
WHERE 
	name_driver_last = 'Albon'
	AND id_driver = 'nan';


UPDATE
	sessions.events_denormalized ed 
SET 
	id_driver = 'mick_schumacher'
WHERE 
	name_driver_last = 'Schumacher'
	AND id_driver = 'nan';


DELETE FROM sessions.events_denormalized ed 
WHERE 
	name_driver_last IN (
		'Bottas',
		'Hamilton',
		'Leclerc',
		'Norris',
		'Ocon',
		'Perez',
		'Räikkönen',
		'Russell',
		'Sainz',
		'Stroll',
		'Verstappen'
	)
	AND id_driver = '';
	

DELETE FROM	sessions.drivers 
WHERE 
	name_driver_last = 'Leclerc'
	AND id_driver = '';


DELETE FROM sessions.drivers 
WHERE 
	id_driver = 'colapinto ';
	
DELETE FROM sessions.drivers 
WHERE 
	name_driver_last = 'Schumacher'
	AND id_driver = 'nan';


DELETE FROM 
	sessions.drivers
WHERE 
	name_driver_last = 'Norris'
	AND id_driver = '';


UPDATE 
	sessions.teams
SET 
	name_team = 'Alfa Romeo'
WHERE 
	name_team = 'Alfa Romeo Racing';


UPDATE 
	sessions.teams 
SET 
	name_team = 'Spyker'
WHERE 
	name_team = 'MF1';
	

DELETE FROM
	sessions.teams
WHERE 
	name_team = 'Spyker MF1'
	AND "year" = 2006;
	

DELETE FROM
	sessions.results
WHERE 
	id_driver = '';
	

DELETE FROM
	sessions.results
WHERE 
	id_driver = 'colapinto ';


UPDATE
	sessions.results
SET
	name_team = 'Marussia'
WHERE 
	name_team LIKE 'Manor Marussia';
	

UPDATE
	sessions.results 
SET
	name_team = 'Red Bull'
WHERE 
	name_team LIKE 'Red Bull Racing';