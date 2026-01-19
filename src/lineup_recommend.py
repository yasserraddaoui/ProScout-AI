import pandas as pd

def get_historical_lineups(team_name, data, top_n=10):
    """Get best historical lineup for a team"""
    try:
        lineups = data.get('game_lineups', pd.DataFrame())
        games = data.get('games', pd.DataFrame())
        players = data.get('players', pd.DataFrame())
        ap = data.get('appearances', pd.DataFrame())
        clubs = data.get('clubs', pd.DataFrame())
        
        if lineups.empty or games.empty or players.empty or ap.empty:
            return pd.DataFrame(columns=['name', 'position', 'goals', 'assists', 'contrib_score', 'player_name'])
        
        # Trouver l'ID du club par son nom
        club_id = None
        if not clubs.empty and 'name' in clubs.columns:
            club_match = clubs[clubs['name'] == team_name]
            if not club_match.empty:
                club_id = club_match.iloc[0]['club_id']
        
        if club_id is None:
            # Essayer de trouver par home_club_name ou away_club_name si ces colonnes existent
            if 'home_club_name' in games.columns:
                team_games = games[(games['home_club_name'] == team_name) | (games['away_club_name'] == team_name)].copy()
            elif 'home_club_id' in games.columns and club_id:
                team_games = games[(games['home_club_id'] == club_id) | (games['away_club_id'] == club_id)].copy()
            else:
                return pd.DataFrame(columns=['name', 'position', 'goals', 'assists', 'contrib_score', 'player_name'])
        else:
            # Utiliser club_id pour trouver les matchs
            if 'home_club_id' in games.columns:
                team_games = games[(games['home_club_id'] == club_id) | (games['away_club_id'] == club_id)].copy()
            else:
                return pd.DataFrame(columns=['name', 'position', 'goals', 'assists', 'contrib_score', 'player_name'])
        
        if team_games.empty:
            return pd.DataFrame(columns=['name', 'position', 'goals', 'assists', 'contrib_score', 'player_name'])
        
        # Stats par joueur dans ces matchs
        player_perf = ap[ap['game_id'].isin(team_games['game_id'])].groupby('player_id').agg({
            'goals': 'sum',
            'assists': 'sum',
            'minutes_played': 'sum'
        }).reset_index()
        
        # Merge avec players pour obtenir nom et position
        if 'name' in players.columns:
            player_perf = player_perf.merge(players[['player_id', 'name', 'position']], on='player_id', how='left')
        elif 'player_name' in players.columns:
            player_perf = player_perf.merge(players[['player_id', 'player_name', 'position']], on='player_id', how='left')
            player_perf = player_perf.rename(columns={'player_name': 'name'})
        else:
            return pd.DataFrame(columns=['name', 'position', 'goals', 'assists', 'contrib_score', 'player_name'])
        
        player_perf['contrib_score'] = player_perf['goals']*5 + player_perf['assists']*3 + player_perf['minutes_played']/90
        player_perf = player_perf.fillna({'goals': 0, 'assists': 0, 'minutes_played': 0, 'contrib_score': 0})
        
        # Normaliser les positions pour une meilleure correspondance
        player_perf['position_normalized'] = player_perf['position'].str.lower().fillna('')
        
        # Meilleurs joueurs par position (formation 4-3-3)
        # Gardien
        best_gk = player_perf[
            player_perf['position_normalized'].str.contains('goalkeeper|gk', case=False, na=False)
        ].sort_values('contrib_score', ascending=False).head(1)
        
        # Défenseurs
        best_def = player_perf[
            player_perf['position_normalized'].str.contains('defender|def|back', case=False, na=False)
        ].sort_values('contrib_score', ascending=False).head(4)
        
        # Milieux
        best_mid = player_perf[
            player_perf['position_normalized'].str.contains('midfielder|mid|central', case=False, na=False)
        ].sort_values('contrib_score', ascending=False).head(3)
        
        # Attaquants
        best_att = player_perf[
            player_perf['position_normalized'].str.contains('attacking|forward|striker|winger|attack', case=False, na=False)
        ].sort_values('contrib_score', ascending=False).head(3)
        
        # Si pas assez de joueurs, prendre les meilleurs disponibles (garantir 11 joueurs)
        used_indices = set()
        
        # GK (1 joueur obligatoire)
        if len(best_gk) == 0:
            best_gk = player_perf.sort_values('contrib_score', ascending=False).head(1)
        used_indices.update(best_gk.index)
        
        # DEF (4 joueurs)
        if len(best_def) < 4:
            remaining = player_perf[~player_perf.index.isin(used_indices)]
            needed = 4 - len(best_def)
            if len(remaining) >= needed:
                additional_def = remaining.sort_values('contrib_score', ascending=False).head(needed)
                best_def = pd.concat([best_def, additional_def], ignore_index=False)
                used_indices.update(additional_def.index)
        else:
            best_def = best_def.head(4)
        used_indices.update(best_def.index)
        
        # MID (3 joueurs)
        if len(best_mid) < 3:
            remaining = player_perf[~player_perf.index.isin(used_indices)]
            needed = 3 - len(best_mid)
            if len(remaining) >= needed:
                additional_mid = remaining.sort_values('contrib_score', ascending=False).head(needed)
                best_mid = pd.concat([best_mid, additional_mid], ignore_index=False)
                used_indices.update(additional_mid.index)
        else:
            best_mid = best_mid.head(3)
        used_indices.update(best_mid.index)
        
        # ATT (3 joueurs)
        if len(best_att) < 3:
            remaining = player_perf[~player_perf.index.isin(used_indices)]
            needed = 3 - len(best_att)
            if len(remaining) >= needed:
                additional_att = remaining.sort_values('contrib_score', ascending=False).head(needed)
                best_att = pd.concat([best_att, additional_att], ignore_index=False)
                used_indices.update(additional_att.index)
        else:
            best_att = best_att.head(3)
        used_indices.update(best_att.index)
        
        # Vérifier qu'on a exactement 11 joueurs
        total_players = len(best_gk) + len(best_def) + len(best_mid) + len(best_att)
        if total_players < 11:
            # Compléter avec les meilleurs joueurs restants
            remaining = player_perf[~player_perf.index.isin(used_indices)]
            needed = 11 - total_players
            if len(remaining) >= needed:
                additional = remaining.sort_values('contrib_score', ascending=False).head(needed)
                # Ajouter aux attaquants par défaut
                best_att = pd.concat([best_att, additional], ignore_index=False)
        
        best_lineup = pd.concat([best_gk, best_def, best_mid, best_att], ignore_index=True)
        
        # S'assurer qu'on a exactement 11 joueurs
        if len(best_lineup) > 11:
            best_lineup = best_lineup.head(11)
        
        # Ajouter image_url si disponible
        if 'image_url' in players.columns:
            best_lineup = best_lineup.merge(players[['player_id', 'image_url']], on='player_id', how='left')
        else:
            best_lineup['image_url'] = None
        
        best_lineup = best_lineup[['name', 'position', 'goals', 'assists', 'contrib_score', 'image_url']].copy()
        best_lineup['player_name'] = best_lineup['name']  # Pour compatibilité avec la formation
        return best_lineup.sort_values('contrib_score', ascending=False)
    except Exception as e:
        import traceback
        return pd.DataFrame(columns=['name', 'position', 'goals', 'assists', 'contrib_score', 'player_name'])