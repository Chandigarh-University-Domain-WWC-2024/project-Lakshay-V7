import pickle
import streamlit as st
import requests
import pandas as pd
import numpy as np

# Function to fetch the movie poster using TMDB API
def fetch_poster(movie_id):
    api_key = '2887491e47021c448ed0b25bfa8b18e2'  # Replace with your actual TMDB API key
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()
    
    if 'poster_path' in data and data['poster_path']:
        poster_path = data['poster_path']
        full_path = "http://image.tmdb.org/t/p/w500" + poster_path
        return full_path
    else:
        return None  # Return None if no poster is found

# Function to recommend movies based on the selected movie
def recommend(selected_movie, movies, similarity):
    try:
        # Find the index of the selected movie
        index = movies[movies['title'] == selected_movie].index[0]
        print(f"Index of the selected movie '{selected_movie}': {index}")  # Debugging line
    except IndexError:
        st.write("Selected movie not found in the dataset.")
        return [], []  # Return empty lists if the movie is not found
    
    # Ensure the similarity DataFrame has the correct index
    if index not in similarity.index:
        st.write("Index not found in the similarity matrix.")
        return [], []

    # Convert similarity matrix to numeric, replace non-numeric values with zero
    similarity_numeric = similarity.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Get the similarity scores for the selected movie
    similarity_scores = list(enumerate(similarity_numeric.iloc[index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    recommended_movies_name = []
    recommended_movies_poster = []

    # Fetch top 5 recommended movies (excluding the first one which is the selected movie itself)
    for i in similarity_scores[1:6]:  # Skip the first movie as it is the selected movie itself
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        
        if poster_url:
            recommended_movies_poster.append(poster_url)
            recommended_movies_name.append(movies.iloc[i[0]].title)

    return recommended_movies_name, recommended_movies_poster

# Streamlit UI setup
st.header("Movies Recommendation System Using Machine Learning")

# Load data
try:
    movies = pickle.load(open('artificats/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('artificats/similarity.pkl', 'rb'))
    st.write("Data loaded successfully.")  # Debugging line
except FileNotFoundError as e:
    st.write(f"Error loading data: {e}")
    st.stop()

# Display first few rows of the data for debugging
st.write(movies.head())
st.write(similarity.head())

movie_list = movies['title'].values
selected_movie = st.selectbox('Type or select a movie to get recommendation', movie_list)

if st.button('Show recommendation'):
    recommended_movies_name, recommended_movies_poster = recommend(selected_movie, movies, similarity)

    # Handle case if there are no recommended movies
    if not recommended_movies_name:
        st.write("Sorry, no recommendations found.")
    else:
        # Display recommended movies
        cols = st.columns(5)
        for i in range(5):
            if i < len(recommended_movies_name):
                with cols[i]:
                    st.text(recommended_movies_name[i])
                    st.image(recommended_movies_poster[i])
