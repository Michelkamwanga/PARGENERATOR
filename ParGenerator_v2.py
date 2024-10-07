import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import io

# Configuration de la page avec le logo et le titre
st.set_page_config(page_title="PAR CAREDRC CT - MK", page_icon="logo.png", layout='wide')

# Affichage du logo et du titre au début
with st.container():
    col1, col2 = st.columns([1, 8])
    with col1:
        st.image("logo.png", width=60)
    with col2:
        st.title("Gestion de temps journalier - Personnel Activity Report (PAR)")

        # Texte de notice
    st.write("""
 ### NOTE D'UTILISATION
    Bienvenue dans notre application de remplissage de PAR pour CARE RDC ! Cette application a été conçue pour vous aider à remplir le PAR tout en tenant compte des jours ouvrables et des jours fériés. Veuillez suivre les étapes ci-dessous pour une utilisation optimale de l'application.
    1. **Paramètres de la période**:
       - **Mois, Année et Jour** : Commencez par saisir le mois, l'année et le jour de référence pour votre période de travail. Assurez-vous que la date saisie est valide.
       - **Nombre de projets** : Indiquez le nombre de projets sur lesquels vous travaillerez durant cette période.
    2. **Quinzaine** : L'application déterminera automatiquement la quinzaine en fonction du jour saisi. La première quinzaine s'étend du 1er au 15 du mois, tandis que la deuxième quinzaine s'étend du 16 jusqu'à la fin du mois.
    3. **Jours fériés** : Si votre période comprend des jours fériés, cochez la case appropriée. Vous pourrez alors saisir le nombre de jours fériés à prendre en compte. Saisissez les dates de ces jours fériés afin qu'ils soient exclus du calcul des heures travaillées.
    4. **Saisie des projets** : Pour chaque projet, entrez le nom et le pourcentage d'heures que vous souhaitez allouer à ce projet. Veillez à ce que la somme des pourcentages soit égale à 100 % pour garantir une répartition correcte des heures.
    5. **Affichage des données** : Vous pouvez choisir d'afficher ou de masquer les données saisies. Cela vous permet de travailler dans une interface propre et simplifiée.
    6. **Calcul des heures** : L'application calcule automatiquement le nombre total d'heures disponibles pour chaque projet, en tenant compte des jours ouvrables et des jours fériés. Un tableau récapitulatif s'affichera pour vous montrer la répartition des heures par projet et par jour.

    ### Remarques
    - Assurez-vous de vérifier la validité des dates saisies pour éviter les erreurs dans les calculs.
    - Pour toute question ou problème rencontré lors de l'utilisation de l'application, n'hésitez pas à contacter le support technique au Michel.Kamwanga@care.org et les codes a charger au Nadine.Kavira@care.org ).""")

    # Saisie du mois, de l'année, du jour et du nombre de projets sur une même ligne
    st.subheader("Paramètres de la période et des projets")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mois = st.number_input("Mois (1-12)", min_value=1, max_value=12, step=1, key='mois')
    with col2:
        annee = st.number_input("Année", min_value=2000, max_value=2100, step=1, key='annee')
    with col3:
        jour = st.number_input("Jour (1-31)", min_value=1, max_value=31, step=1, key='jour')
    with col4:
        nb_projets = st.number_input("Nombre de projets", min_value=1, step=1, key='nb_projets')

    # Validation de la date entrée
    try:
        date_saisie = datetime(int(annee), int(mois), int(jour))
    except ValueError:
        st.error("La date saisie n'est pas valide.")
        st.stop()

    # Choisir la quinzaine
    if jour <= 15:
        debut_quinzaine = datetime(int(annee), int(mois), 1)
        fin_quinzaine = datetime(int(annee), int(mois), 15)
    else:
        dernier_jour_mois = pd.Period(f"{annee}-{mois}").days_in_month
        debut_quinzaine = datetime(int(annee), int(mois), 16)
        fin_quinzaine = datetime(int(annee), int(mois), dernier_jour_mois)

    # Demande de jours fériés
    ajouter_feries = st.checkbox("Y a-t-il des jours fériés dans cette période ?")
    jours_feries_utilisateur = []

    if ajouter_feries:
        # Saisie du nombre de jours fériés
        nb_feries = st.number_input("Nombre de jours fériés à saisir :", min_value=1, step=1, key='nb_feries')
        
        # Création de colonnes pour la saisie des jours fériés
        st.subheader("Saisie des jours fériés")
        cols = st.columns(nb_feries)  # Créer autant de colonnes que le nombre de jours fériés à saisir

        for i in range(int(nb_feries)):  # Limiter à nb_feries
            with cols[i]:  # Utiliser l'index pour accéder à la colonne
                date_ferie = st.date_input(f"Jour férié {i + 1} :", datetime.today())
                jours_feries_utilisateur.append(datetime.combine(date_ferie, datetime.min.time()))  # Convertir en datetime

    # Saisie des noms et pourcentages des projets
    st.subheader("Saisie des projets et des pourcentages")

    projets = []
    total_percentage = 0

    # Affichage/Masquage des données saisies
    afficher_donnees = st.checkbox("Afficher/Masquer les données saisies", value=True)

    # Afficher les champs de saisie si la case est cochée
    if afficher_donnees:
        for i in range(nb_projets):
            col1, col2 = st.columns(2)
            with col1:
                nom_projet = st.text_input(f"Nom du projet {i + 1} :", key=f'nom_projet_{i}')
            with col2:
                pourcentage = st.number_input(f"Pourcentage pour {nom_projet} :", min_value=0, max_value=100, step=1, key=f'pourcentage_{i}')

            total_percentage += pourcentage
            projets.append({'nom': nom_projet, 'pourcentage': pourcentage})

    # Vérification que le pourcentage total est de 100%
    if total_percentage != 100:
        st.error("Le pourcentage total doit être égal à 100%. Veuillez ajuster les pourcentages.")
        st.stop()

    # Calcul des jours ouvrables
    jours_quinzaine = pd.date_range(start=debut_quinzaine, end=fin_quinzaine, freq='D')

    # Exclure les jours fériés
    jours_quinzaine = [jour for jour in jours_quinzaine if jour not in jours_feries_utilisateur]

    # Calcul des heures de travail
    heures_par_jour = 8
    jours_ouvres = [jour for jour in jours_quinzaine if jour.weekday() < 5]  # Jours ouvrables seulement
    total_heures = len(jours_ouvres) * heures_par_jour

    # Calcul des heures par projet
    heures_par_projet = []
    for projet in projets:
        heures_projet = (projet['pourcentage'] / 100) * total_heures
        heures_par_projet.append(round(heures_projet, 1))  # Arrondi à 1 décimale

    # Création du tableau de répartition des heures
    tableau_heures = pd.DataFrame(index=[projet['nom'] for projet in projets])

    # Initialiser le DataFrame avec des None pour chaque jour de la quinzaine
    for date in pd.date_range(start=debut_quinzaine, end=fin_quinzaine, freq='D'):
        jour_label = date.strftime("%A, %d-%m-%Y")  # Inclut le jour de la semaine et la date
        tableau_heures[jour_label] = [None for _ in range(nb_projets)]  # Initialiser avec None

    # Remplir le tableau pour les jours ouvrables
    for i, date in enumerate(jours_quinzaine):
        if date.weekday() < 5:  # Jours ouvrables (lundi à vendredi)
            heures_quotidiennes = [round(heures_par_projet[j] / len(jours_ouvres), 1) for j in range(nb_projets)]
            tableau_heures.iloc[:, tableau_heures.columns.get_loc(date.strftime("%A, %d-%m-%Y"))] = heures_quotidiennes

    # Ajout d'une colonne Total pour chaque projet
    tableau_heures["Total"] = tableau_heures.sum(axis=1, numeric_only=True)

    # Ajout d'une ligne Total pour chaque jour
    total_par_jour = []
    for date in pd.date_range(start=debut_quinzaine, end=fin_quinzaine, freq='D'):
        if date.weekday() < 5:  # Jours ouvrables (lundi à vendredi)
            total_par_jour.append(8)  # Total pour les jours ouvrables
        else:  # Week-end (samedi et dimanche)
            total_par_jour.append(None)  # Aucune heure le week-end

    # Ajout de la ligne Total dans le tableau
    tableau_heures.loc["Total"] = total_par_jour + [total_heures]

    # Calculer le nombre total d'heures
    nombre_total_heures = total_heures  # Heures totales après exclusion des jours fériés et week-ends
    nombre_jours_feries = len(jours_feries_utilisateur) * heures_par_jour  # Total des heures de jours fériés
    total_final_heures = nombre_total_heures + nombre_jours_feries  # Total final

    # Affichage des résultats dans Streamlit
    st.subheader("Répartition des heures par projet et par jour")
    st.write("Note: Les jours fériés suivants ont été exclus du calcul :")
    for jour in jours_feries_utilisateur:
        st.write(jour.strftime("%A, %d-%m-%Y"))
    st.write(tableau_heures)

    # Affichage du nombre total d'heures et des jours fériés
    st.markdown(f"**Nombre total d'heures** : {nombre_total_heures} heures")
    st.markdown(f"**Nombre total d'heures de jours fériés** : {nombre_jours_feries} heures")
    st.markdown(f"**Nombre total d'heures après jours fériés** : {total_final_heures} heures")

    # Exportation du tableau au format Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        tableau_heures.to_excel(writer, sheet_name='Heures Calculées', index=True)
    output.seek(0)
    st.download_button(label="Exporter le tableau d'heure en Excel", data=output, file_name='tableau_heures_calculees.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
