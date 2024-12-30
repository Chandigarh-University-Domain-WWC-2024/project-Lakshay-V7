from flask import Flask, render_template, request
import pickle
import requests
import pandas as pd

app = Flask(__name__)

# Function to fetch poster images from TMDB
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2887491e47021c448ed0b25bfa8b18e2&language=en-US"
    response = requests.get(url)
    data = response.json()
    
    # Check if there's a poster available
    if 'poster_path' in data and data['poster_path']:
        poster_path = data['poster_path']
        full_path = "http://image.tmdb.org/t/p/w500" + poster_path
        return full_path
    else:
        return None  # Return None if no poster is found

# Function to recommend movies based on similarity
def recommend(selected_movie, movies, similarity):
    try:
        # Find the index of the selected movie
        index = movies[movies['title'] == selected_movie].index[0]
    except IndexError:
        return [], []  # Return empty lists if the movie is not found

    # Ensure that the similarity matrix is numeric and fill NaN with 0
    similarity_row = similarity.iloc[index].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Sort the movies based on similarity score
    distances = sorted(list(enumerate(similarity_row)), reverse=True, key=lambda x: x[1])

    recommended_movies_name = []
    recommended_movies_poster = []

    # Limit the recommendations to a maximum of 5
    for i in distances[1:]:  # Exclude the first item (which is the movie itself)
        if len(recommended_movies_name) < 5:  # Prevent adding more than 5 movies
            # Only consider recommendations with a non-zero similarity score
            if i[1] > 0:
                movie_id = movies.iloc[i[0]].movie_id
                poster_url = fetch_poster(movie_id)
                if poster_url:
                    recommended_movies_poster.append(poster_url)
                    recommended_movies_name.append(movies.iloc[i[0]].title)
            else:
                break  # Stop adding recommendations when similarity score is 0 or less

    return recommended_movies_name, recommended_movies_poster

# Load movie data and similarity matrix from pickle files
movies = pickle.load(open('artificats/movie_list.pkl', 'rb'))
similarity = pickle.load(open('artificats/similarity.pkl', 'rb'))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the selected movie from the form
        selected_movie = request.form.get('movie')
        recommended_movies_name, recommended_movies_poster = recommend(selected_movie, movies, similarity)

        # Return the results to the HTML template
        return render_template("index.html", movies=recommended_movies_name, posters=recommended_movies_poster)

    # If GET request, just render the empty form
    movie_list = movies['title'].values
    return render_template("index.html", movies=movie_list, posters=[])

if __name__ == "__main__":
    app.run(debug=True)
