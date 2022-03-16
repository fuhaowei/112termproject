import copy
import json
import math
import os
import random

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


##########################################
# Backend calculations for similarity values and recommendation algo
##########################################

#helper function that does auth and data pulling
def backEnd(app):
    # data pulling process written by myself, looked at documentation to see what calls to make
    # and the results of those calls https://spotipy.readthedocs.io/en/2.18.0/

    # environment set up here modified from
    # https://towardsdatascience.com/using-python-to-refine-your-spotify-recommendations-6dc08bcf408e
    # my client ID and client Secret
    user = ""

    #set my environment as this, set redirect link as well. local host helps it
    #pop up on the browser. 
    os.environ['SPOTIPY_CLIENT_ID']= app.c_id
    os.environ['SPOTIPY_CLIENT_SECRET']= app.c_s
    os.environ['SPOTIPY_REDIRECT_URI']='http://localhost:8888/callback'

    # setting the scope for what I want to pull out of the API, scopes from spotify ref
    scope = 'user-top-read,playlist-modify-public,user-modify-playback-state,user-read-playback-state,user-modify-playback-state, playlist-read-private, playlist-read-collaborative'

    #auth process written by myself
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    client_credentials_manager = SpotifyClientCredentials()
    app.sp = sp
    app.sp2 = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    #sp gives me the Spotify token in spotipy form to access API
    userInfo = app.sp.current_user()
    app.userID = userInfo["id"]
    app.userName = userInfo["display_name"]
    print(f"hey. ready for me to read your personality {app.userName}?")
    # gives me processed data I want
    finalUserSongList = getUserSongsData(sp,app)
    app.finalUserSongList = finalUserSongList
    app.allPlaylistSongList = getPlaylistData(sp)

    # gives me the average score for each category for the user
    app.userData = findAverageUserScore(finalUserSongList)

    allPlaylistSongRatings = []
    # category 0-1 songs
    
    variances = {
        "ESFP": 0,
        "ISFP": 0,
        "ESTP": 0,
        "ISTP": 0,
        "ENFP": 0,
        "INFP": 0,
        "ENFJ": 0,
        "INFJ": 0,
        "ENTP": 0,
        "INTP": 0,
        "ENTJ": 0,
        "INTJ": 0,
        "ESTJ": 0,
        "ISTJ": 0,
        "ESFJ": 0,
        "ISFJ": 0,
    }

    for personality in variances:
        tempDict = {
                    "danceability": [],
                    "energy":[],
                    "speechiness": [],
                    "acousticness": [],
                    "instrumentalness": [],
                    "liveness": [],
                    "valence": [],  
                    "tempo":[]
                }
        
        for song in app.allPlaylistSongList[personality]:
            tempDict["danceability"].append(song.danceability)
            tempDict["energy"].append(song.energy)
            tempDict["speechiness"].append(song.speechiness)
            tempDict["acousticness"].append(song.acousticness)
            tempDict["instrumentalness"].append(song.instrumentalness)
            tempDict["liveness"].append(song.liveness)
            tempDict["valence"].append(song.valence)
            tempDict["tempo"].append(song.tempo/190)

        for feature in tempDict:
            variances[personality] += variance(tempDict[feature], app.userData[feature])

    rankingsList = []

    for personality in variances:
        rankingsList.append(variances[personality])
    
    rankingsList.sort()

    app.rankingList = rankingsList
    app.variances = variances

    findWinner(app)
    songRec(app)
    storeDislikedSongs(app)

#helper function for finding the closest personality
def findWinner(app):
    app.winner = ""
    for name in app.variances:
        if app.variances[name]== app.rankingList[app.index]:
            app.winner = name
    
