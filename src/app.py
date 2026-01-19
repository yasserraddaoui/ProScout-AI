import streamlit as st
import pandas as pd
from preprocess import generate_csv
from player_scoring import compute_score
from clustering import cluster_players
from recommend import recommend

# Générer dataset propre (si nécessaire)
generate_csv(
    sqlite_path="C:/Users/yasse/Desktop/FOOTBALL-ML/data/database.sqlite",
    csv_path="C:/Users/yasse/Desktop/FOOTBALL-ML/data/football_players_stats.csv"
)

# Charger CSV
df = pd.read_csv("C:/Users/yasse/Desktop/FOOTBALL-ML/data/football_players_stats.csv")

# Calculer score
df = compute_score(df)

# Clustering
df, kmeans, pca = cluster_players(df)

# Streamlit UI
st.title("⚽ Football Player Intelligence System")

player_name = st.selectbox("Choisir un joueur :", df["player_name"])

player_info = df[df.player_name == player_name].iloc[0]
st.subheader("Score Performance")
st.write(f"Score : {player_info['score']} / 100")
st.write(f"Cluster / Profil : {player_info['cluster']}")

st.subheader("Top 5 joueurs similaires")
similar_players = recommend(df, player_name)
st.table(similar_players)
