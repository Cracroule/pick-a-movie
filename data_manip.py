import json
import pandas as pd
import requests


def rescale_image_from_url(url):
    tmp_str = url.rsplit('_V1_', 1)
    if len(tmp_str):
        return (tmp_str[0] + ".jpg").replace("..", ".")
    return url


# todo: improve data sources and data management here
def load_movie_data(min_votes=500):
    url = r'https://raw.githubusercontent.com/wakeywakeydata/RandomFilm/main/all_movie_dict_str.txt'
    resp = requests.get(url)
    all_movie_dict_str = resp.content
    all_movie_dict = json.loads(all_movie_dict_str)
    df = pd.DataFrame.from_dict(all_movie_dict)
    df = df[df["n_of_vote"] >= min_votes][["title", "year", "IMDB_rating", "genre", "summary"]]
    df = df.drop_duplicates()

    url = r'https://raw.githubusercontent.com/wakeywakeydata/RandomFilm/main/all_posters_str.txt'
    resp = requests.get(url)
    all_posters_str = resp.content
    all_posters_dict = json.loads(all_posters_str)
    df2 = pd.DataFrame.from_dict(all_posters_dict)[["title", "image"]]

    df = df.merge(df2)

    # tmp_df = df.groupby(["title", "year", "IMDB_rating", "genre"])['n_of_vote'].max().to_frame().reset_index()
    # df = pd.merge(df, tmp_df, on=["title", "year", "IMDB_rating", "genre", 'n_of_vote'])

    return df
