import requests
from bs4 import BeautifulSoup
import time
import random

AFISHA_SCHEDULE = "http://www.afisha.ru/msk/schedule_cinema/"

NUMBER_OF_MOVIES = 10

MIN_NUMBER_OF_THEATERS = 10

PROXY = "183.88.185.181:8080"

KINOPOISK = "https://www.kinopoisk.ru/index.php"

def fetch_afisha_page(url):
    request = requests.get(url)
    if request.status_code == 200:
        request.encoding = "utf-8"
        return request.text
    else:
        print("Нет ответа от сервера")


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
    default = 0
    if movie_ratings is not None:
        movie_rating = float(movie_ratings.text)
    else:
        movie_rating = default

    return movie_rating


def add_movie_rating(movies_list):
    movies_info = dict()
    for movie in movies_list:
        movies_info[movie] = (get_movie_rating(
                            fetch_kinopoisk_page(movie)))
        time.sleep(random.randrange(5, 10))
    return movies_info


def fetch_kinopoisk_page(movie_title):
    url = KINOPOISK
    payload = {"first": "yes", "kp_query": movie_title}
    headers = {"User-Agent": "Mozilla/5.0"
    "(Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"}
    proxy = {"http": PROXY, }
    request = requests.get(url, params=payload, headers=headers,
        proxies=proxy)
    if request.status_code == 200:
        request.encoding = "utf-8"
        return request.text
    else:
        print("{}, нет ответа от кинопоиска".format(movie_title))


def sort_movies_based_on_rating(movie_dict):
    return sorted(movie_dict.items(), key=lambda x: x[1],
                    reverse=True)


def output_movies_to_console(movies):
    for movie in movies:
        print("{}, рейтинг: {}".format(movie[0], movie[1]))


if __name__ == '__main__':
    movies = parse_afisha_list(fetch_afisha_page(AFISHA_SCHEDULE))
    movies_filtered = (filter_movies(movies, MIN_NUMBER_OF_THEATERS))
    movies_rated = add_movie_rating(movies_filtered)
    movies_sorted = sort_movies_based_on_rating(movies_rated)
    output_movies_to_console(movies_sorted)
