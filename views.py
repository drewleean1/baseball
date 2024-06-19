from flask import Flask, render_template, Blueprint, json, redirect, current_app, Blueprint, url_for, request, flash
from flask_mysqldb import MySQL
import sys
import os
import psycopg2
import psycopg2.extras
from psycopg2 import errors

UniqueViolation = errors.lookup('23505')

from app import db 

views = Blueprint('views', __name__)

#
#
#
#######     Navbar views for player/team/position/trade section
#
#
#

@views.route('/')
def home():
    return render_template('index.html')

@views.route('/teams', methods=['GET', 'POST'])
def teams():
    #code adapted from the flask starter app
    if request.method == "GET":
        query = "SELECT team_id, name, mascot, home_field FROM teams"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        data = cur.fetchall()
        
        return render_template("teams.j2", data=data)

    if request.method == 'POST': 
        if request.form.get('add_team'): 
            team_name_input = request.form['team_name_input']
            mascot_input = request.form['mascot_input']
            home_field_input = request.form['home_field_input']

            try: 
                query = 'INSERT INTO teams (name, mascot, home_field) VALUES (%s, %s, %s)'
                cur = db.cursor()
                cur.execute(query, (team_name_input, mascot_input, home_field_input,))
                db.commit()                
                flash('Team Successfully Added!', category='success')                
            
            except UniqueViolation as err:
                db.rollback()            
                flash('Team already exists, please enter a unique team.', category='error') 
                
            return redirect('/teams')
                

@views.route('/players', methods=['GET', 'POST'])
def players():
    if request.method == "GET":
        #JOIN to get player's team as well 
        query = "SELECT players.player_id, players.name, players.birthdate, players.batting, players.running, players.fielding, players.pitching, teams.name AS team FROM players JOIN teams on players.team_id = teams.team_id"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        data = cur.fetchall()

        query1 = "SELECT team_id, name FROM teams"
        cur.execute(query1)
        teams = cur.fetchall()
        
        return render_template("players.j2", data=data, teams=teams)

    if request.method == 'POST': 
        if request.form.get('add_player'): 
            
            player_name_input = request.form['player_name_input']
            birthdate_input = request.form['birthdate_input']
            batting_input = request.form['batting_input']
            fielding_input = request.form['fielding_input']
            running_input = request.form['running_input']
            pitching_input = request.form['pitching_input']
            team_input = request.form['team_input']

            try:
                query = 'INSERT INTO players (name, birthdate, batting, fielding, running, pitching, team_id) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(query, (player_name_input, birthdate_input, batting_input, fielding_input, running_input, pitching_input, team_input,))
                db.commit()
                flash('Player Successfully Added!', category='success')

            except UniqueViolation as err:
                db.rollback()            
                flash('Player already exists, please enter a unique player', category='error')

            return redirect('/players')


@views.route('/positions', methods=['GET', 'POST'])
def positions():
    #code adapted from the flask starter app
    if request.method == "GET":
        query = "SELECT position_id, position FROM positions"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        data = cur.fetchall()
        
        return render_template("positions.j2", data=data)

    if request.method == 'POST': 
        if request.form.get('add_position'): 
            position_id_input = request.form['position_id_input']
            position_input = request.form['position_input']

            try:
                query = 'INSERT INTO positions (position_id, position) VALUES (%s, %s)'
                cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(query, (position_id_input, position_input,))
                db.commit()
                flash('Successfully added position!', category='success')
            
            except UniqueViolation as err:
                db.rollback()            
                flash('Position already exists, please enter a unique position.', category='error')

            return redirect('/positions')

