-- Andrew Lee (leea6@oregonstate.edu)
-- Anthony Lomax (lomaxan@oregonstate.edu)
-- Project 29: data(Baseball)

-- get player data, team names, and positions to populate the players page
SELECT players.player_id, players.name, players.birthdate, players.batting, players.running, players.fielding, players.pitching, teams.name, positions.position
FROM players_position
JOIN players on players_position.player_id = players.player_id
JOIN positions on players_position.position_id = positions.position_id
JOIN teams on players.team_id = teams.team_id

-- get team ids and names to populate team dropdown to create a player
SELECT team_id, name FROM teams 

-- get position ids and names to populate position dropdown to create a player
SELECT position_id, name FROM positions 

-- create a new player
INSERT INTO players (name, birthdate, batting, running, fielding, pitching, team_id)
VALUES
(:player_name_input, :birthdate_input, :batting_input, :running_input, :fielding_input, :pitching_input, :team_id_input)

-- update player
UPDATE players 
SET name = :player_name_input, birthdate = :birthdate_input, batting = :batting_input, running = :running_input, fielding = :fielding_input, pitching = :pitching_input, team = :team_id_input
WHERE player_id = :given_player

-- delete player 
DELETE FROM players WHERE player_id = :given_player

-- associate player with their position
INSERT INTO players_positions (player_id, position_id)
VALUES (:given_player, :given_position)

-- disassociate player from their position 
DELETE FROM players_positions 
WHERE player_id = :given_player AND position_id = :given_position

-- get team names, mascot, and field to populate the teams page
SELECT team_id, name, mascot, home_field 
FROM teams 

-- create a new team 
INSERT INTO teams (name, mascot, home_field)
VALUES (:team_name_input, :mascot_input, :home_field_input)

-- update team
UPDATE teams 
SET name = :team_name_input, mascot = :mascot_input, home_field = :home_field_input
WHERE team_id = :given_team

-- delete team 
DELETE FROM teams WHERE team_id = :given_team

-- get positions to populate the positions page
SELECT position_id, position
FROM positions 

-- create a new position
INSERT INTO positions (position_id, position)
VALUES (:position_id_input, :position_input)

-- update position 
UPDATE positions
SET position_id = :position_id_input, position = :position_input 
WHERE position_id = :given_position

-- delete position
DELETE FROM positions WHERE position_id = :given_position 

-- get trade id, trade description, and players received in the trade to populate the trades page
SELECT trades.trade_id, trades.comment AS description, teams.name AS 'TEAM', players.name as 'player received'
FROM players_received 
INNER JOIN players ON players.player_id = players_received.player_id 
INNER JOIN teams ON teams.team_id = players_received.team_id 
INNER JOIN trades ON trades.trade_id = players_received.trade_id
ORDER BY trades.trade_id ASC;

-- create trade
INSERT INTO trades (trade_date, comment) 
VALUES (:trade_date_input, :comment_input)

-- update trade 
UPDATE trades 
SET trade_date = :trade_date_input, comment = :comment_input
WHERE trade_id = :given_trade

-- delete trade 
DELETE FROM trades where trade_id = :given_trade

-- associate trade with teams and players (players_received) 
INSERT INTO players_received(trade_id, player_id, team_id)
VALUES 
(:given_trade, :given_player, :given_team)

-- remove from players_received
DELETE FROM players_received 
WHERE trade_id = :given_trade AND player_id = :given_player AND team_id = :given_team
