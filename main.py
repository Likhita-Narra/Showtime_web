import requests
import pickle
import pandas as pd
import streamlit as st
from fuzzywuzzy import fuzz

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movies = pd.DataFrame(movies_dict)


def search_crct_name(name, search_list):
    crct_name = None
    max_value = None
    for i in search_list:
        if max_value is None or fuzz.token_set_ratio(i, name) > max_value:
            max_value = fuzz.token_set_ratio(i, name)
            crct_name = i
    return crct_name

st.image("title.png")
with st.sidebar:
    selected_movie_name = st.selectbox(
        '🔎 Search for a movie',
        movies['title'].values)
    search = st.button("Search")

    st.write("")
    col1, col2 = st.columns([3.5, 1])
    with col1:
        st.subheader("Make some choices &")

    with col2:
        view = st.button("  View  ")

    with st.expander("📆 Year"):
        from datetime import date

        current_year = date.today().year
        year = st.slider('Year of release', 1900, current_year, [1900, current_year])
        st.write("Movies released between ", year)

    with st.expander("🎦 Genres"):
        from unique import unique_multi

        genres = st.multiselect("Select genres", unique_multi(movies['genres']), [])

    with st.expander("🗣️ Languages"):
        from unique import unique

        languages = st.multiselect("Select languages", unique(movies['original_language']), [])

    with st.expander("🎬 Director"):
        crew = st.text_input('Search by director', '')

    with st.expander("🎭 Cast"):
        cast = st.text_input('Search by top cast', '')

    st.subheader("\n⬆️ Sort results")
    with st.expander("Sort by"):
        attribute = st.selectbox(
            '',
            ['Popularity', 'Rating'])

    colsm1, colsm2, colsm3 = st.columns([1, 3, 1])
    with colsm2:
        st.write("")
        surprise_me = st.button("🤩 Surprise Me!")


