#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils import ADDON, process_method_on_list
from operator import itemgetter
from artutils import kodidb, Imdb
import xbmc

class Movies(object):
    '''all movie widgets provided by the script'''
    arguments = {}
    
    def __init__(self):
        self.kodi_db = kodidb.KodiDb()
        self.imdb = Imdb()
    
    def listing(self):
        '''main listing with all our movie nodes'''
        all_items = [ 
            (ADDON.getLocalizedString(32028), "inprogress&mediatype=movies", "DefaultMovies.png"), 
            (ADDON.getLocalizedString(32038), "recent&mediatype=movies", "DefaultMovies.png"),
            (ADDON.getLocalizedString(32003), "recommended&mediatype=movies", "DefaultMovies.png"),
            (ADDON.getLocalizedString(32029), "inprogressandrecommended&mediatype=movies", "DefaultMovies.png"),
            (ADDON.getLocalizedString(32032), "inprogressandrandom&mediatype=movies", "DefaultMovies.png"),
            (ADDON.getLocalizedString(32006), "similar&mediatype=movies", "DefaultMovies.png"),
            (ADDON.getLocalizedString(32048), "random&mediatype=movies", "DefaultMovies.png"),
            (ADDON.getLocalizedString(32046), "top250&mediatype=movies", "DefaultMovies.png"),
            (xbmc.getLocalizedString(135), "browsegenres&mediatype=movies", "DefaultGenres.png")
            ]
        return process_method_on_list(self.kodi_db.create_main_entry,all_items)

    def recommended(self):
        ''' get recommended movies - library movies with score higher than 7 '''
        filters = [kodidb.FILTER_RATING]
        if self.arguments["hide_watched"]:
            filters += kodidb.FILTER_
        return self.kodi_db.movies(sort=kodidb.SORT_RATING, filters=filters, limits=(0,self.arguments["limit"]))

    def recent(self):
        ''' get recently added movies '''
        filters = []
        if self.arguments["hide_watched"]:
            filters += kodidb.FILTER_
        return self.kodi_db.movies(sort=kodidb.SORT_DATEADDED, filters=filters, limits=(0,self.arguments["limit"]))
                
    def random(self):
        ''' get random movies '''
        filters = []
        if self.arguments["hide_watched"]:
            filters += kodidb.FILTER_
        return self.kodi_db.movies(sort=kodidb.SORT_RANDOM, filters=filters, limits=(0,self.arguments["limit"]))
                
    def inprogress(self):
        ''' get in progress movies '''
        return self.kodi_db.movies(sort=kodidb.SORT_LASTPLAYED, filters=[kodidb.FILTER_INPROGRESS], limits=(0,self.arguments["limit"]))

    def similar(self):
        ''' get similar movies for given imdbid or just from random watched title if no imdbid'''
        imdb_id = self.arguments.get("imdbid","")
        all_items = []
        all_titles = list()
        json_result = []
        #lookup movie by imdbid or just pick a random watched movie
        
        ref_movie = None
        if imdb_id:
            #get movie by imdbid
            ref_movie = self.kodi_db.movie_by_imdbid(imdb_id)
        if not ref_movie:
            #just get a random watched movie
            ref_movie = self.get_random_watched_movie()
        if ref_movie:
            #get all movies for the genres in the movie
            genres = ref_movie["genre"]
            similar_title = ref_movie["title"]
            for genre in genres:
                self.arguments["genre"] = genre
                genre_movies = self.forgenre()
                for item in genre_movies:
                    #prevent duplicates so skip reference movie and titles already in the list
                    if not item["title"] in all_titles and not item["title"] == similar_title:
                        item["extraproperties"] = {"similartitle": similar_title, "originalpath": item["file"]}
                        all_items.append(item)
                        all_titles.append(item["title"])
        #return the list capped by limit and sorted by rating
        return sorted(all_items,key=itemgetter("rating"),reverse=True)[:self.arguments["limit"]]
    
    def forgenre(self):
        ''' get top rated movies for given genre'''
        genre = self.arguments.get("genre","")
        all_items = []
        if not genre:
            #get a random genre if no genre provided
            genres = self.kodi_db.genres("movie")
            if genres: 
                genre = genres[0]["label"]
        if genre:
            #get all movies from the same genre
            for item in self.get_genre_movies(genre,self.arguments["hide_watched"],self.arguments["limit"]):
                #append original genre as listitem property for later reference by skinner
                item["extraproperties"] = {"genretitle": genre, "originalpath": item["file"]}
                all_items.append(item)

        #return the list sorted by rating
        return sorted(all_items,key=itemgetter("rating"),reverse=True)
        
    def inprogressandrecommended(self):
        ''' get recommended AND in progress movies '''
        all_items = self.inprogress()
        all_titles = [item["title"] for item in all_items]
        for item in self.recommended():
            if item["title"] not in all_titles:
                all_items.append(item)
        return all_items[:self.arguments["limit"]]
        
    def inprogressandrandom(self):
        ''' get in progress AND random movies '''
        all_items = self.inprogress()
        all_ids = [item["movieid"] for item in all_items]
        for item in self.random():
            if item["movieid"] not in all_ids:
                all_items.append(item)
        return all_items[:self.arguments["limit"]]
    
    def top250(self):
        ''' get imdb top250 movies in library '''
        all_items = []
        all_movies = self.kodi_db.get_json('VideoLibrary.GetMovies',fields=["imdbnumber"],returntype="movies")
        top_250 = self.imdb.get_top250_db()
        for movie in all_movies:
            if movie["imdbnumber"] in top_250:
                movie = self.kodi_db.movie(movie["movieid"])
                movie["top250_rank"] = int(top_250[movie["imdbnumber"]])
                all_items.append(movie)
        return sorted(all_items,key=itemgetter("top250_rank"))[:self.arguments["limit"]]
    
    def browsegenres(self):
        '''
            special entry which can be used to create custom genre listings
            returns each genre with poster/fanart artwork properties from 5
            random movies in the genre.
            TODO: get auto generated collage pictures from skinhelper's artutils ?
        '''
        all_genres = self.kodi_db.genres("movie")
        return process_method_on_list(self.get_genre_artwork,all_genres)
        
    def get_genre_artwork(self, genre_json):
        '''helper method for browsegenres'''
        #for each genre we get 5 random items from the library and attach the artwork to the genre listitem
        genre_json["art"] = {}
        genre_json["file"] = "videodb://movies/genres/%s/"%genre_json["genreid"]
        genre_json["isFolder"] = True
        genre_json["IsPlayable"] = "false"
        genre_json["thumbnail"] = genre_json.get("thumbnail", "DefaultGenre.png") #TODO: get icon from resource addon ?
        genre_json["type"] = "genre"
        genre_movies = self.get_genre_movies(genre_json["label"],False,5)
        for count, genre_movie in enumerate(genre_movies):
            genre_json["art"]["poster.%s" %count] = genre_movie["art"].get("poster","")
            genre_json["art"]["fanart.%s" %count] = genre_movie["art"].get("fanart","")
            if not "fanart" in genre_json["art"]:
                #set genre's primary fanart image to first movie fanart
                genre_json["art"]["fanart"] = genre_movie["art"].get("fanart","")
        return genre_json
           
    def get_random_watched_movie(self):
        '''gets a random watched movie from kodidb.'''
        movies = self.kodi_db.movies(sort=kodidb.SORT_RANDOM, filters=[kodidb.FILTER_WATCHED], limits=(0,1))
        if movies:
            return movies[0]
        else:
            return None
            
    def get_genre_movies(self,genre,hide_watched=False,limit=100):
        '''helper method to get all movies in a specific genre'''
        filters = [{"operator":"is", "field":"genre","value":genre}]
        if hide_watched:
            filters += kodidb.FILTER_
        return self.kodi_db.movies(sort=kodidb.SORT_RANDOM, filters=filters, limits=(0,limit))

