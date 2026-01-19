from clustering import find_similar_players

def recommend(df, player_name, top_n=5):
    """
    Recommande les joueurs les plus similaires à player_name.

    Parameters:
    -----------
    df : DataFrame
        Doit contenir les colonnes 'player_name' et 'cluster' (après clustering)
    player_name : str
        Nom du joueur pour lequel on veut les recommandations
    top_n : int
        Nombre de joueurs similaires à retourner

    Returns:
    --------
    DataFrame avec les joueurs similaires et leur cluster
    """
    # Vérifier que le DataFrame contient les colonnes nécessaires
    if 'player_name' not in df.columns or 'cluster' not in df.columns:
        raise ValueError("Le DataFrame doit contenir les colonnes 'player_name' et 'cluster'")

    # Vérifier que le joueur existe
    if player_name not in df['player_name'].values:
        raise ValueError(f"Le joueur '{player_name}' n'existe pas dans le DataFrame")

    # Utiliser la fonction find_similar_players du clustering
    similar_players = find_similar_players(df, player_name, top_n=top_n)
    return similar_players
