import pandas as pd
import streamlit as st
import plotly.express as px

# Load the CSV file
data = pd.read_csv('combined_posts_and_metadata_with_lat_long.csv')

# Title for the dashboard
st.title("Skuffeside Dashboard")

# Sidebar Filters
st.sidebar.header("Filters")


# Filters with defaults set to 'All'
city = st.sidebar.selectbox("Vælg by:", ["All"] + list(data['city'].dropna().unique()), index=0)
bolig_type = st.sidebar.selectbox("Vælg Bolig Type:", ["All"] + list(data['bolig_type'].dropna().unique()), index=0)
rooms = st.sidebar.selectbox("Vælg Antal rum:", ["All"] + list(data['bolig_rooms'].dropna().unique()), index=0)
energy_label = st.sidebar.selectbox("Vælg Energimærke:", ["All"] + list(data['energy_label'].dropna().unique()), index=0)

price_min = int(data['bolig_price'].min())
price_max = int(data['bolig_price'].max())
price_range = st.sidebar.slider("Vælg prisklasse (DKK):", price_min, price_max, (price_min, price_max))

area_min = int(data['boligareal'].min())
area_max = int(data['boligareal'].max())
area_range = st.sidebar.slider("Vælg Boligareal Range (m²):", area_min, area_max, (area_min, area_max))

# Add a "Clear All Filters" button
if st.sidebar.button("Ryd alle filtre"):
    st.experimental_rerun()

# Apply Filters
filtered_data = data.copy()

if city != "All":
    filtered_data = filtered_data[filtered_data['city'] == city]

if bolig_type != "All":
    filtered_data = filtered_data[filtered_data['bolig_type'] == bolig_type]

if rooms != "All":
    filtered_data = filtered_data[filtered_data['bolig_rooms'] == rooms]

if energy_label != "All":
    filtered_data = filtered_data[filtered_data['energy_label'] == energy_label]

filtered_data = filtered_data[
    (filtered_data['bolig_price'] >= price_range[0]) & (filtered_data['bolig_price'] <= price_range[1])
]
filtered_data = filtered_data[
    (filtered_data['boligareal'] >= area_range[0]) & (filtered_data['boligareal'] <= area_range[1])
]

# Display the number of properties found
st.subheader(f"Der er så mange boliger fundet: {len(filtered_data)}")

# Map Section
st.header("Boligers beliggenhed")
if 'latitude' in filtered_data.columns and 'longitude' in filtered_data.columns:
    map_data = filtered_data[['latitude', 'longitude', 'address', 'city', 'bolig_price']].dropna()
    st.map(map_data)

# Insights
st.header("Indsigt")

# 1. Top 10 Cities with Most Bolig Posts
if 'city' in filtered_data.columns:
    st.subheader("Top 10 byer med flest Bolig-indlæg")
    city_counts = filtered_data['city'].value_counts().head(10).reset_index()
    city_counts.columns = ['City', 'Count']
    fig_city_counts = px.bar(
        city_counts,
        x='City',
        y='Count',
        title="Top 10 byer med flest Bolig-indlæg",
        labels={'City': 'By', 'Count': 'Antal boliger'},
        color='City'
    )
    st.plotly_chart(fig_city_counts)

# 2. Properties by Price per Area
if 'bolig_price' in filtered_data.columns and 'boligareal' in filtered_data.columns:
    st.subheader("Ejendomme efter pris pr. by")
    fig_price_area = px.scatter(
        filtered_data,
        x='boligareal',
        y='bolig_price',
        color='city',
        size='bolig_price',
        title="Ejendomme efter pris vs. areal",
        labels={'boligareal': 'Areal (m²)', 'bolig_price': 'Pris (DKK)'},
    )
    st.plotly_chart(fig_price_area)

# 3. Bolig Posts Created Over Time (Bar Graph)
if 'post_date' in filtered_data.columns:
    st.subheader("Bolig Indlæg Oprettet Over Tid")
    filtered_data['post_month'] = pd.to_datetime(filtered_data['post_date']).dt.to_period('M').astype(str)
    monthly_counts = filtered_data['post_month'].value_counts().sort_index().reset_index()
    monthly_counts.columns = ['Month', 'Count']
    fig_post_months = px.bar(
        monthly_counts,
        x='Month',
        y='Count',
        title="Antal Bolig-indlæg oprettet efter måned",
        labels={'Month': 'Måned', 'Count': 'Antal boliger'},
    )
    st.plotly_chart(fig_post_months)


# Define the columns to show and their new names
default_columns = [
    "post_title", 
    "address", 
    "city", 
    "bolig_price", 
    "boligareal", 
    "bolig_rooms", 
    "energy_label"
]
# Rename the columns
column_mapping = {
    "post_title": "Title",
    "address": "Adresse",
    "city": "By",
    "bolig_price": "Prics (DKK)",
    "boligareal": "Areal (m²)",
    "bolig_rooms": "Værelser",
    "energy_label": "Energimærke"
}
filtered_data.rename(columns=column_mapping, inplace=True)

# Reorder columns based on default_columns (mapped to new names)
ordered_columns = [column_mapping[col] for col in default_columns]
filtered_data = filtered_data[ordered_columns]

# Detailed Data Overview
st.header("Detaljeret dataoversigt")
st.dataframe(filtered_data)
