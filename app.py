# app.py
from flask import Flask, render_template, request, redirect, url_for, flash , jsonify
import db_manager # Import the separated database logic
import os
from dotenv import load_dotenv
from forms import *



app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get('FLASK_SECRET_KEY') 

# --- FLASK ROUTES ---

#-------------------------------INDEX/HOME------------------------------------------------------------------

@app.route('/')
def index():
    tournaments = db_manager.get_all_tournaments()
    return render_template('index.html', tournaments=tournaments)


#------------------------------CREATE/ADD---------------------------------------------------------------

@app.route('/tournament/create', methods=['GET', 'POST'])
def new_tourn_route():

    if request.method == 'POST':
        name = request.form['name']
        status = request.form['status']
        type_str = request.form['type']
        
        if name and status and type_str in ['solo', 'teamed']:
            db_manager.new_tournament(name, status, type_str)
            flash(f'Tournament "{name}" created successfully!', 'success')
        else:
            flash('Invalid input for new tournament.', 'error')
            
        return redirect(url_for('index'))
    return render_template('new_tournament.html')


@app.route('/tournament/<tourn_id>/new_team', methods=['POST'])
def add_team_route(tourn_id):
    tourn_data = db_manager.get_tournament_by_id(tourn_id)
    if not tourn_data or tourn_data.get('type') != 'teamed':
        flash('Tournament not found or is not a "teamed" tournament.', 'error')
        return redirect(url_for('index'))
        


    addteamform = AddTeamForm()
    if addteamform.validate_on_submit():
        try:
            data = {'name': addteamform.name.data, 'score' : addteamform.score.data, 'reg-time' : db_manager.firestore.firestore.SERVER_TIMESTAMP}
            db_manager.add_team_to_tournament(tourn_id,data)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': f'DB Error: {str(e)}'}), 500
    else:
        errors = {field: errors for field, errors in addteamform.errors.items()}
        return jsonify({'success': False, 'errors': errors}), 400
    
@app.route('/tournament/<tourn_id>/new_team/add', methods=['GET'])
def getnewteam(tourn_id):
    tourn_data = db_manager.get_tournament_by_id(tourn_id)
    form = AddTeamForm()
    return render_template('add_team_modal.html', 
                           tourn_id=tourn_id, 
                           tourn_data=tourn_data, 
                           form=form)

@app.route('/tournament/<tourn_id>/new_player', methods=['POST'])
def add_player_route(tourn_id):
    """Route for adding a team to a tournament."""
    tourn_data = db_manager.get_tournament_by_id(tourn_id)
    if not tourn_data or tourn_data.get('type') != 'solo':
        flash('Tournament not found or is not a "solo" tournament.', 'error')
        return redirect(url_for('index'))

    addplayerform = AddPlayerForm()
    if addplayerform.validate_on_submit():
        try:
            data = {'name': addplayerform.name.data, 'score' : addplayerform.score.data, 'reg-time' : db_manager.firestore.firestore.SERVER_TIMESTAMP}
            db_manager.addplayer(tourn_id,data)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': f'DB Error: {str(e)}'}), 500
    else:
        errors = {field: errors for field, errors in addplayerform.errors.items()}
        return jsonify({'success': False, 'errors': errors}), 400
    
@app.route('/tournament/<tourn_id>/new_player/add', methods=['GET'])
def getnewplayer(tourn_id):
    tourn_data = db_manager.get_tournament_by_id(tourn_id)
    form = AddPlayerForm()
    return render_template('add_player_modal.html', 
                           tourn_id=tourn_id, 
                           tourn_data=tourn_data, 
                           form=form)


#-----------------------------EDIT/UPDATE------------------------------------------------------------------

@app.route('/tournament/<tourn_id>/<team_id>/edit/', methods=['POST'])
def edit_team(tourn_id,team_id):
    tourn_name, info = db_manager.team_info(tourn_id)
    data = db_manager.get_team_by_id(team_id,tourn_id)
    
    if tourn_name == "Tournament not found":
        flash(f'Tournament ID {tourn_id} not found.', 'error')
        return redirect(url_for('index'))
  

    editteamform = EditTeamForm(data=data)
    if editteamform.validate_on_submit():
        try:
            newdata = {'name': editteamform.name.data, 'score' : editteamform.score.data}
            db_manager.editteam(team_id,tourn_id,newdata)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': f'DB Error: {str(e)}'}), 500
    else:
        errors = {field: errors for field, errors in editteamform.errors.items()}
        return jsonify({'success': False, 'errors': errors}), 400


@app.route('/tournament/<tourn_id>/<team_id>/edit/modal', methods=['GET'])
def geteditteam(tourn_id, team_id):
    tourn_name = db_manager.get_tournament_by_id(tourn_id)['name']
    data = db_manager.get_team_by_id(team_id,tourn_id)

    if not data:
        return jsonify({'error':'Team not found'}), 404
    
    data['name'] = data['name'].strip()
    editteamform = EditTeamForm(data=data)

    return render_template('edit_team_modal.html',
                           tourn_id = tourn_id,
                           tourn_name = tourn_name,
                           data = data,
                           form = editteamform
                           )


