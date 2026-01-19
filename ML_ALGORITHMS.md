# 🤖 Algorithmes de Machine Learning - ProScout AI

## Vue d'ensemble

Ce projet utilise **5 algorithmes de Machine Learning** pour analyser les données de football et fournir des insights professionnels.

---

## 1. 🎯 K-Means Clustering (Clustering non supervisé)

### Fichier : `src/clustering.py`

**Algorithme** : K-Means de scikit-learn

**Objectif** : Grouper les joueurs en clusters similaires selon leurs performances

**Comment ça marche** :
1. Prend toutes les statistiques numériques des joueurs (buts, passes, minutes, etc.)
2. Réduit la dimensionnalité avec PCA (voir ci-dessous)
3. Divise les joueurs en **5 clusters** (groupes)
4. Chaque cluster représente un "profil" de joueur (ex: attaquant prolifique, milieu défensif, etc.)

**Paramètres** :
- `n_clusters = 5` (5 groupes de joueurs)
- `random_state = 42` (pour la reproductibilité)

**Utilisation** :
- Classification automatique des joueurs par profil
- Recommandation de joueurs similaires
- Analyse de tendances par groupe

**Modèle sauvegardé** : `models/cluster_model.pkl`

---

## 2. 📉 PCA (Principal Component Analysis)

### Fichier : `src/clustering.py`

**Algorithme** : PCA de scikit-learn

**Objectif** : Réduire la dimensionnalité des données avant le clustering

**Comment ça marche** :
1. Les joueurs ont beaucoup de statistiques (buts, passes, minutes, cartons, etc.)
2. PCA transforme ces nombreuses variables en **5 composantes principales**
3. Ces composantes capturent l'essentiel de l'information
4. Réduit le bruit et améliore les performances du clustering

**Paramètres** :
- `n_components = min(5, nombre_de_features)` (5 composantes principales)

**Avantages** :
- Réduction du temps de calcul
- Amélioration de la qualité du clustering
- Élimination de la redondance entre variables

---

## 3. 🔍 Cosine Similarity (Similarité cosinus)

### Fichier : `src/clustering.py` - fonction `find_similar_players()`

**Algorithme** : Cosine Similarity de scikit-learn

**Objectif** : Trouver les joueurs les plus similaires à un joueur donné

**Comment ça marche** :
1. Calcule la similarité cosinus entre tous les joueurs
2. La similarité cosinus mesure l'angle entre deux vecteurs de statistiques
3. Plus l'angle est petit, plus les joueurs sont similaires
4. Retourne les **top 5 joueurs** les plus similaires

**Formule** : 
```
similarité = cos(θ) = (A · B) / (||A|| × ||B||)
```

**Utilisation** :
- Recommandation de joueurs similaires
- Comparaison de profils
- Découverte de talents cachés

**Avantages** :
- Indépendant de la magnitude (un joueur avec beaucoup de buts peut être similaire à un autre avec moins de buts mais même style)
- Efficace pour les données normalisées

---

## 4. 📊 MinMaxScaler (Normalisation)

### Fichier : `src/player_scoring.py`

**Algorithme** : MinMaxScaler de scikit-learn

**Objectif** : Normaliser les statistiques entre 0 et 1 pour le calcul du score

**Comment ça marche** :
1. Trouve le minimum et maximum de chaque statistique
2. Transforme chaque valeur : `(x - min) / (max - min)`
3. Toutes les valeurs sont maintenant entre 0 et 1
4. Permet de combiner des statistiques avec des échelles différentes

**Exemple** :
- Buts : 0-50 → normalisé à 0-1
- Passes décisives : 0-30 → normalisé à 0-1
- Minutes : 0-3000 → normalisé à 0-1

**Utilisation** :
- Calcul du score de performance des joueurs
- Combinaison pondérée de différentes statistiques

**Pondérations utilisées** :
- Buts/match : **35%** (le plus important)
- Passes décisives/match : **25%**
- Minutes/match : **15%**
- Valeur marchande : **20%**
- Cartons jaunes : **-10%** (pénalité)
- Cartons rouges : **-15%** (grosse pénalité)

