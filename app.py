import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client
from datetime import datetime
import os

def calcul_trs(df):
    st.subheader("Calcul du TRS")

    # Calculate temps_moyens
    temps_moyens = df['temps_cycle'].mean()

    # Initialize list to store TRS data
    trs_list = []

    # Iterate over posts to calculate TRS for each
    grouped = df.groupby("poste")
    for poste, group in grouped:
        for _, row in group.iterrows():
            temps_cycle = row['temps_cycle']
            performance = temps_cycle / temps_moyens

            # Disponibility and Quality are always 1
            trs = performance  # TRS = 1 * performance * 1

            trs_list.append({
                "Poste": poste,
                "Temps Cycle": temps_cycle,
                "Temps Moyens": round(temps_moyens, 2),
                "Performance (%)": round(performance * 100, 2),
                "TRS (%)": round(trs * 100, 2),
            })

    # Convert results to a DataFrame
    trs_df = pd.DataFrame(trs_list)

    # Display the TRS data
    st.dataframe(trs_df)
    st.bar_chart(trs_df.set_index("Poste")["TRS (%)"])
def simulate_production(df):
    import time
    st.subheader("Résultats de la Simulation")
    for index, row in df.iterrows():
        poste = row['poste']
        temps = row['temps_cycle']
        with st.spinner(f"Traitement du {poste}..."):
            time.sleep(temps / 10)  # Simulate time taken for each task
        st.success(f"{poste} : Tâche terminée en {temps:.1f} secondes.")


# Initialize Supabase connection
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except KeyError:
    st.error("Supabase credentials not found. Please check your secrets.toml file.")
    st.stop()
except Exception as e:
    st.error(f"Error connecting to Supabase: {str(e)}")
    st.stop()

st.title("🛠️ Suivi Ligne d'Assemblage – COFAT")

# Fetch available dataset names from the database
try:
    data = supabase.table("ligne_assemblage").select("dataset_name").execute().data
    datasets = list(set(row['dataset_name'] for row in data)) if data else []
except Exception as e:
    st.error(f"Erreur lors de la récupération des données: {str(e)}")
    st.stop()

# Main menu
menu = st.radio("Que voulez-vous faire ?", ["Ajouter de nouvelles données", "Consulter l'historique"])

if menu == "Ajouter de nouvelles données":
    dataset_name = st.text_input("Nom de la nouvelle table", placeholder="Ex: Dataset X")
    if not dataset_name:
        st.warning("Veuillez saisir un nom de table pour continuer.")
        st.stop()

    n_postes = st.number_input("Nombre total de postes à saisir", min_value=1, step=1, value=5)

    try:
        data = supabase.table("ligne_assemblage").select("*").eq("dataset_name", dataset_name).execute().data
        current_postes = pd.DataFrame(data)['poste'].nunique() if data else 0
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {str(e)}")
        st.stop()

    if current_postes < n_postes:
        with st.form("ajout"):
            col1, col2 = st.columns(2)
            with col1:
                poste = st.text_input("Poste", placeholder="Ex: Encliquetage des fils")
            with col2:
                date = st.date_input("Date", value=datetime.today())

            st.subheader("Temps des étapes (en secondes)")

            temps_fields = []
            cols = st.columns(5)
            for i in range(10):
                if i % 5 == 0 and i != 0:
                    cols = st.columns(5)
                with cols[i % 5]:
                    temps_fields.append(
                        st.number_input(f"Temps {i + 1}", min_value=0, step=1, value=30)
                    )

            temps_cycle = st.number_input("Temps de Cycle Total (s)", min_value=0, step=1, value=35)

            submitted = st.form_submit_button("Ajouter")

        if submitted:
            if not poste:
                st.warning("Veuillez saisir un nom de poste.")
            elif len(temps_fields) < 10:
                st.warning("Veuillez remplir toutes les 10 durées de cycle (temps).")
            else:
                try:
                    data = {
                        "poste": poste,
                        "date_mesure": str(date),
                        "temps_cycle": temps_cycle,
                        "dataset_name": dataset_name,
                    }
                    for idx, value in enumerate(temps_fields, 1):
                        data[f"temps_{idx}"] = value

                    response = supabase.table("ligne_assemblage").insert(data).execute()
                    st.success("Donnée ajoutée avec succès!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erreur lors de l'ajout des données: {str(e)}")

