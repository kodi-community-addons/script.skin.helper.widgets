# script.skin.helper.service
a helper service for Kodi skins

This product uses the TMDb API but is not endorsed or certified by TMDb.


#### Widget reload properties
If you need to refresh a widget automatically after the library is changed or after playback stop you can append these to the widget path.

For example:

```
plugin://myvideoplugin/movies/?latest&amp;reload=$INFO[Window(Home).Property(widgetreload-episodes)]
```

| property 			| description |
|:-----------------------------	| :----------- |
|Window(Home).Property(widgetreload) | will change if any video content is added/changed in the library or after playback stop of any video content (in- or outside of library) |
|Window(Home).Property(widgetreload-episodes) | will change if episodes content is added/changed in the library or after playback stop of episodes content (in- or outside of library) |
|Window(Home).Property(widgetreload-movies) | will change if movies content is added/changed in the library or after playback stop of movies content (in- or outside of library) |
|Window(Home).Property(widgetreload-tvshows) | will change if tvshows content is added/changed in the library |
|Window(Home).Property(widgetreload-music) | will change if any music content is added/changed in the library or after playback stop of music (in- or outside of library) |
|Window(Home).Property(widgetreload2) | will change every 10 minutes (e.g. for pvr widgets or favourites) |



### Dynamic content provider
The script also has a plugin entrypoint to provide some dynamic content that can be used for example in widgets.
use the parameter [LIMIT] to define the number of items to show in the list. defaults to 25 if the parameter is not supplied.


#####Next Episodes
```
plugin://script.skin.helper.service/?action=nextepisodes&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload)]
```
Provides a list of the nextup episodes. This can be the first episode in progress from a tv show or the next unwatched from a in progress show.
Note: the reload parameter is needed to auto refresh the widget when the content has changed.

________________________________________________________________________________________________________

#####Recommended Movies
```
plugin://script.skin.helper.service/?action=recommendedmovies&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload)]
```
Provides a list of the in progress movies AND recommended movies based on rating.
Note: the reload parameter is needed to auto refresh the widget when the content has changed.

________________________________________________________________________________________________________

#####Recommended Media
```
plugin://script.skin.helper.service/?action=recommendedmedia&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
Provides a list of recommended media (movies, tv shows, music)
Note: You can optionally provide the reload= parameter if you want to refresh the widget on library changes.

________________________________________________________________________________________________________

#####Recent albums
```
plugin://script.skin.helper.service/?action=recentalbums&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreloadmusic)]
```
Provides a list of recently added albums, including the artwork provided by this script as ListItem.Art(xxxx)
Note: You can optionally provide the reload= parameter if you want to refresh the widget on library changes.

Optional argument: browse=true --> will open/browse the album instead of playing it
________________________________________________________________________________________________________

#####Recently played albums
```
plugin://script.skin.helper.service/?action=recentplayedalbums&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreloadmusic)]
```
Provides a list of recently played albums, including the artwork provided by this script as ListItem.Art(xxxx)
Note: You can optionally provide the reload= parameter if you want to refresh the widget on library changes.

Optional argument: browse=true --> will open/browse the album instead of playing it
________________________________________________________________________________________________________

#####Recommended albums
```
plugin://script.skin.helper.service/?action=recommendedalbums&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreloadmusic)]
```
Provides a list of recommended albums, including the artwork provided by this script as ListItem.Art(xxxx)
Note: You can optionally provide the reload= parameter if you want to refresh the widget on library changes.

Optional argument: browse=true --> will open/browse the album instead of playing it
________________________________________________________________________________________________________

#####Recent songs
```
plugin://script.skin.helper.service/?action=recentsongs&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreloadmusic)]
```
Provides a list of recently added songs, including the artwork provided by this script as ListItem.Art(xxxx)
Note: You can optionally provide the reload= parameter if you want to refresh the widget on library changes.
________________________________________________________________________________________________________

#####Recently played songs
```
plugin://script.skin.helper.service/?action=recentplayedsongs&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreloadmusic)]
```
Provides a list of recently played songs, including the artwork provided by this script as ListItem.Art(xxxx)
Note: You can optionally provide the reload= parameter if you want to refresh the widget on library changes.
________________________________________________________________________________________________________

#####Recommended songs
```
plugin://script.skin.helper.service/?action=recommendedsongs&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreloadmusic)]
```
Provides a list of recommended songs, including the artwork provided by this script as ListItem.Art(xxxx)
Note: You can optionally provide the reload= parameter if you want to refresh the widget on library changes.
________________________________________________________________________________________________________

#####Recent Media
```
plugin://script.skin.helper.service/?action=recentmedia&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
Provides a list of recently added media (movies, tv shows, music, tv recordings, musicvideos)
Note: You can optionally provide the reload= parameter if you want to refresh the widget on library changes.


