import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os

def cluster_players(df, n_clusters=5):
    """
    Effectue un clustering des joueurs avec PCA + KMeans
    et sauvegarde le modèle KMeans dans models/cluster_model.pkl
    """
    df = df.copy()
    
    # Vérifier que la colonne score existe
    if "score" not in df.columns:
        raise ValueError("La colonne 'score' doit exister dans le DataFrame avant le clustering")

    # Sélection des colonnes statistiques (exclure les colonnes non numériques)
    exclude_cols = ["player_name", "player_id", "name", "score", "cluster", 
                   "position", "sub_position", "foot", "country_of_citizenship"]
    
    # Sélectionner seulement les colonnes numériques
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    stats_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    if len(stats_cols) == 0:
        raise ValueError("Aucune colonne numérique trouvée pour le clustering")
    
    stats = df[stats_cols].fillna(0)

    # Réduction de dimension avec PCA
    n_components = min(5, len(stats_cols))
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(stats)

    # Clustering KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(reduced)

    df["cluster"] = clusters

    # Créer le dossier models s'il n'existe pas
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    os.makedirs(models_dir, exist_ok=True)

    # Sauvegarder le modèle
    model_path = os.path.join(models_dir, "cluster_model.pkl")
    joblib.dump(kmeans, model_path)

    return df, kmeans, pca


def find_similar_players(df, player_name, top_n=5):
    """
    Trouve les top_n joueurs les plus similaires à player_name
    en utilisant la similarité cosinus
    """
    # Vérifier le nom de la colonne (peut être 'player_name' ou 'name')
    name_col = 'player_name' if 'player_name' in df.columns else 'name'
    
    if name_col not in df.columns:
        raise ValueError(f"Colonne de nom de joueur introuvable dans le DataFrame")
    
    if player_name not in df[name_col].values:
        raise ValueError(f"Le joueur {player_name} n'existe pas dans le DataFrame")

    player_idx = df[df[name_col] == player_name].index[0]
    
    # Sélectionner seulement les colonnes numériques pour la similarité
    exclude_cols = ["player_name", "player_id", "name", "score", "cluster", 
                   "position", "sub_position", "foot", "country_of_citizenship"]
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    stats_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    stats = df[stats_cols].fillna(0)

    sim_matrix = cosine_similarity(stats)
    sim_scores = list(enumerate(sim_matrix[player_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # On prend les indices des joueurs les plus similaires (sauf lui-même)
    similar_idx = [i for i, score in sim_scores[1:top_n+1]]
    
    # Retourner plus d'informations utiles
    result_cols = [name_col]
    if "cluster" in df.columns:
        result_cols.append("cluster")
    if "score" in df.columns:
        result_cols.append("score")
    if "position" in df.columns:
        result_cols.append("position")
    if "goals" in df.columns:
        result_cols.append("goals")
    if "assists" in df.columns:
        result_cols.append("assists")
    
    return df.iloc[similar_idx][result_cols]