---

## 5. 🔮 Prophet (Forecasting / Prédiction temporelle)

### Fichier : `src/forecasting.py`

**Algorithme** : Prophet de Facebook (Meta)

**Objectif** : Prédire le nombre de buts futurs d'un joueur

**Comment ça marche** :
1. Analyse l'historique des buts du joueur dans le temps
2. Détecte les tendances et saisonnalités
3. Prédit les buts futurs avec des intervalles de confiance
4. Utilise un modèle additif avec composantes :
   - Tendance
   - Saisonnalité mensuelle
   - Variations aléatoires

**Paramètres** :
- `yearly_seasonality = False`
- `weekly_seasonality = False`
- `daily_seasonality = False`
- `monthly_seasonality = True` (période de 30.5 jours)

**Sortie** :
- `yhat` : Prédiction moyenne
- `yhat_lower` : Borne inférieure (intervalle de confiance)
- `yhat_upper` : Borne supérieure (intervalle de confiance)

**Utilisation** :
- Prédiction de performance future
- Planification de transferts
- Analyse de tendances

**Avantages** :
- Gère automatiquement les saisonnalités
- Robuste aux valeurs manquantes
- Fournit des intervalles de confiance

---

## 📋 Résumé des Algorithmes

| Algorithme | Type | Bibliothèque | Objectif |
|------------|------|--------------|----------|
| **K-Means** | Clustering | scikit-learn | Grouper les joueurs en profils |
| **PCA** | Réduction dimension | scikit-learn | Optimiser le clustering |
| **Cosine Similarity** | Similarité | scikit-learn | Trouver joueurs similaires |
| **MinMaxScaler** | Normalisation | scikit-learn | Calculer scores normalisés |
| **Prophet** | Forecasting | Prophet (Meta) | Prédire performances futures |

---

## 🔄 Pipeline ML Complet

```
1. Données brutes (CSV)
   ↓
2. Preprocessing (agrégation, nettoyage)
   ↓
3. MinMaxScaler → Normalisation
   ↓
4. Calcul Score (pondération)
   ↓
5. PCA → Réduction dimension
   ↓
6. K-Means → Clustering (5 groupes)
   ↓
7. Cosine Similarity → Recommandations
   ↓
8. Prophet → Prédictions (optionnel)
```

---

## 💡 Cas d'usage

### 1. Scoring des joueurs
- **Algorithme** : MinMaxScaler + Pondération
- **Résultat** : Score de 0 à 100 pour chaque joueur

### 2. Classification par profil
- **Algorithme** : PCA + K-Means
- **Résultat** : 5 clusters de joueurs (ex: Cluster 0 = Attaquants, Cluster 1 = Milieux, etc.)

### 3. Recommandation
- **Algorithme** : Cosine Similarity
- **Résultat** : Top 5 joueurs similaires à un joueur donné

### 4. Prédiction
- **Algorithme** : Prophet
- **Résultat** : Nombre de buts prévus pour les prochains matchs

---

## 🎓 Niveau de complexité

- **Débutant** : MinMaxScaler, Cosine Similarity
- **Intermédiaire** : K-Means, PCA
- **Avancé** : Prophet (modèle de séries temporelles)

---

## 📚 Références

- **scikit-learn** : https://scikit-learn.org/
- **Prophet** : https://facebook.github.io/prophet/
- **K-Means** : Algorithme classique de clustering
- **PCA** : Analyse en composantes principales
- **Cosine Similarity** : Mesure de similarité vectorielle

---

## 🚀 Améliorations possibles

1. **Deep Learning** : Réseaux de neurones pour classification avancée
2. **XGBoost/LightGBM** : Pour meilleures prédictions
3. **Collaborative Filtering** : Recommandations basées sur les préférences
4. **Reinforcement Learning** : Optimisation de formations tactiques
5. **NLP** : Analyse de commentaires et articles de presse

---

**Créé pour ProScout AI** ⚽