________________________________________________________________________________________________________

#####Similar Movies (because you watched...)
```
plugin://script.skin.helper.service/?action=similarmovies&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
This will provide a list with movies that are similar to a random watched movie from the library.
TIP: The listitem provided by this list will have a property "similartitle" which contains the movie from which this list is generated. That way you can create a "Because you watched $INFO[Container.ListItem.Property(originaltitle)]" label....
Note: You can optionally provide the widgetreload2 parameter if you want to refresh the widget every 10 minutes. If you want to refresh the widget on other circumstances just provide any changing info with the reload parameter, such as the window title or some window Property which you change on X interval.

The above command will create a similar movies listing based on a random watched movie in the library.
If you want to specify the movie to base the request on yourself you can optionally specify the imdb id to the script:

```
plugin://script.skin.helper.service/?action=similarmovies&amp;imdbid=[IMDBID]&amp;limit=[LIMIT]
```

________________________________________________________________________________________________________

#####Similar Tv Shows (because you watched...)
```
plugin://script.skin.helper.service/?action=similarshows&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
This will provide a list with TV shows that are similar to a random in progress show from the library.
TIP: The listitem provided by this list will have a property "similartitle" which contains the movie from which this list is generated. That way you can create a "Because you watched $INFO[Container.ListItem.Property(originaltitle)]" label....
Note: You can optionally provide the widgetreload2 parameter if you want to refresh the widget every 10 minutes. If you want to refresh the widget on other circumstances just provide any changing info with the reload parameter, such as the window title or some window Property which you change on X interval.

The above command will create a similar shows listing based on a random in progress show in the library.
If you want to specify the show to base the request on yourself you can optionally specify the imdb/tvdb id to the script:

```
plugin://script.skin.helper.service/?action=similarshows&amp;imdbid=[IMDBID]&amp;limit=[LIMIT]
```

________________________________________________________________________________________________________

#####Similar Media (because you watched...)
```
plugin://script.skin.helper.service/?action=similarmedia&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
This will provide a list with both Movies and TV shows that are similar to a random in progress movie or show from the library.
TIP: The listitem provided by this list will have a property "similartitle" which contains the movie from which this list is generated. That way you can create a "Because you watched $INFO[Container.ListItem.Property(originaltitle)]" label....
Note: You can optionally provide the widgetreload2 parameter if you want to refresh the widget every 10 minutes. If you want to refresh the widget on other circumstances just provide any changing info with the reload parameter, such as the window title or some window Property which you change on X interval.

The above command will create a similar shows listing based on a random in progress show in the library.
If you want to specify the movie/show to base the request on yourself you can optionally specify the imdb/tvdb id to the script:

```
plugin://script.skin.helper.service/?action=similarshows&amp;imdbid=[IMDBID]&amp;limit=[LIMIT]
```

________________________________________________________________________________________________________

#####Top rated Movies in genre
```
plugin://script.skin.helper.service/?action=moviesforgenre&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
This will provide a list with movies that for a random genre from the library.
TIP: The listitem provided by this list will have a property "genretitle" which contains the movie from which this list is generated.
Note: You can optionally provide the widgetreload2 parameter if you want to refresh the widget every 10 minutes. If you want to refresh the widget on other circumstances just provide any changing info with the reload parameter, such as the window title or some window Property which you change on X interval.

________________________________________________________________________________________________________

