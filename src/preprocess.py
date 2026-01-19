import pandas as pd
import os
import numpy as np

def load_all_data(data_folder="data"):
    """Charge tous les CSV et retourne un dictionnaire"""
    files = {
        'players': 'players.csv',
        'games': 'games.csv',
        'appearances': 'appearances.csv',
        'game_lineups': 'game_lineups.csv',
        'game_events': 'game_events.csv',
        'clubs': 'clubs.csv',
        'club_games': 'club_games.csv',
        'competitions': 'competitions.csv',
        'player_valuations': 'player_valuations.csv'
    }
    
    data = {}
    for key, filename in files.items():
        path = os.path.join(data_folder, filename)
        if os.path.exists(path):
            data[key] = pd.read_csv(path)
            print(f"Chargé {filename} -> {len(data[key]):,} lignes")
        else:
            raise FileNotFoundError(f"Fichier manquant : {path}")
    return data

def create_player_stats_df(data):
    """Crée un DataFrame enrichi avec toutes les stats agrégées par joueur"""
    app = data['appearances'].copy()
    players = data['players'].copy()
    
    stats = app.groupby('player_id').agg({
        'goals': 'sum',
        'assists': 'sum',
        'minutes_played': 'sum',
        'yellow_cards': 'sum',
        'red_cards': 'sum',
        'game_id': 'count'
    }).reset_index()
    
    stats = stats.rename(columns={'game_id': 'games_played'})
    
    stats['goals_per_game'] = stats['goals'] / stats['games_played']
    stats['assists_per_game'] = stats['assists'] / stats['games_played']
    stats['minutes_per_game'] = stats['minutes_played'] / stats['games_played']
    
    stats = stats.fillna(0)
    
    df = stats.merge(players[['player_id', 'name', 'current_club_id', 'position', 'sub_position', 
                              'foot', 'height_in_cm', 'market_value_in_eur', 'country_of_citizenship', 'image_url']], 
                     on='player_id', how='left')
    
    df = df[df['games_played'] >= 5].copy().reset_index(drop=True)
    
    return df

def create_team_history_df(data, data_folder="data"):
    """Génère team_history.csv pour les prédictions Prophet"""
    games = data['games'].copy()
    club_games = data['club_games'].copy()
    clubs = data['clubs'].copy()
    
    home = club_games[['game_id', 'club_id', 'own_goals']].rename(columns={'own_goals': 'goals'})
    away = club_games[['game_id', 'club_id', 'opponent_goals']].rename(columns={'opponent_goals': 'goals'})
    
    home['is_home'] = True
    away['is_home'] = False
    
    all_goals = pd.concat([home, away], ignore_index=True)
    
    all_goals = all_goals.merge(games[['game_id', 'date', 'home_club_id', 'away_club_id']], on='game_id')
    
    all_goals['team_id'] = np.where(all_goals['is_home'], all_goals['home_club_id'], all_goals['away_club_id'])
    all_goals = all_goals[['date', 'team_id', 'goals']]
    
    team_history = all_goals.groupby(['date', 'team_id'])['goals'].sum().reset_index()
    team_history = team_history.merge(clubs[['club_id', 'name']], left_on='team_id', right_on='club_id')
    team_history = team_history[['date', 'name', 'goals']].rename(columns={'name': 'team_name'})
    team_history['date'] = pd.to_datetime(team_history['date'])
    
    team_history.to_csv(os.path.join(data_folder, "team_history.csv"), index=False)
    return team_history

if __name__ == "__main__":
    print("Debut du preprocessing...\n")
    data_folder = "data"
    data = load_all_data(data_folder)  # Les CSV sont dans data/ depuis la racine
    
    # Creer player_stats_enriched.csv
    player_stats = create_player_stats_df(data)
    player_stats.to_csv(os.path.join(data_folder, "player_stats_enriched.csv"), index=False)
    print(f"\ndata/player_stats_enriched.csv genere avec succes -> {len(player_stats):,} joueurs")
    
    # Creer team_history.csv
    team_history = create_team_history_df(data, data_folder)
    print(f"data/team_history.csv genere avec succes -> {len(team_history):,} lignes")
    
    print("\nPreprocessing termine avec succes !")