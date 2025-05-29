# Suivi_Prod
📊 Suivi de la Ligne d'Assemblage – COFAT

Cette application Streamlit permet de suivre, analyser et simuler les performances d'une ligne d'assemblage industrielle (chez COFAT Group), en s'appuyant sur les données collectées et stockées dans une base Supabase.

---

## ⚙️ Fonctionnalités Principales

### ✅ Ajout de Données
- Saisie manuelle des postes, dates, durées de cycle individuelles (x10), et temps de cycle total.
- Stockage automatique dans la table Supabase "ligne_assemblage" sous le nom de dataset défini.

### 📊 Analyse de Données
- Affichage du tableau historique d'un dataset sélectionné.
- Calcul du TRS (Taux de Rendement Synthétique) basé uniquement sur la performance :
  ```
  TRS = Disponibilité × Performance × Qualité = 1 × (temps_cycle / moyenne) × 1
  ```
- Affichage d’un graphique en barres du TRS par poste.

### 🔍 Diagramme de Pareto
- Calcul et affichage du temps moyen par poste.
- Analyse des goulots d’étranglement via un diagramme de Pareto combinant :
  - Barres = temps moyen
  - Courbe = pourcentage cumulé

### 🎬 Simulation
- Reproduction animée du déroulement de la production selon les postes et leurs temps de cycle.

---

## 🧰 Technologies Utilisées

- Python
- Streamlit
- Supabase (PostgreSQL Backend)
- Pandas
- Matplotlib

---

## 📦 Dépendances

Assurez-vous d’installer les dépendances suivantes :
```bash
pip install streamlit pandas matplotlib supabase
```

---

## 🔐 Configuration

Créez un fichier `.streamlit/secrets.toml` avec vos identifiants Supabase :
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-api-key"
```

---

## ▶️ Lancement de l'application

Lancez l'application localement avec :
```bash
streamlit run app.py
```

---

## 📁 Structure des Données dans Supabase (Table : ligne_assemblage)

- `poste`: nom du poste
- `date_mesure`: date de la saisie
- `temps_cycle`: durée totale du cycle
- `dataset_name`: nom du dataset
- `temps_1` à `temps_10`: étapes individuelles du cycle

---

## 📌 Remarques
- Le TRS ici est simplifié : on suppose une disponibilité et une qualité égales à 1.
- Les animations de simulation sont simulées avec des pauses (`time.sleep`) proportionnelles aux temps de cycle.

---

## 👩‍💼 Auteur

Projet réalisé par une étudiante en 2eme année Génie Industriel dans le cadre du projet PFA2 avec COFAT Group.