#####Top rated tvshows in genre
```
plugin://script.skin.helper.service/?action=showsforgenre&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
This will provide a list with tvshows for a random genre from the library.
TIP: The listitem provided by this list will have a property "genretitle" which contains the movie from which this list is generated.
Note: You can optionally provide the widgetreload2 parameter if you want to refresh the widget every 10 minutes. If you want to refresh the widget on other circumstances just provide any changing info with the reload parameter, such as the window title or some window Property which you change on X interval.

________________________________________________________________________________________________________


#####In progress Media
```
plugin://script.skin.helper.service/?action=inprogressmedia&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload)]
```
Provides a list of all in progress media (movies, tv shows, music, musicvideos)
Note: the reload parameter is needed to auto refresh the widget when the content has changed.


________________________________________________________________________________________________________

#####In progress and Recommended Media
```
plugin://script.skin.helper.service/?action=inprogressandrecommendedmedia&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload)]
```
This combines in progress media and recommended media, usefull to prevent an empty widget when no items are in progress.
Note: the reload parameter is needed to auto refresh the widget when the content has changed.

________________________________________________________________________________________________________

#####Favourite Media
```
plugin://script.skin.helper.service/?action=favouritemedia&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
Provides a list of all media items that are added as favourite (movies, tv shows, songs, musicvideos)
Note: By providing the reload-parameter set to the widgetreload2 property, the widget will be updated every 10 minutes.

________________________________________________________________________________________________________

#####PVR TV Channels widget
```
plugin://script.skin.helper.service/?action=pvrchannels&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
Provides the Kodi TV channels as list content, enriched with the artwork provided by this script (where possible).
Note: By providing the reload-parameter set to the widgetreload2 property, the widget will be updated every 10 minutes.

________________________________________________________________________________________________________

#####PVR Latest Recordings widget
```
plugin://script.skin.helper.service/?action=pvrrecordings&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
Provides the Kodi TV Recordings (sorted by date) as list content, enriched with the artwork provided by this script (where possible).
Note: By providing the reload-parameter set to the widgetreload2 property, the widget will be updated every 10 minutes.


________________________________________________________________________________________________________

#####Favourites
```
plugin://script.skin.helper.service/?action=favourites&amp;limit=[LIMIT]&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
Provides the Kodi favourites as list content.
Note: By providing the reload-parameter set to the widgetreload2 property, the widget will be updated every 10 minutes.


________________________________________________________________________________________________________

##### Unaired episodes
```
plugin://script.skin.helper.service/?action=unairedepisodes&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
Provides a listing for episodes for tvshows in the Kodi library that are airing within the next 2 months.

All listitem properties should be the same as any other episode listitem, 
all properties should be correctly filled with the correct info.
Just treat the widget as any other episode widget and you should have all the details properly set.
If not, let me know ;-)

Listitem.Title --> title of the episode
Listitem.Season, ListItem.Episode --> season/episode of the episode
ListItem.TvShowTitle --> Name of the show
ListItem.Studio --> Network of the show
ListItem.FirstAired --> Airdate for the episode
ListItem.Art(fanart, poster etc.) --> Artwork from the TV show
ListItem.Thumb or Listitem.Art(thumb) --> Episode thumb (if provided by tvdb)

Besides the default Kodi ListItem properties for episodes the following properties will exist:

ListItem.Property(airday) --> The weekday the show will air on the network (e.g. Monday)
ListItem.Property(airtime) --> The time the show will air on the network (e.g. 8:00 PM)
________________________________________________________________________________________________________

##### Next airing episodes
```
plugin://script.skin.helper.service/?action=nextairedepisodes&amp;reload=$INFO[Window(Home).Property(widgetreload2)]
```
Provides the next unaired episode for each tvshow in the library which is airing within the next 2 months.
Difference with the unaired episodes is that it will only show the first airing episode for each show while unaired episodes shows all airing episodes.
Also, the next airing episodes looks 45 days ahead for airing episodes while the unaired episodes looks 120 days ahead.

For the listitem properties, see the "unaired episodes" plugin path.
________________________________________
_______________________________________________________________________________________________________

#####Cast Details
```
plugin://script.skin.helper.service/?action=getcast&amp;movie=[MOVIENAME OR DBID]
plugin://script.skin.helper.service/?action=getcast&amp;tvshow=[TVSHOW NAME OR DBID]
plugin://script.skin.helper.service/?action=getcast&amp;movieset=[MOVIESET NAME OR DBID]
plugin://script.skin.helper.service/?action=getcast&amp;episode=[EPISODE NAME OR DBID]
```
Provides the Cast list for the specified media type as a listing.
Label = Name of the actor
Label2 = Role
Icon = Thumb of the actor

