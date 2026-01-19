# run_all.py
import os
import pandas as pd
from preprocess import generate_csv
from player_scoring import compute_score
from clustering import cluster_players
from recommend import recommend
from forecasting import predict_goals
import streamlit as st

# --- 1. Générer CSV ---
sqlite_path = "C:/Users/yasse/Desktop/FOOTBALL-ML/data/database.sqlite"
csv_path = "C:/Users/yasse/Desktop/FOOTBALL-ML/data/football player-stats.csv"
if not os.path.exists(csv_path):
    generate_csv(sqlite_path=sqlite_path, csv_path=csv_path)
print("CSV généré ✅")

# --- 2. Charger CSV et calculer score ---
df = pd.read_csv(csv_path)
df = compute_score(df)
print("Score calculé ✅")

# --- 3. Clustering des joueurs ---
df, kmeans, pca = cluster_players(df, n_clusters=5)
print("Clustering effectué ✅")

# --- 4. Streamlit Interface ---
st.title("Football Player Intelligence System")
player_name = st.text_input("Entrez le nom du joueur :","Lionel Messi")

if player_name and player_name in df['player_name'].values:
    st.subheader("Score et cluster")
    player_data = df[df.player_name==player_name]
    st.write(player_data[['player_name','score','cluster']])

    st.subheader("Joueurs similaires")
    similar = recommend(df, player_name)
    st.write(similar)
else:
    st.write("Joueur non trouvé dans le dataset.")
