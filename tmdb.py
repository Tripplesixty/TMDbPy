'''
tmdb.py is a wrapper for The Movie Database API v3
Their documentation is at:
    http://docs.themoviedb.apiary.io/

Created by Artifaxx on 2014-04-01
'''
#Standar library imports
import cgi
import json
import urllib

#Third Party Imports
import requests

'''
 _____ __  __ ____  _
|_   _|  \/  |  _ \| |__
  | | | |\/| | | | | '_ \
  | | | |  | | |_| | |_) |
  |_| |_|  |_|____/|_.__/
'''
class TMDB:
    def __init__(self, api_key, api_uri="https://api.themoviedb.org", version=3):
        if api_key is None:
            raise ValueError("No API key provided")

        TMDB.api_key = api_key
        TMDB.uri = '{}/{}'.format(api_uri, version)

        params={"api_key" : api_key}

        self.request("configuration", params)

    def request(self, path, params={}):
        uri = "{}/{}".format(TMDB.uri, path)
        params["api_key"] = TMDB.api_key 
        headers = {'Accept': 'application/json'}

        request = requests.get(uri, params = params, headers=headers)
        if request.status_code == requests.codes.ok:
            body = request.json()
            return body
        else:
            return request.raise_for_status()

    '''
     __  __            _
    |  \/  | _____   _(_) ___
    | |\/| |/ _ \ \ / / |/ _ \
    | |  | | (_) \ V /| |  __/
    |_|  |_|\___/ \_/ |_|\___|
    '''
    def get_movie(self, movie_id):
        return Movie(movie_id, self)

    def get_movie_info(self, movie_id):
        path = "movie/{}".format(movie_id)
        return self.request(path)

    def get_movie_property(self, movie_id, property, params={}):
        ''''
        used as an abstraction layer for the movie object
            
        queries a specific TMDB API URI based on the movie_id
        and propery.
        '''
        path = "movie/{}/{}".format(movie_id, property)
        return self.request(path, params)

    def get_latest_movies(self, params={}):
        '''
        Get the latest movie id.
        '''

        path = "/movie/latest"
        return self.request(path, params)

    def get_upcoming_movies(self, params={}):
        '''
        Get the list of upcoming movies. This list refreshes every day. 
        The maximum number of items this list will include is 100.

        Optional Parameters
            page    Minimum 1, maximum 1000.
            language    ISO 639-1 code.
        '''

        path = "/movie/upcoming"
        return self.request(path, params)

    def get_now_playing_movies(self, params={}):
        '''
        Get the list of movies playing in theatres. This list refreshes every day. 
        The maximum number of items this list will include is 100.

        Optional Parameters
            page    Minimum 1, maximum 1000.
            language    ISO 639-1 code.        
        '''

        path = "/movie/now_playing"
        return self.request(path, params)

    def get_popular_movies(self, params={}):
        '''
        Get the list of popular movies on The Movie Database. This list refreshes every day.

        Optional Parameters
            page    Minimum 1, maximum 1000.
            language    ISO 639-1 code.
        '''

        path = "/movie/popular"
        return self.request(path, params)

    def get_top_rated_movies(self, params={}):
        '''
        Get the list of top rated movies. By default, this list will only include movies that have 10 or more votes. This list refreshes every day.

        Optional Parameters
            page    Minimum 1, maximum 1000.
            language    ISO 639-1 code.
        '''

        path = "/movie/top_rated"
        return self.request(path, params)

    '''
     ____                      _
    / ___|  ___  __ _ _ __ ___| |__
    \___ \ / _ \/ _` | '__/ __| '_ \
     ___) |  __/ (_| | | | (__| | | |
    |____/ \___|\__,_|_|  \___|_| |_|
    '''
    def _search(self, query, path, params):
        params["query"] = query
        path = "search/{}".format(path)
        body = self.request(path, params)

        return body["results"]
    
    def search_movie(self, query="", params={}):
        '''
        Search TMDB for a movie, retunrs a list of the first 10 results

        Required parameters:
            query (CGI escaped string)

        Optional parameters:
            page (min = 1, max = 1000),
            language (ISO 639-1 code),
            include_adult (true/false),
            year (filters all release dates),
            primary_release_year (filters primary release date)
        '''
        
        path = "movie"

        return self._search(query, path, params)
        
    def search_movie_all(self, query="", params={}, page=1):
        '''
        Search TMDB for a movie, retunrs a complete list of results
        matching the search query.  This is exhaustive and should
        only be used with complete title names.  Due to recursion
        this function could take a very long time to return or may
        overrun stack size.  Use with caution.

        Required parameters:
            query (CGI escaped string)
            
        Optional parameters:
            language (ISO 639-1 code),
            include_adult (true/false),
            year (filters all release dates),
            primary_release_year (filters primary release date)
        '''
        params["query"] = query
        params["page"] = page
        path = "search/movie"

        body = self.request(path, params)
        result = body["results"]

        if body["page"] < body["total_pages"]:
            page += 1
            body += self.search_movie_all(query, params, page)
            result += body[results]

        return result


    def search_collection(self, query="", params={}):
        '''
        Search TMDB for a collection, returns a list of collections
        matching the serch query

        Optional parameters:
            page (min = 1, max = 100),
            language (ISO 639-1 code)
        '''
        path = "collection"
        return self._search(query, path, params)


    def search_person(self, params):
        '''
        Search TMDB for a person, returns a list of people
        matching the serch query

        Optional parameters:
            page (min = 1, max = 100),
            include_adult (true/false)
        '''
        path = "person"
        return self._search(query, path, params)