You can use the name of the item or the DBID to perform the lookup.
There will also a Window Property be set when you use the above query to the script: SkinHelper.ListItemCast --> It will return the cast list seperated by [CR]

Optional parameter: downloadthumbs=true --> will auto download any missing actor thumbs from IMDB


#####Browse Genres
```
plugin://script.skin.helper.service/?action=browsegenres&amp;type=movie&amp;limit=1000
plugin://script.skin.helper.service/?action=browsegenres&amp;type=tvshow&amp;limit=1000
```
Provides the genres listing for movies or tvshows with artwork properties from movies/shows with the genre so you can build custom genre icons.

ListItem.Art(poster.X) --> poster for movie/show X (start counting at 0) in the genre

ListItem.Art(fanart.X) --> fanart for movie/show X (start counting at 0) in the genre


For each genre, only 5 movies/tvshows are retrieved.
Supported types: movie, tvshow (will return 5 items from the library for each genre)
If you use randommovie or randomtvshow as type the library items will be randomized


#####Jump to alphabet list for media views
This little workaround let's you add an alphabet strip in your media view to quickly jump to a certain sort letter in the list.
All you have to do is include a panel inside your media view with the following path:

plugin://script.skin.helper.service/?action=alphabet&amp;reload=$INFO[Container.NumItems]

This will present you an alphabet listing. If you click a letter, the listing will jump to ther chosen letter.

Example skin XML code:

```xml
<control type="panel" id="6000">
    <width>40</width>
    <right>0</right>
    <height>100%</height>
    <orientation>vertical</orientation>
    <itemlayout height="41" width="40">
        <control type="label">
            <label>$INFO[ListItem.Label]</label>
            <textcolor>white</textcolor>
            <animation effect="fade" start="100" end="20" time="0" condition="!IsEmpty(ListItem.Property(NotAvailable))">Conditional</animation>
        </control>
        <control type="label">
            <label>$INFO[ListItem.Label]</label>
            <textcolor>blue</textcolor>
            <visible>StringCompare(ListItem.Label,Container.ListItem.SortLetter)</visible>
        </control>
    </itemlayout>
    <focusedlayout height="41" width="40">
        <control type="label">
            <label>$INFO[ListItem.Label]</label>
            <textcolor>green</textcolor>
            <animation effect="fade" start="100" end="20" time="0" condition="!IsEmpty(ListItem.Property(NotAvailable))">Conditional</animation>
        </control>
    </focusedlayout>
    <content>plugin://script.skin.helper.service/?action=alphabet&amp;reload=$INFO[Container.NumItems]</content>
</control>
```

________________________________________________________________________________________________________
________________________________________________________________________________________________________

### Smart shortcuts feature
This feature is introduced to be able to provide quick-access shortcuts to specific sections of Kodi, such as user created playlists and favourites and entry points of some 3th party addons such as Emby and Plex. What it does is provide some Window properties about the shortcut. It is most convenient used with the skin shortcuts script but can offcourse be used in any part of your skin. The most important behaviour of the smart shortcuts feature is that is pulls images from the library path so you can have content based backgrounds.


________________________________________________________________________________________________________

##### Smart shortcuts for playlists
Will only be available if this Skin Bool is true --> SmartShortcuts.playlists

| property 			| description |
| :----------------------------	| :----------- |
| Window(Home).Property(playlist.X.label) | Title of the playlist|
| Window(Home).Property(playlist.X.action) | Path of the playlist|
| Window(Home).Property(playlist.X.content) | Contentpath (without activatewindow) of the playlist, to display it's content in widgets.|
| Window(Home).Property(playlist.X.image) | Rotating fanart of the playlist|
--> replace X with the item count, starting at 0.


________________________________________________________________________________________________________


##### Smart shortcuts for Kodi Favourites
Will only be available if this Skin Bool is true --> SmartShortcuts.favorites

Note that only favourites will be processed that actually contain video/audio content.

| property 			| description |
| :----------------------------	| :----------- |
| Window(Home).Property(favorite.X.label) | Title of the favourite|
| Window(Home).Property(favorite.X.action) | Path of the favourite|
| Window(Home).Property(favorite.X.content) | Contentpath (without activatewindow) of the favourite, to display it's content in widgets.|
| Window(Home).Property(favorite.X.image) | Rotating fanart of the favourite|
--> replace X with the item count, starting at 0.


