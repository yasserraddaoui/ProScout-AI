import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

def compute_player_score(df):
    """Calcule un score global de 0 à 100 basé sur les stats réelles"""
    df = df.copy()
    
    # Colonnes à utiliser (vérifier qu'elles existent)
    available_features = []
    feature_weights = []
    
    if 'goals_per_game' in df.columns:
        available_features.append('goals_per_game')
        feature_weights.append(0.35)
    if 'assists_per_game' in df.columns:
        available_features.append('assists_per_game')
        feature_weights.append(0.25)
    if 'minutes_per_game' in df.columns:
        available_features.append('minutes_per_game')
        feature_weights.append(0.15)
    if 'yellow_cards' in df.columns:
        available_features.append('yellow_cards')
        feature_weights.append(-0.10)
    if 'red_cards' in df.columns:
        available_features.append('red_cards')
        feature_weights.append(-0.15)
    if 'market_value_in_eur' in df.columns:
        available_features.append('market_value_in_eur')
        feature_weights.append(0.20)
    
    if len(available_features) == 0:
        # Fallback: use basic stats
        df['score'] = 50.0
        return df
    
    # Fill NaN values
    df[available_features] = df[available_features].fillna(0)
    
    # Normalisation
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[available_features])
    
    # Pondérations
    weights = np.array(feature_weights)
    
    score = scaled.dot(weights) * 100
    df['score'] = np.clip(score, 0, 100).round(1)
    return df