elif menu == "Consulter l'historique":
    # Dropdown to select a dataset
    selected_dataset = st.selectbox("Sélectionnez une table existante :", datasets)

    if selected_dataset:
        try:
            # Fetch data for the selected dataset
            data = supabase.table("ligne_assemblage").select("*").eq("dataset_name", selected_dataset).execute().data
            df = pd.DataFrame(data)

            if not df.empty:
                # Display the cleaned dataset
                st.subheader("Données récupérées")
                clean_df = df[["poste", "temps_cycle", "date_mesure"]]
                st.dataframe(clean_df)

                # Calculate temps_moyens for the dataset
                temps_moyens = df['temps_cycle'].mean()

                # TRS Calculation
                st.subheader("Calcul du TRS")
                trs_list = []

                grouped = df.groupby("poste")
                for poste, group in grouped:
                    for _, row in group.iterrows():
                        temps_cycle = row["temps_cycle"]
                        performance = temps_cycle / temps_moyens

                        # Since disponibilite and qualite are always 1
                        trs = performance

                        trs_list.append({
                            "Poste": poste,
                            "Temps Cycle": temps_cycle,
                            "Temps Moyens": round(temps_moyens, 2),
                            "Performance (%)": round(performance * 100, 2),
                            "TRS (%)": round(trs * 100, 2)
                        })

                # Convert results to DataFrame and display
                trs_df = pd.DataFrame(trs_list)
                st.dataframe(trs_df)

                # TRS Bar Chart
                st.bar_chart(trs_df.set_index("Poste")["TRS (%)"])

                # Pareto diagram logic (Restored Original)
                poste_stats = df.groupby('poste', as_index=False).agg(
                    temps_moyen=('temps_cycle', 'mean'),
                    occurrences=('temps_cycle', 'count')
                ).sort_values('temps_moyen', ascending=False)

                poste_stats['cumulative_percent'] = (
                    poste_stats['temps_moyen'].cumsum() /
                    poste_stats['temps_moyen'].sum() * 100
                )
                # Pareto diagram logic (Restored Original)
                poste_stats = df.groupby('poste', as_index=False).agg(
                    temps_moyen=('temps_cycle', 'mean'),
                    occurrences=('temps_cycle', 'count')
                ).sort_values('temps_moyen', ascending=False)

                poste_stats['cumulative_percent'] = (
                    poste_stats['temps_moyen'].cumsum() /
                    poste_stats['temps_moyen'].sum() * 100
                )

                # Create Pareto diagram
                fig, ax1 = plt.subplots(figsize=(10, 6))

                bars = ax1.bar(
                    poste_stats['poste'],
                    poste_stats['temps_moyen'],
                    color='skyblue',
                    edgecolor='black'
                )
                ax1.set_xlabel('Postes')
                ax1.set_ylabel('Temps Moyen (secondes)', color='steelblue')
                ax1.tick_params(axis='y', labelcolor='steelblue')
                plt.xticks(rotation=45, ha='right')

                ax2 = ax1.twinx()
                ax2.plot(
                    poste_stats['poste'],
                    poste_stats['cumulative_percent'],
                    color='tomato',
                    marker='o',
                    linestyle='--'
                )
                ax2.set_ylabel('Pourcentage Cumulé (%)', color='tomato')
                ax2.tick_params(axis='y', labelcolor='tomato')
                ax2.set_ylim(0, 110)

                plt.title(f'Analyse des Goulots de Production (Pareto) – {selected_dataset}')
                st.pyplot(fig)

                # Simulation Section
                st.subheader("Simulation du Flux de Production")
                n_postes = df['poste'].nunique() if 'poste' in df.columns else 0

                if n_postes > 0:
                    if st.button("Démarrer la Simulation"):
                        simulate_production(df)  # Pass the dataframe to the simulation function
                else:
                    st.warning("Aucune donnée disponible pour la simulation.")
            else:
                st.warning(f"Aucune donnée trouvée pour le dataset '{selected_dataset}'.")
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données: {str(e)}")