________________________________________________________________________________________________________



##### Smart shortcuts for Plex addon (plugin.video.plexbmc)
Will only be available if this Skin Bool is true --> SmartShortcuts.plex

Note that the plexbmc addon must be present on the system for this to function.

| property 			| description |
| :----------------------------	| :----------- |
| Window(Home).Property(plexbmc.X.title) | Title of the Plex collection|
| Window(Home).Property(plexbmc.X.path) | Path of the Plex collection|
| Window(Home).Property(plexbmc.X.content) | Contentpath (without activatewindow) of the Plex collection, to display it's content in widgets.|
| Window(Home).Property(plexbmc.X.image) | Rotating fanart of the Plex collection|
| Window(Home).Property(plexbmc.X.type) | Type of the Plex collection (e.g. movies, tvshows)|
| Window(Home).Property(plexbmc.X.recent) | Path to the recently added items node of the Plex collection|
| Window(Home).Property(plexbmc.X.recent.content) | Contentpath to the recently added items node of the Plex collection (for widgets)|
| Window(Home).Property(plexbmc.X.recent.image) | Rotating fanart of the recently added items node|
| Window(Home).Property(plexbmc.X.ondeck) | Path to the in progress items node of the Plex collection|
| Window(Home).Property(plexbmc.X.ondeck.content) | Contentpath to the in progress items node of the Plex collection (for widgets)|
| Window(Home).Property(plexbmc.X.ondeck.image) | Rotating fanart of the in progress items node|
| Window(Home).Property(plexbmc.X.unwatched) | Path to the in unwatched items node of the Plex collection|
| Window(Home).Property(plexbmc.X.unwatched.content) | Contentpath to the unwatched items node of the Plex collection (for widgets)|
| Window(Home).Property(plexbmc.X.unwatched.image) | Rotating fanart of the unwatched items node|
| |
| Window(Home).Property(plexbmc.channels.title) | Title of the Plex Channels collection|
| Window(Home).Property(plexbmc.channels.path) | Path to the Plex Channels|
| Window(Home).Property(plexbmc.channels.content) | Contentpath to the Plex Channels (for widgets)|
| Window(Home).Property(plexbmc.channels.image) | Rotating fanart of the Plex Channels|
| |
| Window(Home).Property(plexfanartbg) | A global fanart background from plex sources|
--> replace X with the item count, starting at 0.



________________________________________________________________________________________________________



##### Smart shortcuts for Emby addon (plugin.video.emby)
Will only be available if this Skin Bool is true --> SmartShortcuts.emby

Note that the Emby addon must be present on the system for this to function.