@app.route('/tournament/<tourn_id>/<player_id>/edit', methods=['POST'])
def edit_player(tourn_id,player_id):
    data = db_manager.get_player_by_id(player_id,tourn_id)
    tourn_name = db_manager.get_tournament_by_id(tourn_id)['name']

    if tourn_name == "Tournament not found":
        flash(f'Tournament ID {tourn_id} not found.', 'error')
        return redirect(url_for('index'))

    editplayerform = EditPlayerForm(data=data)
    if editplayerform.validate_on_submit():
        try:
            newdata = {'name': editplayerform.name.data, 'score' : editplayerform.score.data}
            db_manager.editplayer(player_id,tourn_id,newdata)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': f'DB Error: {str(e)}'}), 500
    else:
        errors = {field: errors for field, errors in editplayerform.errors.items()}
        return jsonify({'success': False, 'errors': errors}), 400


@app.route('/tournament/<tourn_id>/<player_id>/edit/modal', methods=['GET'])
def geteditplayer(tourn_id, player_id):
    tourn_name = db_manager.get_tournament_by_id(tourn_id)['name']
    data = db_manager.get_player_by_id(player_id,tourn_id)

    if not data:
        return jsonify({'error':'Team not found'}), 404
    
    data['name'] = data['name'].strip()
    form = EditPlayerForm(data=data)

    return render_template('edit_player_modal.html',
                           tourn_id = tourn_id,
                           tourn_name = tourn_name,
                           data = data,
                           form = form
                           )


@app.route('/tournament/<tourn_id>/update', methods=['GET', 'POST'])
def update_tourn_route(tourn_id):
    """Route for updating an existing tournament."""
    tourn_data = db_manager.get_tournament_by_id(tourn_id)
    
    if not tourn_data:
        flash(f'Tournament ID {tourn_id} not found.', 'error')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        new_data = {}
        new_name = request.form['name']
        new_status = request.form['status']
        
        if new_name and new_name != tourn_data.get('name'):
            new_data['name'] = new_name
        if new_status and new_status != tourn_data.get('status'):
            new_data['status'] = new_status
            
        if new_data:
            db_manager.update_tournament(tourn_id, new_data)
            flash(f'Tournament "{new_name or tourn_data["name"]}" updated successfully!', 'success')
        else:
            flash('No changes detected for update.', 'info')
            
        return redirect(url_for('index'))
        
    return render_template('update_tournament.html', tournament=tourn_data)


#----------------------------------DELETE/REMOVE---------------------------------------------------------


@app.route('/tournament/<tourn_id>/<team_id>delete', methods=['POST'])
def del_team(team_id,tourn_id):
    
    db_manager.delteam(team_id,tourn_id)
    return redirect(url_for('view_tournament',tourn_id=tourn_id))    

@app.route('/tournament/<tourn_id>/<player_id>/delete', methods=['POST'])
def del_player(player_id,tourn_id):
    
    db_manager.delplayer(player_id,tourn_id)
    return redirect(url_for('view_tournament',tourn_id=tourn_id))    

# --- DELETE Tournament ---
@app.route('/tournament/<tourn_id>/delete', methods=['POST'])
def delete_tourn_route(tourn_id):
    """Deletes a tournament."""
    tourn_data = db_manager.get_tournament_by_id(tourn_id)
    if tourn_data:
        db_manager.delete_tournament(tourn_id)
        flash(f'Tournament "{tourn_data["name"]}" deleted successfully.', 'success')
    else:
        flash(f'Tournament ID {tourn_id} not found.', 'error')
        
    return redirect(url_for('index'))

# --- CREATE Team ---


#-----------------------------READINGS/PAIRINGS/STANDINGS-------------------------------------------------------

@app.route('/tournament/<tourn_id>')
def view_tournament(tourn_id):
    tourn_type = db_manager.get_tournament_by_id(tourn_id)['type']
    tourn_name = db_manager.get_tournament_by_id(tourn_id)['name']
    if tourn_name == "Tournament not found":
        flash(f'Tournament ID {tourn_id} not found.', 'error')
        return redirect(url_for('index'))

    if tourn_type == 'solo':
        tourn_name, info = db_manager.player_info(tourn_id)
        return render_template('view_tournament.html',
                               tourn_id = tourn_id,
                               tourn_name = tourn_name,
                               tourn_type = tourn_type,
                               info = info)
    else:
        tourn_name, info = db_manager.team_info(tourn_id)
        return render_template('view_tournament.html',
                               tourn_id = tourn_id,
                               tourn_name = tourn_name,
                               tourn_type = tourn_type,
                               info = info)


@app.route('/tournament/<tourn_id>/standings')
def standings_route(tourn_id):
    """Route for displaying tournament standings."""
    tourn_name, standings = db_manager.get_standings(tourn_id)
    for t in standings : team_id = t['id']
    if tourn_name == "Tournament not found":
        flash(f'Tournament ID {tourn_id} not found.', 'error')
        return redirect(url_for('index'))
    

    return render_template('standings.html', 
                           tourn_name=tourn_name, 
                           tourn_id=tourn_id,
                           standings=standings,
                           )

if __name__ == '__main__':
    app.run(debug=True)