import pandas as pd
from prophet import Prophet
import joblib

def predict_goals(player_history_df, player_name, periods=5):
    """
    Prédit le nombre de buts futurs d'un joueur avec Prophet.

    Parameters:
    -----------
    player_history_df : DataFrame
        Doit contenir les colonnes ['date', 'player_name', 'goals']
    player_name : str
        Nom du joueur à prédire
    periods : int
        Nombre de matchs/jours futurs à prédire

    Returns:
    --------
    forecast : DataFrame
        Colonnes ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
    """
    # Filtrer le joueur
    df_player = player_history_df[player_history_df.player_name == player_name][['date', 'goals']].copy()
    df_player = df_player.rename(columns={'date':'ds','goals':'y'})

    # Vérifier qu'il y a des données
    if df_player.empty:
        raise ValueError(f"Aucune donnée historique pour le joueur {player_name}")

    # Convertir la colonne 'ds' en datetime
    df_player['ds'] = pd.to_datetime(df_player['ds'])

    # Créer et entraîner le modèle Prophet
    m = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
    m.add_seasonality(name='monthly', period=30.5, fourier_order=5)
    m.fit(df_player)

    # Créer les dates futures à prédire
    future = m.make_future_dataframe(periods=periods, freq='D')  # freq='D' pour un jour, adapte si besoin

    # Faire la prédiction
    forecast = m.predict(future)

    # Retourner seulement les colonnes importantes
    return forecast[['ds','yhat','yhat_lower','yhat_upper']]
