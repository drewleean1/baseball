-- Andrew Lee (leea6@oregonstate.edu)
-- Anthony Lomax (lomaxan@oregonstate.edu)
-- Project 29: data(Baseball)


CREATE TABLE teams (
	team_id SERIAL PRIMARY KEY, 
	name text UNIQUE NOT NULL, 
	mascot text NOT NULL, 
	home_field text NOT NULL 
);

CREATE TABLE players (
	player_id SERIAL PRIMARY KEY, 
	name text UNIQUE NOT NULL, 
	birthdate DATE NOT NULL,
	batting int NOT NULL,
	running int NOT NULL, 
	fielding int NOT NULL, 
	pitching int NOT NULL, 
	team_id int, 
	FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE positions (
	position_id int UNIQUE NOT NULL PRIMARY KEY,     
	position varchar(45) NOT NULL
);

-- an intersection table that allows the M:N relationship between players and positions

CREATE TABLE players_position (
	player_id int, 
	position_id int, 
	FOREIGN KEY (player_id) REFERENCES players(player_id),
	FOREIGN KEY (position_id) REFERENCES positions(position_id)
);

CREATE TABLE trades (
	trade_id SERIAL PRIMARY KEY, 
	trade_date DATE NOT NULL, 
	comment text UNIQUE NOT NULL
);

-- player_received is an  intersection table between trades, players, and teams
-- they allow us to see which team received which player in a trade
-- due to a trade requiring at least two teams and most often two players, this means that each trade will have two of each of the tables below

CREATE TABLE players_received (
	players_received_id SERIAL PRIMARY KEY, 
	player1_id int, 
	team1_id int,
	player2_id int, 
	team2_id int, 		
	trade_id int, 
	FOREIGN KEY (player1_id) REFERENCES players(player_id),
	FOREIGN KEY (team1_id) REFERENCES teams(team_id),
	FOREIGN KEY (player2_id) REFERENCES players(player_id),
	FOREIGN KEY (team_id) REFERENCES teams(team_id),
	FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
);

/* INSERT QUERIES BELOW */

INSERT INTO teams (name, mascot, home_field)
VALUES ('Dry Pumpkins', 'Perry the Pumpkin', 'Pumpkin Field'), 
('Wet Vipers', 'Waldo the Viper', 'Snake Pit'), 
('Thunder Clappers', 'Than the Clapper', 'Lightning Dome');

-- insert players using team_id foreign key 
INSERT INTO players (name, birthdate, batting, running, fielding, pitching, team_id)
VALUES 
('Clay', '2013-03-27', 8, 3, 5, 5, (SELECT team_id FROM teams WHERE teams.name = 'Dry Pumpkins')),
('Nestor', '2014-12-10', 1, 1, 4, 8, (SELECT team_id FROM teams WHERE teams.name = 'Dry Pumpkins')),
('Julio', '2016-12-29', 8, 9, 5, 1, (SELECT team_id FROM teams WHERE teams.name = 'Wet Vipers')),
('Josh', '2014-06-30', 5, 7, 8, 3,(SELECT team_id FROM teams WHERE teams.name = 'Wet Vipers')),
('Willy', '2015-09-02', 6, 7, 6, 4,(SELECT team_id FROM teams WHERE teams.name = 'Wet Vipers')),
('Peter', '2012-12-24', 6, 2, 9, 2, (SELECT team_id FROM teams WHERE teams.name = 'Wet Vipers')),
('Freddie', '2012-09-12', 9,3, 5, 6, (SELECT team_id FROM teams WHERE teams.name = 'Thunder Clappers')),
('Shohei', '2014-07-05', 9, 8, 3, 9, (SELECT team_id FROM teams WHERE teams.name = 'Thunder Clappers'));

-- each position has a predetermined id
INSERT INTO positions (position_id, position)
VALUES
(1, 'Starting Pitcher'),
(2, 'Catcher'),
(3, 'First Base'),
(4, 'Second Base'),
(5, 'Third Base'),
(6, 'Shortstop'),
(7, 'Left Field'),
(8, 'Center Field'),
(9, 'Right Field');

-- insert into the intersection table, player_id foreign key, and then we know what each position's id is
INSERT INTO players_position (player_id, position_id)
VALUES 
((SELECT player_id FROM players WHERE players.name = 'Clay'), 9),
((SELECT player_id FROM players WHERE players.name = 'Nestor'), 1),
((SELECT player_id FROM players WHERE players.name = 'Julio'), 7),
((SELECT player_id FROM players WHERE players.name = 'Josh'), 4),
((SELECT player_id FROM players WHERE players.name = 'Josh'), 5),
((SELECT player_id FROM players WHERE players.name = 'Willy'), 6),
((SELECT player_id FROM players WHERE players.name = 'Peter'), 2),
((SELECT player_id FROM players WHERE players.name = 'Freddie'), 3),
((SELECT player_id FROM players WHERE players.name = 'Shohei'), 8),
((SELECT player_id FROM players WHERE players.name = 'Shohei'), 1);

/*For trades, we are imagining that teams are trading players to get to the status quo.
For example, Julio Rodriguez is a Mariner. To facilitate that, we are having the Yankees trade him to the Mariners.*/

-- Trade between the Dry Pumpkins and Wet Vipers
INSERT INTO trades (trade_date, comment)
VALUES ('2024-05-01', 'The Dry Pumpkins trade Julio to the Wet Vipers for Nestor.');

-- Wet Vipers receive Julio
INSERT INTO players_received (player_id, team_id, trade_id)
VALUES
((SELECT player_id FROM players WHERE players.name = 'Julio'),
(SELECT team_id FROM teams WHERE teams.name = 'Wet Vipers'),
(SELECT trade_id FROM trades WHERE trades.comment = 'The Dry Pumpkins trade Julio to the Wet Vipers for Nestor.'));

-- Dry Pumpkins receive Nestor
INSERT INTO players_received (player_id, team_id, trade_id)
VALUES
((SELECT player_id FROM players WHERE players.name = 'Nestor'),
(SELECT team_id FROM teams WHERE teams.name = 'Dry Pumpkins'),
(SELECT trade_id FROM trades WHERE trades.comment = 'The Dry Pumpkins trade Julio to the Wet Vipers for Nestor.'));

-- Trade between Wet Vipers and Thunder Clappers 
INSERT INTO trades (trade_date, comment)
VALUES ('2024-05-01', 'The Thunder Clappers trade Willy to the Wet Vipers for Freddie.');

-- Thunder Clappers receive Freddie
INSERT INTO players_received (player_id, team_id, trade_id)
VALUES
((SELECT player_id FROM players WHERE players.name = 'Freddie'),
(SELECT team_id FROM teams WHERE teams.name = 'Thunder Clappers'),
(SELECT trade_id FROM trades WHERE trades.comment = 'The Thunder Clappers trade Willy to the Wet Vipers for Freddie.'));

-- Wet Vipers receive Willy
INSERT INTO players_received (player_id, team_id, trade_id)
VALUES
((SELECT player_id FROM players WHERE players.name = 'Willy'),
(SELECT team_id FROM teams WHERE teams.name = 'Wet Vipers'),
(SELECT trade_id FROM trades WHERE trades.comment = 'The Thunder Clappers trade Willy to the Wet Vipers for Freddie.'));

-- Trade between Thunder Clappers and Wet Vipers 
INSERT INTO trades (trade_date, comment)
VALUES ('2024-05-01', 'The Thunder Clappers trade Josh to the Wet Vipers for Shohei.');

-- Thunder Clappers receive Shohei
INSERT INTO players_received (player_id, team_id, trade_id)
VALUES
((SELECT player_id FROM players WHERE players.name = 'Shohei'),
(SELECT team_id FROM teams WHERE teams.name = 'Thunder Clappers'),
(SELECT trade_id FROM trades WHERE trades.comment = 'The Thunder Clappers trade Josh to the Wet Vipers for Shohei.'));

-- Wet Vipers receive Josh
INSERT INTO players_received (player_id, team_id, trade_id)
VALUES
((SELECT player_id FROM players WHERE players.name = 'Josh'),
(SELECT team_id FROM teams WHERE teams.name = 'Wet Vipers'),
(SELECT trade_id FROM trades WHERE trades.comment = 'The Thunder Clappers trade Josh to the Wet Vipers for Shohei.'));


SET FOREIGN_KEY_CHECKS=1;
COMMIT;
