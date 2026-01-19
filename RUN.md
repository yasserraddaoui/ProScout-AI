# ProScout AI - Guide d'installation et d'exécution

## 📋 Prérequis
- Python 3.8+
- Tous les fichiers CSV dans le dossier `data/`

## 🚀 Installation

### 1. Installer les dépendances

Si Streamlit est déjà en cours d'exécution, fermez-le d'abord, puis :

```bash
pip install -r requirements.txt
```

Ou avec l'option --user si vous avez des problèmes de permissions :

```bash
pip install --user -r requirements.txt
```

### 2. Vérifier que les données sont prêtes

Assurez-vous que ces fichiers existent dans `data/` :
- ✅ `player_stats_enriched.csv` (généré par preprocess.py)
- ✅ `team_history.csv` (généré par preprocess.py)
- ✅ Tous les autres CSV originaux

Si les fichiers enrichis n'existent pas, exécutez :

```bash
python src/preprocess.py
```

## 🎯 Lancer l'application

```bash
streamlit run streamlit_app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse :
**http://localhost:8501**

## 📱 Fonctionnalités

### 🏠 Dashboard
- Vue d'ensemble des statistiques
- Top 10 joueurs par score
- Distribution des scores

### 👤 Player Analysis
- Analyse détaillée d'un joueur
- Radar chart de performance
- Joueurs similaires
- Statistiques complètes

### ⚽ Team Lineup
- Recommandation de meilleure équipe historique
- Formation 4-3-3 interactive
- Analyse par équipe

### 📊 Analytics
- Performance par position
- Analyse Goals vs Assists
- Graphiques interactifs

### 🔍 Player Search
- Recherche par nom
- Filtres avancés (score, buts, position)
- Tableau de résultats

## 🎨 Interface

L'application utilise un thème dark mode professionnel avec :
- Design moderne inspiré de Wyscout/InStat
- Cartes joueurs stylisées
- Graphiques interactifs Plotly
- Formation tactique 4-3-3

## ⚠️ Dépannage

### Erreur "Module not found"
```bash
pip install -r requirements.txt
```

### Erreur "File not found"
Vérifiez que tous les CSV sont dans le dossier `data/` et exécutez :
```bash
python src/preprocess.py
```

### Streamlit ne démarre pas
Fermez toutes les instances de Streamlit et réessayez :
```bash
# Windows
taskkill /F /IM streamlit.exe

# Puis relancez
streamlit run streamlit_app.py
```

## 📞 Support

En cas de problème, vérifiez :
1. Que Python 3.8+ est installé
2. Que tous les packages sont installés
3. Que les fichiers CSV sont présents
4. Que le port 8501 n'est pas utilisé par une autre application

