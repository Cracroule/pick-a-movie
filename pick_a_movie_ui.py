import numpy as np
import pandas as pd
import streamlit as st
import st_aggrid

from datetime import datetime

from data_manip import rescale_image_from_url, load_movie_data

# to run it locally;
# conda activate pick-a-movie      OR       pyenv activate pick-a-movie
# streamlit run /home/raoul/Code/pick-a-movie/pick_a_movie_ui.py


@st.cache_data
def load_movie_data_cached(min_votes=500):
    return load_movie_data(min_votes)


st.set_page_config(page_title="pick-a-movie", layout="centered")  # prepare steamlit page
df_movies = load_movie_data_cached()  # load all data (only once using @cache_data decorator)

###########################################################################
#              Sidebar Widgets   (used for selection criteria)
st.sidebar.title("Pick-a-movie")
st.sidebar.subheader("Search Criteria")

# Platforms
all_platforms = ["Netflix US", "Netflix NZ", "Prime"]
platforms = st.sidebar.multiselect("Platforms", all_platforms)

# IMDB Rating
imdb_rating_range = st.sidebar.slider("Minimum IMDB Rating", 3.0, 10.0, (5.0, 10.0), 0.1)

# Movie Categories
# todo: parse actual categories from overall data
all_categories = ["Action", "Comedy", "Romance", "Thriller"]
categories = st.sidebar.multiselect("Movie Categories", all_categories)

# expander to handle extra criteria (year / country...)
expander = st.sidebar.expander("More search criteria")

# year release
current_year = datetime.now().year
year_range = expander.slider("Release year", 1950, current_year, (1990, current_year))
all_countries = sorted(["United States", "Canada", "France", "Germany", "India"])
production_country = expander.multiselect("production country", all_countries)

st.sidebar.write("")
empty_col, button_col = st.sidebar.columns([1, 1])
pick_movie_button = button_col.button("pick-a-movie!")

###########################################################################
#                       State handling
#  (Only refreshed content if state is updated, i.e. init or button pressed)
if "user_selection" not in st.session_state or pick_movie_button:
    st.session_state.user_selection = {"platforms": platforms, "imdb_rating_range": imdb_rating_range,
                                       "categories": categories, "year_range": year_range}
    st.session_state.seed = np.random.randint(1, 1000)
np.random.seed(st.session_state.seed)  # set "constant" seed (constant per state)

###########################################################################
#         Main content widget: picked movie and suggested table

placeholder_movie = st.empty()  # container for the picked movie, will be defined below
st.write("")
st.header("Some more movies choices")

# filter selected movies dynamically
# todo: improve selection criterias here
selected_df = df_movies[(df_movies["IMDB_rating"] > st.session_state.user_selection["imdb_rating_range"][0]) &
                        (df_movies["IMDB_rating"] < st.session_state.user_selection["imdb_rating_range"][1])]
n_random_choices = 20
selected_df = selected_df.iloc[np.random.choice(selected_df.shape[0], n_random_choices,
                                                p=selected_df["IMDB_rating"]/selected_df["IMDB_rating"].sum())]
displayed_df = selected_df[["title", "year", "IMDB_rating", "genre"]]

gb = st_aggrid.GridOptionsBuilder.from_dataframe(displayed_df)
# gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
gb.configure_side_bar()  # Add a sidebar
gb.configure_selection()
# gb.configure_selection('multiple', groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
gridOptions = gb.build()

grid_response = st_aggrid.AgGrid(
    selected_df, gridOptions=gridOptions,
    # data_return_mode='AS_INPUT',
    # update_mode='MODEL_CHANGED',
    fit_columns_on_grid_load=False,
    columns_auto_size_mode=st_aggrid.ColumnsAutoSizeMode.FIT_CONTENTS,
    # theme='material', #Add theme color to the table
    enable_enterprise_modules=True,
    height=300, width='100%', reload_data=False)

data = grid_response['data']
selected = grid_response['selected_rows']

# if something is selected in the aggrid, display it, else display first of the displayed list
displayed_movie = selected[0] if len(selected) else selected_df.iloc[0]

col2, col1 = placeholder_movie.columns([5, 2])
col1.image(rescale_image_from_url(displayed_movie["image"]))
col2.header(displayed_movie["title"])
col2.write(str(displayed_movie["year"]))
col2.write(displayed_movie["genre"].replace(";", ", "))
col2.write(displayed_movie["summary"])