| property 			| description |
| :----------------------------	| :----------- |
| Window(Home).Property(emby.nodes.X.title) | Title of the Emby collection|
| Window(Home).Property(emby.nodes.X.path) | Path of the Emby collection|
| Window(Home).Property(emby.nodes.X.content) | Contentpath of the Emby collection (for widgets)|
| Window(Home).Property(emby.nodes.X.image) | Rotating Fanart of the Emby collection|
| Window(Home).Property(emby.nodes.X.type) | Type of the Emby collection (e.g. movies, tvshows)|
| |
| Window(Home).Property(emby.nodes.X.recent.title) | Title of the recently added node for the Emby collection|
| Window(Home).Property(emby.nodes.X.recent.path) | Path of the recently added node for the Emby collection|
| Window(Home).Property(emby.nodes.X.recent.content) | Contentpath of the recently added node for the Emby collection|
| Window(Home).Property(emby.nodes.X.recent.image) | Rotating Fanart of the recently added node for the Emby collection|
| |
| Window(Home).Property(emby.nodes.X.unwatched.title) | Title of the unwatched node for the Emby collection|
| Window(Home).Property(emby.nodes.X.unwatched.path) | Path of the unwatched node for the Emby collection|
| Window(Home).Property(emby.nodes.X.unwatched.content) | Contentpath of the unwatched node for the Emby collection|
| Window(Home).Property(emby.nodes.X.unwatched.image) | Rotating Fanart of the unwatched node for the Emby collection|
| |
| Window(Home).Property(emby.nodes.X.inprogress.title) | Title of the inprogress node for the Emby collection|
| Window(Home).Property(emby.nodes.X.inprogress.path) | Path of the inprogress node for the Emby collection|
| Window(Home).Property(emby.nodes.X.inprogress.content) | Contentpath of the inprogress node for the Emby collection|
| Window(Home).Property(emby.nodes.X.inprogress.image) | Rotating Fanart of the inprogress node for the Emby collection|
| |
| Window(Home).Property(emby.nodes.X.recentepisodes.title) | Title of the recent episodes node for the Emby collection|
| Window(Home).Property(emby.nodes.X.recentepisodes.path) | Path of the recent episodes node for the Emby collection|
| Window(Home).Property(emby.nodes.X.recentepisodes.content) | Contentpath of the recent episodes node for the Emby collection|
| Window(Home).Property(emby.nodes.X.recentepisodes.image) | Rotating Fanart of the recent episodes node for the Emby collection|
| |
| Window(Home).Property(emby.nodes.X.nextepisodes.title) | Title of the next episodes node for the Emby collection|
| Window(Home).Property(emby.nodes.X.nextepisodes.path) | Path of the next episodes node for the Emby collection|
| Window(Home).Property(emby.nodes.X.nextepisodes.content) | Contentpath of the next episodes node for the Emby collection|
| Window(Home).Property(emby.nodes.X.nextepisodes.image) | Rotating Fanart of the next episodes node for the Emby collection|
| |
| Window(Home).Property(emby.nodes.X.inprogressepisodes.title) | Title of the in progress episodes node for the Emby collection|
| Window(Home).Property(emby.nodes.X.inprogressepisodes.path) | Path of the in progress episodes node for the Emby collection|
| Window(Home).Property(emby.nodes.X.inprogressepisodes.content) | Contentpath of the in progress episodes node for the Emby collection|
| Window(Home).Property(emby.nodes.X.inprogressepisodes.image) | Rotating Fanart of the in progress episodes node for the Emby collection|



________________________________________________________________________________________________________



##### Smart shortcuts for Netflix addon (plugin.video.flix2kodi)
Will only be available if this Skin Bool is true --> SmartShortcuts.netflix

Note that the Flix2Kodi addon must be present on the system for this to function.