#song recommendation algorithm
def songRec(app):

    #open likes file, make sure that only one copy of each
    f = open("likes.txt", "r")
    likeList = f.readlines()
    likes = set(likeList)
    app.likes = []
    for temp in likes:
        app.likes.append(temp[:36])
    f.close()

    #loads liked images for my app
    app.likedSongsPics = [] 
    if len(app.likes) != 0:
        for i in app.likes:
            temp = app.sp.track(i[14:36])
            url = temp['album']['images'][1]['url']
            image= app.loadImage(url)
            app.likedSongsPics.append(image)

    #open dislike file, make sure only one copy of each
    f = open('dislikes.txt', "r")
    dislikeList = f.readlines()
    dislikes = set(dislikeList)
    app.dislikes = []
    for temp in dislikes:
        app.dislikes.append(temp[:36])
    app.dislikedSongNames = []
    #creates song names for dislikes songs
    for song in app.dislikes:
        app.dislikedSongNames.append(app.sp.track(song)["name"])
    f.close()
    
    #different places to store the seeds I want to generate my recos by
    app.songReccos = []
    seed_artists = []
    seed_tracks = []
    for personality in app.allPlaylistSongList:
        if personality == app.winner:
            for song in app.allPlaylistSongList[personality]:
                seed_tracks.append(song.trackId)
                seed_artists.append(song.trackArtist)

    index = random.randint(0,21)
    app.songReccos = app.sp.recommendations(seed_tracks = seed_tracks[index:index+3],limit = 80)

    #dict to store my variances
    app.recoVariances = {}

    #uri for each song in list to call audio features
    tempSongsURI = []
    for song in app.songReccos['tracks']:
        tempSongsURI.append(song['uri'])

    #called
    dataToFilter = app.sp.audio_features(tempSongsURI)
    
    userAve = (app.userData["danceability"],app.userData["energy"],\
            app.userData["speechiness"],app.userData["acousticness"],app.userData["liveness"],\
                app.userData["valence"],app.userData["tempo"]/190)

    for song in dataToFilter:
        recSong = (song["danceability"],song["energy"],\
            song["speechiness"],song["acousticness"],song["liveness"],\
                song["valence"],song["tempo"]/190)

        #eucld distance algo
        eucldDist = math.sqrt(sum([(user - rec) ** 2 for user, rec in zip(userAve, recSong)]))
        app.recoVariances[song["id"]] = eucldDist

    app.variances = []
    for key in app.recoVariances:
        app.variances.append(app.recoVariances[key])

    #sort and make sure the closest one is presented
    sorted(app.variances, reverse = True)
    app.reccosTotal = []

    for song in app.variances:
        if song in app.dislikes:
            #make sure dislike is kicked out, new one generated
            temp = app.sp.recommendations(seed_tracks = seed_tracks[index:index+3],limit = 1)
            app.reccosTotal.append(temp['track'][name], temp['track']['uri'])
        else:
            for key in app.recoVariances:
                if app.recoVariances[key] == song:
                    temp2 = app.sp.track(key)
                    app.reccosTotal.append((temp2["name"], f"spotify:track:{key}"))
    loadSongs(app)

#load the songs into the storage function
def loadSongs(app):
    app.reccos = app.reccosTotal[app.counter:app.counter+4]
            
#refresh func when user presses M
def storeLikedSongs(app):
    f = open("likes.txt", "r")
    likeList = f.readlines()
    likes = set(likeList)
    app.likes = list(likes)
    f.close()

    app.likedSongsPics = [] 
    if len(app.likes) != 0:
        for i in app.likes:
            temp = app.sp.track(i[14:36])
            url = temp['album']['images'][1]['url']
            image= app.loadImage(url)
            app.likedSongsPics.append(image)

#refresh func when user presses M
def storeDislikedSongs(app):
    f = open('dislikes.txt', "r")
    dislikeList = f.readlines()
    dislikes = set(dislikeList)
    app.dislikes = []
    for temp in dislikes:
        app.dislikes.append(temp[:36])
    f.close()
    
    app.dislikedSongsPics = []
    if len(app.dislikes) != 0:
        for song in app.dislikes:
            temp = app.sp.track(song[14:36])
            url = temp['album']['images'][1]['url']
            image= app.loadImage(url)
            app.dislikedSongsPics.append(image)

    app.dislikedSongNames = []
    for song in app.dislikes:
        app.dislikedSongNames.append(app.sp.track(song)["name"])

