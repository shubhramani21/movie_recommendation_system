import streamlit as st
import pickle
import pandas as pd
import requests

API_KEY = '350d9555d777e2abfbc466e83e8fb0d2'
BASE_URL = 'https://api.themoviedb.org/3/'
HEADERS = {'accept': 'application/json'}

def getPosterImdbID(movieID):
    movie_url = f"{BASE_URL}movie/{movieID}?api_key={API_KEY}&append_to_response=keywords"
    movie_response = requests.get(movie_url, headers=HEADERS)

    movie = movie_response.json()

    path = 'https://image.tmdb.org/t/p/original' + movie.get('poster_path')
    imdbID = movie.get('imdb_id')
    imdbID = imdbID[2:]

    return path, imdbID

def recommend(movie):
    # Get the input movie's ID (handle duplicate titles)
    input_movie = movies[movies['title'] == movie]
    if input_movie.empty:
        return [], []  # Movie not found
    movie_index = input_movie.index[0]
    current_movie_id = input_movie.iloc[0].id  # Unique ID of the input movie
    current_movie_vote = input_movie.iloc[0].vote_average

    # Get similarity scores
    distance = similarity[movie_index]
    sort_list = sorted(enumerate(distance), reverse=True, key=lambda x: x[1])

    recommend_movies = []
    recommend_movieID = []
    seen_ids = set()  # Track unique movie IDs (not titles)

    for i in sort_list:
        movie_id = movies.iloc[i[0]].id
        movie_title = movies.iloc[i[0]].title
        movie_vote = movies.iloc[i[0]].vote_average

        # Skip the input movie or already added movies
        if movie_id == current_movie_id or movie_id in seen_ids:
            continue

        # Condition 1: Higher or equal rating than input movie (max 2)
        if (movie_vote >= current_movie_vote) and (len(recommend_movies) < 2):
            recommend_movies.append(movie_title)
            recommend_movieID.append(movie_id)
            seen_ids.add(movie_id)

        # Condition 2: General high rating (max 5 total)
        elif (movie_vote >= 7) and (len(recommend_movies) < 5):
            recommend_movies.append(movie_title)
            recommend_movieID.append(movie_id)
            seen_ids.add(movie_id)

        # Stop once we have 5 recommendations
        if len(recommend_movies) >= 5:
            break

    return recommend_movies, recommend_movieID

movies = pickle.load(open('movies.pkl', 'rb')) # dataframe of the movies
similarity = pickle.load(open('similarity.pkl', 'rb')) # getting similarity score

movies_title = movies['title'].values
movies_title = tuple(movies_title)

st.title('Movie Recommender System')

selected_movie = st.selectbox(
    "How would you like to be contacted?",
    movies_title,
)

if st.button("Recommend", type='primary'):
    st.write("### You have selected:", selected_movie)  # Bigger heading

    recommended_movies, recommend_movieID = recommend(selected_movie)

    cols = st.columns(len(recommended_movies))  # Create columns dynamically

    for col, movie, movieID in zip(cols, recommended_movies, recommend_movieID):
        poster, imdbID = getPosterImdbID(movieID)
        imdb_url = f"https://www.imdb.com/title/tt{imdbID}/"  # TMDB movie link
        
        with col:
            st.markdown(
                f"""
                <div style="text-align: center; height: 500px;">
                    <a href="{imdb_url}" target="_blank">
                        <img src="{poster}" width="200" style="border-radius: 10px;">
                    </a>
                    <br>
                    <a href="{imdb_url}" target="_blank" style="text-decoration: none; color: white;">
                        <h4>{movie}</h4>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