| property 			| description |
| :----------------------------	| :----------- |
| Window(Home).Property(netflix.generic.title) | Title of the main Netflix entry|
| Window(Home).Property(netflix.generic.path) | Path of the main Netflix entry|
| Window(Home).Property(netflix.generic.content) | Contentpath of the main Netflix entry (for widgets)|
| Window(Home).Property(netflix.generic.image) | Rotating Fanart from Netflix addon|
| |
| Window(Home).Property(netflix.generic.mylist.title) | Title of the Netflix My List entry|
| Window(Home).Property(netflix.generic.mylist.path) | Path of the Netflix My List entry|
| Window(Home).Property(netflix.generic.mylist.content) | Contentpath of the Netflix My List entry (for widgets)|
| Window(Home).Property(netflix.generic.mylist.image) | Rotating Fanart from Netflix My List entry|
| |
| Window(Home).Property(netflix.generic.suggestions.title) | Title of the Netflix Suggestions entry|
| Window(Home).Property(netflix.generic.suggestions.path) | Path of the Netflix Suggestions entry|
| Window(Home).Property(netflix.generic.suggestions.content) | Contentpath of the Netflix Suggestions entry (for widgets)|
| Window(Home).Property(netflix.generic.suggestions.image) | Rotating Fanart from Netflix Suggestions entry|
| |
| Window(Home).Property(netflix.generic.inprogress.title) | Title of the Netflix Continue Watching entry|
| Window(Home).Property(netflix.generic.inprogress.path) | Path of the Netflix Continue Watching entry|
| Window(Home).Property(netflix.generic.inprogress.content) | Contentpath of the Netflix Continue Watching entry (for widgets)|
| Window(Home).Property(netflix.generic.inprogress.image) | Rotating Fanart from Netflix Continue Watching entry|
| |
| Window(Home).Property(netflix.generic.recent.title) | Title of the Netflix Latest entry|
| Window(Home).Property(netflix.generic.recent.path) | Path of the Netflix Latest entry|
| Window(Home).Property(netflix.generic.recent.content) | Contentpath of the Netflix Latest entry (for widgets)|
| Window(Home).Property(netflix.generic.recent.image) | Rotating Fanart from Netflix Latest entry|
| |
| Window(Home).Property(netflix.movies.title) | Title of the Netflix Movies entry|
| Window(Home).Property(netflix.movies.path) | Path of the Netflix Movies entry|
| Window(Home).Property(netflix.movies.content) | Contentpath of the Netflix Movies entry (for widgets)|
| Window(Home).Property(netflix.movies.image) | Rotating Fanart from Netflix Movies entry|
| |
| Window(Home).Property(netflix.movies.mylist.title) | Title of the Netflix Movies Mylist entry|
| Window(Home).Property(netflix.movies.mylist.path) | Path of the Netflix Movies Mylist entry|
| Window(Home).Property(netflix.movies.mylist.content) | Contentpath of the Netflix Movies Mylist entry (for widgets)|
| Window(Home).Property(netflix.movies.mylist.image) | Rotating Fanart from Netflix Movies Mylist entry|
| |
| Window(Home).Property(netflix.movies.suggestions.title) | Title of the Netflix Movies suggestions entry|
| Window(Home).Property(netflix.movies.suggestions.path) | Path of the Netflix Movies suggestions entry|
| Window(Home).Property(netflix.movies.suggestions.content) | Contentpath of the Netflix Movies suggestions entry (for widgets)|
| Window(Home).Property(netflix.movies.suggestions.image) | Rotating Fanart from Netflix Movies suggestions entry|
| |
| Window(Home).Property(netflix.movies.genres.title) | Title of the Netflix Movies genres entry|
| Window(Home).Property(netflix.movies.genres.path) | Path of the Netflix Movies genres entry|
| Window(Home).Property(netflix.movies.genres.content) | Contentpath of the Netflix Movies genres entry (for widgets)|
| Window(Home).Property(netflix.movies.genres.image) | Rotating Fanart from Netflix Movies genres entry|
| |
| Window(Home).Property(netflix.movies.recent.title) | Title of the Netflix Latest movies entry|
| Window(Home).Property(netflix.movies.recent.path) | Path of the Netflix Latest movies entry|
| Window(Home).Property(netflix.movies.recent.content) | Contentpath of the Netflix Latest movies entry (for widgets)|
| Window(Home).Property(netflix.movies.recent.image) | Rotating Fanart from Netflix Latest movies entry|
| |
| Window(Home).Property(netflix.tvshows.title) | Title of the Netflix tvshows entry|
| Window(Home).Property(netflix.tvshows.path) | Path of the Netflix tvshows entry|
| Window(Home).Property(netflix.tvshows.content) | Contentpath of the Netflix tvshows entry (for widgets)|
| Window(Home).Property(netflix.tvshows.image) | Rotating Fanart from Netflix tvshows entry|
| |
| Window(Home).Property(netflix.tvshows.mylist.title) | Title of the Netflix tvshows Mylist entry|
| Window(Home).Property(netflix.tvshows.mylist.path) | Path of the Netflix tvshows Mylist entry|
| Window(Home).Property(netflix.tvshows.mylist.content) | Contentpath of the Netflix tvshows Mylist entry (for widgets)|
| Window(Home).Property(netflix.tvshows.mylist.image) | Rotating Fanart from Netflix tvshows Mylist entry|
| |
| Window(Home).Property(netflix.tvshows.suggestions.title) | Title of the Netflix tvshows suggestions entry|
| Window(Home).Property(netflix.tvshows.suggestions.path) | Path of the Netflix tvshows suggestions entry|
| Window(Home).Property(netflix.tvshows.suggestions.content) | Contentpath of the Netflix tvshows suggestions entry (for widgets)|
| Window(Home).Property(netflix.tvshows.suggestions.image) | Rotating Fanart from Netflix tvshows suggestions entry|
| |
| Window(Home).Property(netflix.tvshows.genres.title) | Title of the Netflix tvshows genres entry|
| Window(Home).Property(netflix.tvshows.genres.path) | Path of the Netflix tvshows genres entry|
| Window(Home).Property(netflix.tvshows.genres.content) | Contentpath of the Netflix tvshows genres entry (for widgets)|
| Window(Home).Property(netflix.tvshows.genres.image) | Rotating Fanart from Netflix tvshows genres entry|
| |
| Window(Home).Property(netflix.tvshows.recent.title) | Title of the Netflix Latest tvshows entry|
| Window(Home).Property(netflix.tvshows.recent.path) | Path of the Netflix Latest tvshows entry|
| Window(Home).Property(netflix.tvshows.recent.content) | Contentpath of the Netflix Latest tvshows entry (for widgets)|
| Window(Home).Property(netflix.tvshows.recent.image) | Rotating Fanart from Netflix Latest tvshows entry|
| |