def fetch_poster(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=2d41c3dee6e40a90011507ecef2855e6&language=en-US'.format(
            movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/original/" + data['poster_path']


def fetch_overview(title):
    overview = movies['overview'][movies.index[movies['title'] == title]].values[0]
    return overview


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[0:10]
    recommended_movies = [movies.iloc[i[0]].title for i in movies_list]
    recommended_movies_posters = [fetch_poster(movies.iloc[i[0]].id) for i in movies_list]
    return recommended_movies, recommended_movies_posters


def display_column_content(movie_name, movie_poster):
    st.text(movie_name)
    st.image(movie_poster)
    with st.expander("Know More"):
        st.write(fetch_overview(movie_name))


@st.cache(suppress_st_warning=True)
def popular_movies():
    movie_ids = list(movies['id'][0:9])
    movie_names = list(movies['title'][0:9])
    movie_posters = [fetch_poster(i) for i in movie_ids]
    return movie_names, movie_posters


if not(search or view or surprise_me):
    names, posters = popular_movies()
    st.subheader("\n✨ Most popular movies:")

    colp01, colp02, colp03 = st.columns(3)
    colp11, colp12, colp13 = st.columns(3)
    colp21, colp22, colp23 = st.columns(3)

    with colp01:
        display_column_content(names[0], posters[0])

    with colp02:
        display_column_content(names[1], posters[1])

    with colp03:
        display_column_content(names[2], posters[2])

    with colp11:
        display_column_content(names[3], posters[3])

    with colp12:
        display_column_content(names[4], posters[4])

    with colp13:
        display_column_content(names[5], posters[5])

    with colp21:
        display_column_content(names[6], posters[6])

    with colp22:
        display_column_content(names[7], posters[7])

    with colp23:
        display_column_content(names[8], posters[8])


elif search:
    names, posters = recommend(selected_movie_name)
    st.subheader("\n🥇 Top Result:")
    col11, col12 = st.columns(2)
    with col11:
        st.text(names[0])
        st.image(posters[0])

    with col12:
        st.text("Overview")
        st.write(fetch_overview(names[0]))

    st.write("")
    st.subheader("More similar results:")

    col21, col22, col23 = st.columns(3)

    with col21:
        display_column_content(names[1], posters[1])

    with col22:
        display_column_content(names[2], posters[2])

    with col23:
        display_column_content(names[3], posters[3])

    col31, col32, col33 = st.columns(3)

    with col31:
        display_column_content(names[4], posters[4])

    with col32:
        display_column_content(names[5], posters[5])

    with col33:
        display_column_content(names[6], posters[6])

    col41, col42, col43 = st.columns(3)

    with col41:
        display_column_content(names[7], posters[7])

    with col42:
        display_column_content(names[8], posters[8])

    with col43:
        display_column_content(names[9], posters[9])


elif view:
    condition = {
        'crew': "crew in movies['crew'].iloc[i]",
        'cast': "cast in movies['cast'].iloc[i]",
        'language': "str(movies['original_language'].iloc[i]) in languages",
        'genres': "any(x in genres for x in movies['genres'].iloc[i])",
        'years': "year[0] <= movies['year'].iloc[i] <= year[1]",
    }

    cond_list = []
    if crew != '':
        crew = search_crct_name(crew, unique(movies['crew']))
        cond_list.append(condition['crew'])
    if cast != '':
        cast = search_crct_name(cast, unique_multi(movies['cast']))
        cond_list.append(condition['cast'])
    if len(genres) != 0:
        cond_list.append(condition['genres'])
    if len(languages) != 0:
        cond_list.append(condition['language'])
    if year != (1900, current_year):
        cond_list.append(condition['years'])
    condition_str = " and ".join(cond_list)

    filtered_movies = pd.DataFrame(columns=movies.columns)
    for i in range(0, len(movies)):
        if eval(condition_str):
            filtered_movies = filtered_movies.append(movies.iloc[i])

    if len(filtered_movies) == 0:
        st.info('Oops! No matching results')
    else:
        if attribute == 'Rating':
            filtered_movies = filtered_movies.sort_values(by=['vote_average'], ascending=False)
        length = len(filtered_movies)
        f_names = list(filtered_movies['title'])[0:10]
        f_ids = list(filtered_movies['id'])[0:10]
        f_posters = [fetch_poster(i) for i in f_ids]
        f_overviews = [fetch_overview(i) for i in f_names]

        st.subheader("\n🥇 Top Result:")
        col11, col12 = st.columns(2)

        with col11:
            st.text(f_names[0])
            st.image(f_posters[0])

        with col12:
            st.text("Overview")
            st.write(fetch_overview(f_names[0]))

        if length >= 2:
            st.subheader("\nMore matching results:")
            col21, col22, col23 = st.columns(3)
            with col21:
                display_column_content(f_names[1], f_posters[1])

            if length >= 3:
                with col22:
                    display_column_content(f_names[2], f_posters[2])

            if length >= 4:
                with col23:
                    display_column_content(f_names[3], f_posters[3])

            col31, col32, col33 = st.columns(3)

            if length >= 5:
                with col31:
                    display_column_content(f_names[4], f_posters[4])

            if length >= 6:
                with col32:
                    display_column_content(f_names[5], f_posters[5])

            if length >= 7:
                with col33:
                    display_column_content(f_names[6], f_posters[6])

            col41, col42, col43 = st.columns(3)

            if length >= 8:
                with col41:
                    display_column_content(f_names[7], f_posters[7])

            if length >= 9:
                with col42:
                    display_column_content(f_names[8], f_posters[8])

            if length >= 10:
                with col43:
                    display_column_content(f_names[9], f_posters[9])

elif surprise_me:
    cols1, cols2, cols3 = st.columns([1, 4, 1])
    with cols2:
        id = movies['id'].sample().item()
        title = movies['title'][movies.index[movies['id'] == id]].item()
        st.subheader("\n🍿 Wanna give it a shot? 🥤\n")
        st.text(title)
        st.image(fetch_poster(id))
        with st.expander("Know More"):
            st.write(fetch_overview(title))
    with cols3:
        st.balloons()