@views.route('/trades', methods=['GET', 'POST'])
def trades():
    if request.method == "GET":
        query = "SELECT trade_id, trade_date, comment FROM trades ORDER BY trade_date DESC"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        data = cur.fetchall()

        query1 = "SELECT team_id, name FROM teams"
        cur.execute(query1)
        teams = cur.fetchall()

        query2 = "SELECT player_id, name FROM players"
        cur.execute(query2)
        players = cur.fetchall()

        return render_template("trades.j2", data=data, teams=teams, players=players)

    if request.method == 'POST': 
        if request.form.get('add_trade'): 
            
            trade_date_input = request.form['trade_date_input']
            team1_input = request.form['team1_input']
            player1_input = request.form['player1_input']
            team2_input = request.form['team2_input']
            player2_input = request.form['player2_input']

            #queries to build the comment_input to insert into trades
            query1 = "SELECT name FROM teams WHERE team_id = (%s)"
            cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(query1, (team1_input,))
            team1 = cur.fetchall()

            cur.execute(query1, (team2_input,))
            team2 = cur.fetchall()

            query2 = "SELECT name FROM players WHERE player_id = (%s)"
            cur.execute(query2, (player1_input,))
            player1 = cur.fetchall()

            cur.execute(query2, (player2_input,))
            player2 = cur.fetchall()

            comment_input = 'The ' + team1[0]['name'] + ' trade ' + player1[0]['name']  + ' to the ' + team2[0]['name']  + ' for ' + player2[0]['name']  + '.'

            try: 
                query_trade = 'INSERT INTO trades (trade_date, comment) VALUES (%s, %s)'
                cur.execute(query_trade, (trade_date_input, comment_input,))
                db.commit()

                #query to get trade_id to insert into players_received
                query_trade_id = 'SELECT trade_id FROM trades WHERE comment = (%s)'
                cur.execute(query_trade_id, (comment_input,))
                trade_id = cur.fetchall()[0]['trade_id']

                query_pr = 'INSERT INTO players_received (player1_id, team1_id, player2_id, team2_id, trade_id) VALUES (%s, %s, %s, %s, %s)'
                cur.execute(query_pr, (player2_input, team1_input, player1_input, team2_input, trade_id,))
                db.commit()   

                #update traded players to new teams 
                trades = [
                    (player2_input, team1_input),
                    (player1_input, team2_input)
                ]

                query_player_update = 'UPDATE players SET team_id = %s WHERE player_id = %s'
                for trade in trades:
                    player_input, team_input = trade
                    cur.execute(query_player_update, (team_input, player_input,))
                    db.commit()         

                #flash successful trade message
                flash('Trade Successfully added!', category='success')
                
            except UniqueViolation as err:
                db.rollback()  
                flash('Trade already exists!', category='error')
            
            return redirect('/trades')

@views.route('/players_positions', methods=['GET', 'POST'])
def players_positions():
    #code adapted from the flask starter app
    if request.method == "GET":
        query = "SELECT players_positions.players_positions_id AS id, players.name, positions.position FROM players_positions INNER JOIN players ON players.player_id = players_positions.player_id INNER JOIN positions ON positions.position_id = players_positions.position_id"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        data = cur.fetchall()

        query1 = "SELECT player_id, name FROM players"
        cur.execute(query1)
        players = cur.fetchall()

        query2 = "SELECT position_id, position FROM positions"
        cur.execute(query2)
        positions = cur.fetchall()

        return render_template("players_positions.j2", data=data, players=players, positions=positions)

    if request.method == 'POST': 
        if request.form.get('associate'): 
            position_input = request.form['position_input']
            player_input = request.form['player_input']

            #protect against a player having multiple of the same position
            condition = True

            query_condition = "SELECT player_id FROM players_positions WHERE player_id = (%s) AND position_id =(%s)"
            cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(query_condition, (player_input, position_input,))
            data = cur.fetchall()

            if len(data) > 0: 
                condition = False

            if condition: 
                query = 'INSERT INTO players_positions (position_id, player_id) VALUES (%s, %s)'
                cur.execute(query, (position_input, player_input,))
                db.commit()
                flash("Players' Position added!", category='success')
            
            else: 
                flash("Position already attributed to player!", category='error')

            return redirect('/players_positions')

@views.route('/players_received')
def players_received():
    if request.method == "GET":
        query ='''
        SELECT players_received.players_received_id AS id, trades.trade_id, teams.name AS Team_1, players.name AS Player_1, t2.name AS Team_2, p2.name AS Player_2 
        FROM players_received 
        JOIN trades on trades.trade_id = players_received.trade_id 
        JOIN players on players.player_id = players_received.player1_id 
        JOIN teams on teams.team_id = players_received.team1_id 
        JOIN players AS p2 on p2.player_id = players_received.player2_id 
        JOIN teams AS t2 on t2.team_id = players_received.team2_id 
        ORDER BY id DESC
        '''
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        data = cur.fetchall()

        return render_template("players_received.j2", data=data)
#
#
#
#######     Edit player/team/position/trade section
#
#
#

@views.route('/edit_team/<id>', methods=['GET', 'POST'])
def edit_team(id):
    if request.method == "GET":
        query = "SELECT team_id, name, mascot, home_field FROM teams WHERE team_id = (%s)"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, (id,))
        data = cur.fetchall()

        return render_template("edit_team.j2", data=data)

    if request.method == 'POST': 
        if request.form.get('edit_team'): 
            team_name_input = request.form['team_name_input']
            mascot_input = request.form['mascot_input']
            home_field_input = request.form['home_field_input']

            try:  
                query = 'UPDATE teams SET name = %s, mascot = %s, home_field = %s WHERE team_id = %s'
                cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(query, (team_name_input, mascot_input, home_field_input, id,))
                db.connection.commit()
                flash('Team successfully edited!', category='success')
            
            except UniqueViolation as err:
                db.rollback()  
                flash('Team name already exists, please choose a unique name', category='error')

            return redirect('/teams')

