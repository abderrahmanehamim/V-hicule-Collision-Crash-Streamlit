# Importation des bibliothèques nécessaires
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Charger les données à partir d'un fichier
@st.cache(allow_output_mutation=True)
def load_data(nrows):
    # Chemin du fichier contenant les données
    data_url = "https://raw.githubusercontent.com/fivethirtyeight/data/master/car-accidents/car-accidents.csv"
    
    # Lire les données du fichier
    data = pd.read_csv(data_url, nrows=nrows)
    
    # Renommer les colonnes
    data.rename(columns={"crash_date_crash_time": "date/time"}, inplace=True)
    
    return data

# Charger les données
data = load_data(100000)

# Afficher le titre et le slider pour filtrer les collisions par nombre de personnes blessées
st.header("Où sont les plus de personnes blessées dans New York?")
injured_people = st.slider("Nombre de personnes blessées dans les collisions de véhicules", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

# Afficher le titre et le slider pour filtrer les collisions par heure
st.header("Combien de collisions ont lieu au cours d'une heure donnée?")
hour = st.slider("Heure à examiner", 0, 23)
original_data = data
data = data[data['date/time'].dt.hour == hour]

# Afficher le résultat pour l'heure choisie
st.markdown("Collisions de véhicules entre %i:00 et %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))

# Afficher la carte 3D avec les collisions pour l'heure choisie
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ],
))

# Afficher le graphique pour le nombre de collisions par minute pour l'heure choisie
st.subheader("Répartition par minute entre %i:00 et %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

# Afficher le classement des 5 rues les plus dangereuses par classe d'affectés
st.header("Classement des 5 rues les plus dangereuses par classe d'affectés")
select = st.selectbox('Classe d\'affectés', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])

# Afficher les données brutes si l'utilisateur le souhaite
if st.checkbox("Afficher les données brutes", False):
    st.subheader('Données brutes')
    st.write(data)