# helper function that takes in auth token, and then returns a list of song objects with data already filled in
def getUserSongsData(sp,app):

    # defining my song object. 
    class Song(object):
            def __init__(self,trackName,trackArtist,trackId):
                Song.trackName = trackName
                Song.trackArtist = trackArtist
                Song.trackId = trackId
                Song.danceability = 0
                Song.energy = 0
                Song.key = 0
                Song.loudness = 0
                Song.mode = 0
                Song.speechiness = 0
                Song.acousticness = 0
                Song.instrumentalness = 0
                Song.liveness = 0
                Song.valence = 0
                Song.tempo = 0

    #gets the results for my user's top tracks, this is long term, takes top 40
    userTempList = sp.current_user_top_tracks(limit=40,offset=0,time_range='long_term')
    temp = sp.current_user_top_tracks(limit=40,offset=0,time_range='short_term')

    #my formatted data
    userSongList = []

    for song in range(40):
        userSong = Song(None,None,None)
        userSongList.append(userSong)

    for newsong in range(40):
        tempName = userTempList['items'][newsong]["name"]
        tempArtist = userTempList['items'][newsong]["artists"][0]["uri"]
        tempId = userTempList['items'][newsong]["id"]
        userSongList[newsong].trackName = tempName
        userSongList[newsong].trackId = tempId
        userSongList[newsong].trackArtist = tempArtist


    for userSong in userSongList:
        tempUserFeatures = sp.audio_features(userSong.trackId)
        userSong.danceability = tempUserFeatures[0]["danceability"]
        userSong.energy = tempUserFeatures[0]["energy"]
        userSong.key = tempUserFeatures[0]["key"]
        userSong.loudness = tempUserFeatures[0]["loudness"]
        userSong.mode = tempUserFeatures[0]["mode"]
        userSong.speechiness = tempUserFeatures[0]["speechiness"]
        userSong.acousticness = tempUserFeatures[0]["acousticness"]
        userSong.instrumentalness = tempUserFeatures[0]["instrumentalness"]
        userSong.liveness = tempUserFeatures[0]["liveness"]
        userSong.valence = tempUserFeatures[0]["valence"]
        userSong.tempo = tempUserFeatures[0]["tempo"]
        
        
    # call the playlist, access the songs avail. 
    return userSongList