@views.route('/edit_player/<id>', methods=['GET', 'POST'])
def edit_player(id):
    if request.method == "GET":
        query = "SELECT players.player_id, players.name, players.birthdate, players.batting, players.running, players.fielding, players.pitching, teams.name AS team FROM players JOIN teams on players.team_id = teams.team_id WHERE players.player_id = (%s)"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, (id,))
        data = cur.fetchall()

        query1 = "SELECT team_id, name FROM teams"
        cur.execute(query1)
        teams = cur.fetchall()

        return render_template("edit_player.j2", data=data, teams=teams)
    
    if request.method == 'POST': 
        if request.form.get('edit_player'): 
            
            player_name_input = request.form['player_name_input']
            birthdate_input = request.form['birthdate_input']
            batting_input = request.form['batting_input']
            fielding_input = request.form['fielding_input']
            running_input = request.form['running_input']
            pitching_input = request.form['pitching_input']
            team_input = request.form['team_id_input']

            try: 
                query = 'UPDATE players SET name = %s, birthdate = %s, batting = %s, fielding = %s, running = %s, pitching = %s, team_id = %s WHERE player_id = %s'
                cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(query, (player_name_input, birthdate_input, batting_input, fielding_input, running_input, pitching_input, team_input, id,))
                db.commit()
                flash('Player successfully edited!', category='success')
            
            except UniqueViolation as err:
                db.rollback()  
                flash('Player name already exists, please choose a unique name', category='error')

            return redirect('/players')

@views.route('/edit_trade/<id>', methods=['GET', 'POST'])
def edit_trade(id):
    if request.method == "GET":
        query = "SELECT trade_id, trade_date, comment FROM trades WHERE trade_id = (%s)"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, (id,))
        data = cur.fetchall()

        #we have to reverse the players receieved so we can do the appropriate trade.
        query1 ='''
        SELECT teams.name AS Team_1, players.name AS Player_2, t2.name AS Team_2, p2.name AS Player_1 
        FROM players_received 
        JOIN trades on trades.trade_id = players_received.trade_id 
        JOIN players on players.player_id = players_received.player1_id 
        JOIN teams on teams.team_id = players_received.team1_id 
        JOIN players AS p2 on p2.player_id = players_received.player2_id 
        JOIN teams AS t2 on t2.team_id = players_received.team2_id 
        WHERE trades.trade_id = (%s)
        '''
        cur.execute(query1, (id,))
        players_received = cur.fetchall()

        query2 = "SELECT team_id, name FROM teams"
        cur.execute(query2)
        teams = cur.fetchall()

        query3 = "SELECT player_id, name FROM players"
        cur.execute(query3)
        players = cur.fetchall()

        return render_template("edit_trade.j2", data=data, pr=players_received, teams=teams, players=players)
    
    if request.method == 'POST': 
        if request.form.get('edit_trade'): 
            
            trade_date_input = request.form['trade_date_input']
            team1_input = request.form['team1_input']
            player1_input = request.form['player1_input']
            team2_input = request.form['team2_input']
            player2_input = request.form['player2_input']

            #queries to build the comment_input to insert into trades
            query1 = "SELECT name FROM teams WHERE team_id = (%s)"
            cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(query1, (team1_input,))
            team1 = cur.fetchall()

            cur.execute(query1, (team2_input,))
            team2 = cur.fetchall()

            query2 = "SELECT name FROM players WHERE player_id = (%s)"
            cur.execute(query2, (player1_input,))
            player1 = cur.fetchall()

            cur.execute(query2, (player2_input,))
            player2 = cur.fetchall()

            comment_input = 'The ' + team1[0]['name'] + ' trade ' + player1[0]['name']  + ' to the ' + team2[0]['name']  + ' for ' + player2[0]['name']  + '.'

            try:
                #edit the trade 
                query3 = 'UPDATE trades SET trade_date = %s, comment = %s WHERE trade_id =%s'
                cur.execute(query3, (trade_date_input, comment_input, id,))
                db.commit()

                #edit the players_received table
                query4 = 'UPDATE players_received SET player1_id = %s, team1_id = %s, player2_id = %s, team2_id = %s WHERE trade_id = %s'
                cur.execute(query4, (player2_input, team1_input, player1_input, team2_input, id,))
                db.commit()

                #update traded players to new teams 
                trades = [
                    (player2_input, team1_input),
                    (player1_input, team2_input)
                ]

                query_player_update = 'UPDATE players SET team_id = %s WHERE player_id = %s'
                for trade in trades:
                    player_input, team_input = trade
                    cur.execute(query_player_update, (team_input, player_input,))
                    db.commit()   

            except UniqueViolation as err:
                db.rollback()  
                flash('Trade already exists!', category='error')

            return redirect('/trades')