________________________________________________________________________________________________________
________________________________________________________________________________________________________

### Use with skin shortcuts script
This addon is designed to fully work together with the skinshortcuts script, so it will save you a lot of time because the script provides skinshortcuts with all the info to display contents.
No need to manually skin all those window properties in your skin, just a few lines in your overrides file is enough.

#### Display Smart Shortcuts in skin shortcuts listing

When the smart shortcuts are used together with skinshortcuts it will auto assign the icon and background with rotating fanart and both the widget and submenu (if needed) are assigned by default. The user just adds the shortcut and is all set.

To display the complete listing of Smart Shortcuts in your skin, place the following line in your overrides file, in the groupings section:
```xml
<shortcut label="Smart Shortcuts" type="32010">||BROWSE||script.skin.helper.service/?action=smartshortcuts</shortcut>
```

full example:
```xml
<overrides>
	<groupings>
		<shortcut label="$ADDON[script.skin.helper.service 32062]" type="32010">||BROWSE||script.skin.helper.service/?action=smartshortcuts</shortcut>
	</groupings>
</overrides>	
```
Offcourse you can use a condition parameter to only show the smart shortcuts entry if it's enabled in your skin.
You can also choose to use display the smart shortcuts to be used as widgets, in that case include this line in your overrides.xml file:
```xml
<widget label="Smart Shortcuts" type="32010">||BROWSE||script.skin.helper.service/?action=smartshortcuts</widget>
```

#### Auto display Backgrounds provided by the script in skinshortcuts selector

You can choose to show all backgrounds (including those for smart shortcuts) that are provided by this addon in the skinshortcuts backgrounds selector.

To display all backgrounds automatically in skinshorts you only have to include the line below in your overrides file:
```xml
<background label="smartshortcuts">||BROWSE||plugin://script.skin.helper.service/?action=backgrounds</background>
```

Note: You can still use the default skinshortcuts method to assign a default background to a item by labelID or defaultID.
In that case use the full $INFO path of the background. For example, to assign the "all movies" background to the Movies shortcut:
```xml
<backgrounddefault defaultID="movies">$INFO[Window(Home).Property(SkinHelper.AllMoviesBackground)]</backgrounddefault>
```
For more info, see skinshortcut's documentation.


#### Auto display widgets in skinshortcuts

Coding all widgets in your skin can be a pain, especially to keep up with all the fancy scripts like extendedinfo and library data provider. This addon, combined with skinshortcuts can make things a little easier for you...
By including just one line of code in your skinshortcuts override.xml you can display a whole bunch of widgets, ready to be selected by the user:

```xml
<widget label="Widgets" type="32010">||BROWSE||script.skin.helper.service/?action=widgets&amp;path=skinplaylists,librarydataprovider,scriptwidgets,extendedinfo,smartshortcuts,pvr,smartishwidgets</widget>
```

This will display a complete list of widgets available to select if the user presses the select widget button in skinshortcuts. In the path parameter you can specify which widgettypes should be listed. The widgets will be displayed in the order of which you type them as parameters (comma separated). You can also leave out the whole path parameterm in that case all available widgets will be displayed.

Currently available widgets (more to be added soon):

skinplaylist --> all playlists that are stored in "yourskin\extras\widgetplaylists" or "yourskin\playlists" or "yourskin\extras\playlists"

librarydataprovider --> all widgets that are provided by the Library Data Provider script

scriptwidgets --> the special widgets that are provided by this addon, like favourites and favourite media etc.

extendedinfo --> All widgets that are provided by the Extended info script

smartshortcuts --> all smartshortcuts

pvr --> pvr widgets provided by the script

smartishwidgets --> widget supplied by the smartish widgets addon

favourites --> any browsable nodes in the user's favourites that can be used as widget


Note: the script will auto check the existence of the addons on the system so no need for complex visibility conditions in your skin.



________________________________________________________________________________________________________
________________________________________________________________________________________________________