# helper function that takes in auth token and returns me data struct containing the data for all the playlists
def getPlaylistData(sp):

    # playlist URI for different personality types stored in a dict
    # playlists are public playlists from user (spotify:user:annieboyse)
    playListURIs = {
        "ESFP": "spotify:playlist:4pi2j0t6uT4YtBXnT2gAa4",
        "ISFP": "spotify:playlist:4phCnknfZ5LhEYmArdUJXv",
        "ESTP": "spotify:playlist:4OnGyVyLPdmBev3HBT0tYu",
        "ISTP": "spotify:playlist:3RqQRynMWJoP9JkEc7YrOE",
        "ENFP": "spotify:playlist:5GQ1YxFYw0pxC9LmAVcCXZ",
        "INFP": "spotify:playlist:5TW1TKTM7Q99Z3p4NvtReA",
        "ENFJ": "spotify:playlist:6th4JW4Dky7UjeEhHuQeQd",
        "INFJ": "spotify:playlist:2fHK41mb288anu6dQDNuB8",
        "ENTP": "spotify:playlist:4RdPgciqwk1Pzo8OXKVCZB",
        "INTP": "spotify:playlist:3g57PuPnoAVo1lfJhQZeDj",
        "ENTJ": "spotify:playlist:2L6Dxf2WAqoIQX50Zg4wFR",
        "INTJ": "spotify:playlist:0qBVUmdHvl7vaQnNtQatlC",
        "ESTJ": "spotify:playlist:1KIdUNGcJLOPTkewJimsQ7",
        "ISTJ": "spotify:playlist:00Ni0Ve2XMw43uPE6g73RN",
        "ESFJ": "spotify:playlist:3aVsLjJaHunrEhlVRp9AxT",
        "ISFJ": "spotify:playlist:3ZXgVNRlimnET5ceMz7XXQ",
    }

    #going to be the dict that is returned 
    playListSongObjs = {}

    #defining my song object
    class Song(object):
            def __init__(self,trackName,trackArtist,trackId):
                Song.trackName = trackName
                Song.trackArtist = trackArtist
                Song.trackId = trackId
                Song.danceability = 0
                Song.energy = 0
                Song.key = 0
                Song.loudness = 0
                Song.mode = 0
                Song.speechiness = 0
                Song.acousticness = 0
                Song.instrumentalness = 0
                Song.liveness = 0
                Song.valence = 0
                Song.tempo = 0

    # for each personality type  
    for key in playListURIs:

        #temp stores for what I need
        playlistTempList = []
        playlistSongList = []

        #temp stores of all my trackIDs for that personality type
        trackIds = []

        # getting the tracks, json response from API
        playlistTempList = sp.playlist(playListURIs[key])

        #flexible length depending on the number of tracks that playlist has
        length = len(playlistTempList["tracks"]["items"])-1
        
        
        #adding my song objects to the temp list for this playlist        
        for i in range(length):
            playlistSong = Song(None, None, None)
            playlistSongList.append(playlistSong)

        #adding data into them, preparing my trackId list as well
        for i in range(length):
            playlistSongList[i].trackName = playlistTempList['tracks']['items'][i]["track"]["name"]
            playlistSongList[i].trackArtist = playlistTempList['tracks']['items'][i]["track"]["artists"][0]["uri"]
            playlistSongList[i].trackId = playlistTempList['tracks']['items'][i]["track"]["uri"]
            trackIds.append(playlistSongList[i].trackId)

        #json response of all audio features of every song in that playlist
        tempPlaylistFeature = sp.audio_features(trackIds)

        #for everysong in the playlist, add the data in for audio features
        for i in range(length):        
            playlistSongList[i].danceability = tempPlaylistFeature[i]["danceability"]
            playlistSongList[i].energy = tempPlaylistFeature[i]["energy"]
            playlistSongList[i].key = tempPlaylistFeature[i]["key"]
            playlistSongList[i].loudness = tempPlaylistFeature[i]["loudness"]
            playlistSongList[i].mode = tempPlaylistFeature[i]["mode"]
            playlistSongList[i].speechiness = tempPlaylistFeature[i]["speechiness"]
            playlistSongList[i].acousticness = tempPlaylistFeature[i]["acousticness"]
            playlistSongList[i].instrumentalness = tempPlaylistFeature[i]["instrumentalness"]
            playlistSongList[i].liveness = tempPlaylistFeature[i]["liveness"]
            playlistSongList[i].valence = tempPlaylistFeature[i]["valence"]        
            playlistSongList[i].tempo = tempPlaylistFeature[i]["tempo"]
           
        #break aliasing, load into the object to be returned
        temp = copy.copy(playlistSongList)
        playListSongObjs[key] = temp
    
    #return the obj that contains all the data for those playlists
    return playListSongObjs

# helper function that returns a dict with my user's average scores for every audio feature
def findAverageUserScore(userSong):
    
    #that dict
    userPlaylistAudioFeatures = {
                        "danceability": 0,
                        "energy":0,
                        "key": 0,
                        "loudness": 0,
                        "mode": 0,
                        "speechiness": 0,
                        "acousticness": 0,
                        "instrumentalness": 0,
                        "liveness": 0,
                        "valence": 0,
                        "tempo": 0,        
                    }

    #for every song in the user's playlist, add the stats for the audio features up
    for song in userSong:
        userPlaylistAudioFeatures["danceability"] += song.danceability
        userPlaylistAudioFeatures["energy"] += song.energy
        userPlaylistAudioFeatures["key"] += song.key
        userPlaylistAudioFeatures["loudness"] += song.loudness
        userPlaylistAudioFeatures["mode"] += song.mode
        userPlaylistAudioFeatures["acousticness"] += song.acousticness
        userPlaylistAudioFeatures["instrumentalness"] += song.instrumentalness
        userPlaylistAudioFeatures["liveness"] += song.liveness
        userPlaylistAudioFeatures["valence"] += song.valence
        userPlaylistAudioFeatures["tempo"] += song.tempo

    #for every audio feature, average it 
    for feature in userPlaylistAudioFeatures:
        userPlaylistAudioFeatures[feature] /= len(userSong)

    #return the dict
    return userPlaylistAudioFeatures

#takes in the list of data for that specific feature from the playlist, and the mean score for that feature from the user, cal variance
def variance(playlistIndivData,mean):

    # square the deviations to form the mean in the lsit
    deviations = [(x - mean) ** 2 for x in playlistIndivData]
    # get the variance divided by the total number of songs there are 
    variance = sum(deviations)/len(playlistIndivData)

    return variance