@views.route('/edit_position/<id>', methods=['GET', 'POST'])
def edit_position(id):
    if request.method == "GET":
        query = "SELECT position_id, position FROM positions WHERE position_id = (%s)"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, (id,))
        data = cur.fetchall()

        return render_template("edit_position.j2", data=data)

    if request.method == 'POST': 
        if request.form.get('edit_position'): 
            position_id_input = request.form['position_id_input']
            position_input = request.form['position_input']

            #protection against two positions with either the same ID or name
            condition = True

            query_condition = "SELECT position FROM positions WHERE position_id = (%s)"
            cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(query_condition, (position_id_input,))
            data = cur.fetchall()

            query_condition2 = "SELECT position FROM positions WHERE position = (%s)"
            cur.execute(query_condition2, (position_input,))
            data2 = cur.fetchall()

            if len(data) > 0 or len(data2)>0: 
                condition = False 

            if condition: 
                query = 'UPDATE positions SET position_id = %s, position = %s WHERE position_id = (%s)'
                cur.execute(query, (position_id_input, position_input, id,))
                db.commit()
                flash('Position Successfully edited!', category='success')
            
            else: 
                flash('Position already exists.')

            return redirect('/positions')

@views.route('/edit_players_position/<id>', methods=['GET', 'POST'])
def edit_players_position(id):
    if request.method == "GET":
        query = "SELECT players_positions.players_positions_id AS id, players.name, positions.position FROM players_positions INNER JOIN players ON players.player_id = players_positions.player_id INNER JOIN positions ON positions.position_id = players_positions.position_id WHERE players_positions_id = (%s)"
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, (id,))
        data = cur.fetchall()

        query1 = "SELECT player_id, name FROM players"
        cur.execute(query1)
        players = cur.fetchall()

        query2 = "SELECT position_id, position FROM positions"
        cur.execute(query2)
        positions = cur.fetchall()

        return render_template("edit_players_position.j2", data=data, players=players, positions=positions)

    if request.method == 'POST': 
        if request.form.get('edit_players_position'): 
            player_input = request.form['player_input']
            position_input = request.form['position_input']

            #protect against a player having multiple of the same position
            condition = True

            query_condition = "SELECT player_id FROM players_positions WHERE player_id = (%s) AND position_id =(%s)"
            cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(query_condition, (player_input, position_input,))
            data = cur.fetchall()

            if len(data) > 0: 
                condition = False 

            if condition: 
                query = 'UPDATE players_positions SET player_id = %s, position_id = %s WHERE players_positions_id = %s'
                cur.execute(query, (player_input, position_input, id,))
                db.commit()
                flash("Players' Position successfully edited!", category='success')
                            
            else: 
                flash('Player already has that position.', category='error')

            return redirect('/players_positions')

#
#
#
#######     Delete player/team/position/trade section
#
#
#

@views.route('/delete_player/<id>', methods = ['GET', 'POST'])
def delete_player(id):
    query = 'DELETE FROM players WHERE player_id = (%s)'
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, (id,))
    db.commit()
    flash('Player successfully deleted!', category='success')
    return redirect('/players')

@views.route('/delete_team/<id>', methods=['GET', 'POST'])
def delete_team(id):
    query = 'DELETE FROM teams WHERE team_id = (%s)'
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, (id,))
    db.commit()
    flash('Team successfully deleted!', category='success')
    return redirect('/teams')

@views.route('/delete_position/<id>', methods=['GET', 'POST'])
def delete_position(id):
    query = 'DELETE FROM positions WHERE position_id = (%s)'
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, (id,))
    db.commit()
    flash('Position successfully deleted!', category='success')
    return redirect('/positions')

@views.route('/delete_trade/<id>', methods=['GET', 'POST'])
def delete_trade(id):
    query = 'SELECT player1_id, team1_id, player2_id, team2_id FROM players_received WHERE trade_id = (%s)'
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, (id,))
    data = cur.fetchall()

    #return players to their teams
    query = 'UPDATE players SET team_id = %s WHERE player_id = %s'
    cur.execute(query, (data[0]['team2_id'], data[0]['player1_id'],))
    db.commit()

    query = 'UPDATE players SET team_id = %s WHERE player_id = %s'
    cur.execute(query, (data[0]['team1_id'], data[0]['player2_id'],))
    db.commit()

    #delete players_received
    query = 'DELETE FROM players_received WHERE trade_id = (%s)'
    cur.execute(query, (id,))
    db.commit()

    query = 'DELETE FROM trades WHERE trade_id = (%s)'
    cur.execute(query, (id,))
    db.commit()
    flash('Trade successfully deleted!', category='success')
    return redirect('/trades')

@views.route('/delete_players_position/<id>', methods=['GET', 'POST'])
def delete_players_position(id):
    query = 'DELETE FROM players_positions WHERE players_positions_id = (%s)'
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, (id,))
    db.commit()
    flash("Players' Position successfully deleted!", category='success')
    return redirect('/players_positions')
