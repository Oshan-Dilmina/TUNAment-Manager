# db_manager.py
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- FIREBASE SETUP (Centralized) ---
try:
    cred_path = 'tournament-mgr-caf10-firebase-adminsdk-fbsvc-9e0b266b27.json'
    if not os.path.exists(cred_path):
        # Raise an exception if the key file is missing
        raise FileNotFoundError(f"Service account key not found at {cred_path}")
        
    cred = credentials.Certificate(cred_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    tref = db.collection('tournament')
    print(" + Firebase initialized successfully in db_manager.")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    db = None
    tref = None

# --- CORE DB FUNCTIONS --- 

def get_all_tournaments():
    """Fetches all tournaments with their ID, name, status, and type."""
    if tref is None: return []
    tlist_data = []
    for doc in tref.stream():
        data = doc.to_dict()
        tlist_data.append({
            'id': doc.id,
            'name': data.get('name', 'Unnamed Tournament'),
            'type': data.get('type', 'solo'),
            'status': data.get('status', 'Open'),
            'reg_time': data.get('reg-time', 'N/A')
        })
    return tlist_data

def get_tournament_by_id(tourn_id):
    if tref is None: return None
    doc = tref.document(tourn_id).get()
    if doc.exists:
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    # Change: return this dict so app.py doesn't break
    return {'name': "Tournament not found", 'type': 'solo'}

def get_tournament_round_count(tourn_id):
    if tref is None: return None
    doc = tref.document(tourn_id).get()
    if doc.exists:
        data = doc.to_dict()

    return data['round_count']

def new_tournament(name, status, type_str):
    """Creates a new tournament document."""
    if tref is None: return
    info = {'name': name, 'status': status, 'reg-time': firestore.firestore.SERVER_TIMESTAMP, 'type': type_str, 'round_count' : 0}
    tref.add(info)

def update_tournament(tourn_id, new_data):
    """Updates fields of an existing tournament."""
    if tref is None: return
    if new_data:
        tref.document(tourn_id).update(new_data)

def delete_tournament(tourn_id):
    """Deletes a tournament document."""
    if tref is None: return
    tref.document(tourn_id).delete()

def add_team_to_tournament(tourn_id, data=dict):
    """Adds a new team to a 'teamed' tournament."""
    if tref is None: return
    tref.document(tourn_id).collection('teams').add(data)

def get_teams_for_tournament(tourn_id):
    """Gets all teams for a teamed tournament."""
    if tref is None: return []
    teams_list = []
    teams_ref = tref.document(tourn_id).collection('teams')
    for doc in teams_ref.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        teams_list.append(data)
    return teams_list

def get_team_by_id(team_id,tourn_id):
    """Fetches a single tournament document."""
    if tref is None: return None
    doc = tref.document(tourn_id).collection('teams').document(team_id).get()
    if doc.exists:
        data = doc.to_dict()
        data['id'] = doc.id
        
        return data
        
    return None


def get_standings(tourn_id):
    """Calculates and returns sorted standings (players or teams)."""
    tourn_data = get_tournament_by_id(tourn_id)
    if not tourn_data:
        return "Tournament not found", []

    tourn_name = tourn_data.get('name', 'Unnamed Tournament')
    tourn_type = tourn_data.get('type', 'solo')
    
    standings = []
    
    if tourn_type == 'solo':
        # Get players
        players_ref = tref.document(tourn_id).collection('players')
        for doc in players_ref.stream():
            data = doc.to_dict()
            standings.append({
                'name': data.get('name', 'N/A Player'), 
                'score': data.get('score', 0), 
                'id': doc.id
            })
            
    elif tourn_type == 'teamed':
        # Get teams
        teams_ref = tref.document(tourn_id).collection('teams')
        for doc in teams_ref.stream():
            data = doc.to_dict()
            standings.append({
                'name': data.get('name', 'N/A Team'), 
                'score': data.get('score', 0), 
                'id' : doc.id
            })
        
    # Sort the results by score (descending)
    standings.sort(key=lambda x: x['score'], reverse=True)
    
    return tourn_name, standings

def team_info(tourn_id):
    tourn_data = get_tournament_by_id(tourn_id)
    if not tourn_data:
        return "Tournament not found", []

    tourn_name = tourn_data.get('name', 'Unnamed Tournament')
    tourn_type = tourn_data.get('type', 'solo')
    
    info = []

    if tourn_type == 'teamed':
        # Get teams
        teams_ref = tref.document(tourn_id).collection('teams')
        for doc in teams_ref.stream():
            data = doc.to_dict()
            info.append({
                'name': data.get('name', 'N/A Team'), 
                'score': data.get('score', 0),
                'id' : doc.id
            })
        
    # Sort the results by score (descending)
    
    return tourn_name, info

def delteam(team_id,tourn_id):
    tref.document(tourn_id).collection('teams').document(team_id).delete()

def editteam(team_id,tourn_id,data):
    tref.document(tourn_id).collection('teams').document(team_id).update(data)



def addplayer(tourn_id,data):
    tref.document(tourn_id).collection('players').add(data)

def editplayer(player_id,tourn_id,data):
    tref.document(tourn_id).collection('players').document(player_id).update(data)

def delplayer(player_id,tourn_id):
    tref.document(tourn_id).collection('players').document(player_id).delete()

def player_info(tourn_id):
    tourn_data = get_tournament_by_id(tourn_id)
    if not tourn_data or tourn_data.get('name') == "Tournament not found":
        return "Tournament not found", []

    tourn_name = tourn_data.get('name', 'Unnamed Tournament')
    
    info = []
    # Make sure you are pulling from 'players' collection
    players_ref = tref.document(tourn_id).collection('players')
    for doc in players_ref.stream():
        data = doc.to_dict()
        info.append({
            'name': data.get('name', 'N/A Player'), # Fixed label
            'score': data.get('score', 0),
            'id' : doc.id
        })
    return tourn_name, info

def get_player_by_id(player_id,tourn_id):
    if tref is None: return None
    doc = tref.document(tourn_id).collection('players').document(player_id).get()
    if doc.exists:
        data = doc.to_dict()
        data['id'] = doc.id
        
        return data
        
    return None

def get_players_alphabetical(tourn_id):
    players_ref = tref.document(tourn_id).collection('players')
    players = []
    for doc in players_ref.stream():
        data = doc.to_dict()
        data['id'] = doc.id
        players.append(data)
    return sorted(players, key=lambda x: x['name'])

def save_matches(tourn_id, round_number, matches):
    round_ref = tref.document(tourn_id).collection('rounds').document(f'round_{round_number}')
    round_ref.set({
        'round_number': round_number,
        'matches': matches,
        'status': 'in_progress'
    })