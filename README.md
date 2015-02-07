# Project plan

General description of what you are doing and how you are doing that (what kinds of views, models are needed), how they relate to each other, and what is the implementation order and timetable.

## Requirements

* South 0.8.4 - Handles database migrations, good for development as fixtures are troublesome.
* django.contrib.comments 1.5 - Adds comments functionality
* crispy-forms 1.4.0 - Eases the use of forms together with bootstrap
* fluent-comments 0.9.2 - Adds AJAX comments functionality
* Haystack 2.1.0 - Search engine
* Woosh 2.5.6 - Search engine indexing database
* Requests 2.1.0 - Who doesn't need requests?

## Features

* Authentication
    * Our authentication scheme will include login, logout, and registration to the service. These basic features should be easy to implement using *[django.aut*h](https://docs.djangoproject.com/en/dev/topics/auth/).

* Mandatory features of Laulutunkki
    * Add, remove and modify songs. The modifications are transmitted to song administrators.
    * A separate classification for old songs - meaning the songs that are not sung anymore or are not timely anymore.
    * Classification of songs e.g. according to association with drinks: water songs, schnaps songs, wine songs, etc.
    * Search functionality for songs according to name, class, etc.
    * Song booklet generation: pick songs and their order in the booklet.
    * Save functionality for song booklets for future use, including the possibility to upload the final booklet, with pictures and everything, in pdf-format.
    * Search functionality for old song booklets.
    * Comment functionality on a per song level (only within the Laulutunkki).
    * Song statistics e.g. in how many song booklets has the song appeared etc.
    * Gravatar integration
        * A user can synchronize an avatar from the Gravatar service.

* Non-mandatory features of Laulutunkki
    * Public link to song booklets
    * Share song booklet
        * A user can share and like old song booklets and songs.
        * Use case: a user can generate a song booklet and share it e.g. in Twitter or Facebook.
    * Integration with an image service API
        * Use case: search themed photos for the song booklet pdf. (Flickr-api)
    * 3rd party login
        * Login integration with e.g. Facebook
        * OpenID, then Google account can be used
    * Use of AJAX
        * Why not? Would be silly not to.

## Models

### Songs

* name
* lyrics
* extra verses
* categories
* comments

### Categories

* name
* description

### Song booklets

* pages
* author
* name
* images
* description
* creation date
* events

### Pages

* songs
* order

### Events

* booklet
* extra-songs
* date

### Changes

* song
* user
* new lyrics
* description
* is extra verse

## Views

* Front page view
    * Contains a description of the service as well as the fields required for login
* Authentication view
    * Login view (Django’s internal)
    * Register view (Django’s internal)
    * Profile view
* Administrator view
    * Django’s internal
    * Additional scripts to incorporate song and song booklet administration functionalities.
* Search view
    * Possibility search song booklets or songs by name, event, category, etc.
    * List search results
* Booklet create/edit view
    * Song booklet creation and editing: add, remove, and order songs.
    * Possibility to search associated photos.
* Booklet view
    * View booklet contents and associated comments.
    * Possibility to share, like, etc.
* Song create/edit view
* Song view
    * View song information and associated comments.
    * Possibility to share, like, etc.

## Preliminary timetable

We plan to have all of the mandatory functionalities implemented by Friday 1.2.2014. This leaves us with two weeks of time for testing and implementing the non-mandatory features.

### Preliminary implementation order

1. Mandatory functionality, AJAX
    1. Creating and editing for songs
    2. Creating and editing for booklets
    3. Viewing songs and booklets, including AJAX
    4. Admin view changes for accepting edits
2. Public links and social media sharing
3. Third party login (e.g Facebook / Google)
4. Image search from third party (e.g flicker)
5. Gravatar integration
6. Basic authentication
7. Authentication integration with third party software
