import requests
from bs4 import BeautifulSoup
import time
import random

AFISHA_SCHEDULE = "http://www.afisha.ru/msk/schedule_cinema/"

NUMBER_OF_MOVIES = 10

MIN_NUMBER_OF_THEATERS = 100

KINOPOISK = "https://www.kinopoisk.ru/index.php"

PARAMETERS = dict()

PARAMETERS["payload"] = {"first": "yes", "kp_query": ""}

PARAMETERS["headers"] = {"User-Agent": "Mozilla/5.0"
"(Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"}


def get_raw_html(request):
    if request.status_code == 200:
        request.encoding = "utf-8"
        return request.text


def fetch_page(url, **kwargs):
    params = None
    headers = None
    for key in kwargs:
        params = kwargs["payload"]
        headers = kwargs["headers"] 
    request = requests.get(url, params=params, headers=headers)
    return get_raw_html(request)


# def fetch_page(url, parameters=None):
#     if parameters is None:
#         request = requests.get(url)
#         return get_raw_html(request)
#     else:
#         payload = parameters["payload"]
#         headers = parameters["headers"]
#         request = requests.get(url, params=payload, headers=headers)
#         return get_raw_html(request)


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    movies = soup.find_all("h3", class_="usetags")
    movie_titles_list = [movie.text for movie in movies]
    cinemas = soup.find(id="schedule").find_all("tbody")
    cinemas_count = [len(cinema.find_all("tr")) for cinema in cinemas]
    movies_with_cinemas = dict(zip(movie_titles_list, cinemas_count))
    return movies_with_cinemas


def filter_movies(movies_dict, min_num_of_theaters):
    return [movie for movie in movies_dict if
            movies_dict[movie] > min_num_of_theaters]


def get_movie_rating(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    movie_ratings = soup.find("span", class_="rating_ball")
    movie_votes = soup.find("span", class_="ratingCount")
    if movie_ratings is not None:
        movie_rating = float(movie_ratings.text)
        return movie_rating


def add_movie_rating(movies_list):
    movies_info = dict()
    for movie in movies_list:
        PARAMETERS["payload"]["kp_query"] = movie
        movies_info[movie] = (get_movie_rating(
                            fetch_page(KINOPOISK, payload=PARAMETERS["payload"], headers=PARAMETERS["headers"])))
        time.sleep(random.randrange(5, 10))
    return movies_info


def sort_movies_based_on_rating(movie_dict):
    return sorted(movie_dict.items(), key=lambda x: x[1],
                    reverse=True)


def output_movies_to_console(movies):
    for movie in movies:
        print("{}, рейтинг: {}".format(movie[0], movie[1]))


if __name__ == '__main__':
    movies = parse_afisha_list(fetch_page(AFISHA_SCHEDULE))
    movies_filtered = (filter_movies(movies, MIN_NUMBER_OF_THEATERS))
    movies_rated = add_movie_rating(movies_filtered)
    movies_sorted = sort_movies_based_on_rating(movies_rated)
    output_movies_to_console(movies_sorted)
    