'''
 __  __            _
|  \/  | _____   _(_) ___
| |\/| |/ _ \ \ / / |/ _ \
| |  | | (_) \ V /| |  __/
|_|  |_|\___/ \_/ |_|\___|
'''
class Movie:
    def __init__(self, movie_id, tmdb):
        self.movie_id = movie_id
        self.tmdb = tmdb
        
        self.info = tmdb.get_movie_info(movie_id)

    def get_info(self):
        return self.info;
    
    def get_alternative_titles(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "credits", params)

    def get_credits(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "credits", params)

    def get_images(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "images", params)

    def get_keywords(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "keywords", params)

    def get_releases(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "releases", params)

    def get_trailers(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "trailers", params)

    def get_translations(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "translations", params)

    def get_similar_movies(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "similar_movies", params)

    def get_reviews(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "reviews", params)

    def get_lists(self, params={}):
        return self.tmdb.get_movie_property(self.movie_id, "lists", params)

'''
  ____      _ _           _   _
 / ___|___ | | | ___  ___| |_(_) ___  _ __
| |   / _ \| | |/ _ \/ __| __| |/ _ \| '_ \
| |__| (_) | | |  __/ (__| |_| | (_) | | | |
 \____\___/|_|_|\___|\___|\__|_|\___/|_| |_|
 '''
class Collection:
    def __init__(self, collection_id=0):
        self.collection_id = collection_id
        self.base = "/collection/" + str(self.collection_id)

    def info(self):
        return TMDB.request(self.base)

    def images(self):
        path = self.base + "/images"
        return TMDB.request(path)

'''
  ____
 / ___|___  _ __ ___  _ __   __ _ _ __  _   _
| |   / _ \| '_ ` _ \| '_ \ / _` | '_ \| | | |
| |__| (_) | | | | | | |_) | (_| | | | | |_| |
 \____\___/|_| |_| |_| .__/ \__,_|_| |_|\__, |
                     |_|                |___/
'''
class Company:
    def __init__(self, company_id=0):
        self.company_id = company_id
        self.base = "/company/" + str(self.company_id)

    def info(self):
        return TMDB.request(self.base)

    def movies(self):
        path = self.base + "/movies"
        return TMDB.request(path)

'''
 ____
|  _ \ ___ _ __ ___  ___  _ __
| |_) / _ \ '__/ __|/ _ \| '_ \
|  __/  __/ |  \__ \ (_) | | | |
|_|   \___|_|  |___/\___/|_| |_|
'''
class Person:
    def __init__(self, person_id=0):
        self.person_id = person_id
        self.base = "/person/" + str(self.person_id)

    def info(self):
        return TMDB.request(self.base)

    def movie_credits(self):
        path = self.base + "/movie_credits"
        return TMDB.request(path)

    def external_ids(self):
        path = self.base + "/external_ids"
        return TMDB.request(path)

    def images(self):
        path = self.base + "/images"
        return TMDB.request(path)

    def popular(self):
        path = "/person/popular"
        return TMDB.request(path)

    def latest(self):
        path = "/person/latest"
        return TMDB.request(path)
'''
____            _
|  _ \ _____   _(_) _____      __
| |_) / _ \ \ / / |/ _ \ \ /\ / /
|  _ <  __/\ V /| |  __/\ V  V /
|_| \_\___| \_/ |_|\___| \_/\_/
'''
class Review:
    def __init__(self, review_id=0):
        self.review_id = review_id
        self.base = "/review/" + str(self.review_id)

    def info(self):
        return TMDB.request(self.base)



