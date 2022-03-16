import copy
import json
import math
import os
import random

import spotipy
import spotipy.util as util
from cmu_112_graphics import *
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from backend import *


#modes learnt from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
#spotipy API calls learnt from https://spotipy.readthedocs.io/en/2.18.0/#api-reference and https://developer.spotify.com/documentation/web-api/reference/

##########################################
# starting screen (startingScreenMode)
##########################################

def startingScreenMode_redrawAll(app, canvas):
    canvas.create_image(app.width//2, app.height//2, image=ImageTk.PhotoImage(app.background))
    canvas.create_text(app.width//2, app.height//2,
    text = "psst. hey. let me guess your mbti. click the screen.", font = 'Times 22 bold')
    canvas.create_text(app.width//2, app.height*3//4,
    text = "remember to add http://localhost:8888/callback as a redirect URI in your spotify for devs project.", font = 'Times 18 bold')

def startingScreenMode_mousePressed(app, event):
    #gets my inputs and switches it to the next screen)
    app.c_id = app.getUserInput("Enter your Client Key:")
    app.c_s = app.getUserInput("Enter your Secret Key:")
    app.mode = "generatingResultsMode"
    
##########################################
# generating results screen (generatingResultsMode)
##########################################

def generatingResultsMode_redrawAll(app,canvas):
    #background image
    canvas.create_image(app.width//2, app.height//2, image=ImageTk.PhotoImage(app.background))
    canvas.create_text(app.width//2, app.height//4,
        text = f"aight getting your results now homie. hit spacebar.", \
        font = 'Times 22 bold')
    canvas.create_text(app.width//2, app.height//2,
        text = f"remember to have an active spotify player open for the full experience.", \
        font = 'Times 16 bold')

def generatingResultsMode_keyPressed(app,event):
    if event.key == "Space":
        backEnd(app)
        app.mode = "loadingPageMode"
        
##########################################
# loading in character (loadingPageMode)
##########################################

def loadingPageMode_redrawAll(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = "#353148")

    canvas.create_polygon(1480,app.height//2,1480-50,app.height//2-50,1480-50,app.height//2+50, fill="#cecee2")
    
    #if app.moving = false then sprite will do its idle animation
    if not app.moving:
        sprite = app.sprites[app.spriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))

    #sprite's running animation
    else:
        sprite = app.movingSprites[app.spriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))

    canvas.create_text(app.width//2, app.height*3//4,
    text = f"here's your good boi. move him with your arrow keys, and go explore your music taste.", \
    font = 'Times 22 bold', fill = "#cecee2")

def loadingPageMode_timerFired(app):
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)

def loadingPageMode_keyPressed(app,event):
    if event.key == "Right":
        app.x += 10
        app.moving = True
        if app.x >= app.width - 30 and app.mode == "loadingPageMode":
            app.mode ="mainRoomMode"
            app.x=0
            app.y = app.height//2
    if event.key == "Left":
        app.x -= 10
        app.moving = True
        if app.x <= 30:
            app.x += 10
    if event.key == "Down":
        app.y += 10
        app.moving = True
        if app.y >= app.height - 40:
            app.y -=10
    if event.key == "Up":
        app.y -= 10
        app.moving = True
        if app.y <= 40:
            app.y+= 10
    if event.key == "6":
        app.x = app.width-20
    if event.key == "4":
        app.x = 20
    if event.key == "2":
        app.y = app.height-20
    if event.key == "8":
        app.y = 20

def loadingPageMode_keyReleased(app, event):
    if event.key == "Right":
        app.moving = False
    if event.key == "Left":
        app.moving = False
    if event.key == "Down":
        app.moving = False
    if event.key == "Up":
        app.moving = False


##########################################
# main room (mainRoomMode)
##########################################

def mainRoomMode_redrawAll(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = "#353148")
    canvas.create_rectangle(app.width//2-300,app.height*4//10 - 30, app.width//2+300, app.height*6//10+20, fill ="#7b7cb2" )

    canvas.create_text(app.width//2, app.height*4//10, text = f"welcome to the main room", \
    font = 'Times 26 bold', fill="#cecee2")

    canvas.create_text(app.width//2, app.height*6//10-20, text = f"feel free to explore the different special rooms!", \
    font = 'Times 16', fill="#cecee2")

    #top triangle
    canvas.create_polygon(app.width//2,20,app.width//2-50,20 +50,app.width//2+50,20+50, fill="#cecee2")
    canvas.create_text(app.width//2, 100, text = f"room of personality~", \
    font = 'Times 20 bold', fill="#cecee2")

    canvas.create_polygon(app.width//2,880,app.width//2-50,830,app.width//2+50,830, fill="#cecee2")
    canvas.create_text(app.width//2, 810, text = f"room of good songs~", \
    font = 'Times 20 bold', fill="#cecee2")

    canvas.create_polygon(1480,app.height//2,1480-50,app.height//2-50,1480-50,app.height//2+50, fill="#cecee2")
    canvas.create_text(1280,app.height//2, text = \
    f"""        room of good 
        recommendations~""", \
    font = 'Times 20 bold', fill="#cecee2")

    canvas.create_polygon(20,app.height//2,20+50,app.height//2-50,20+50,app.height//2+50, fill="#cecee2")
    canvas.create_text(180,app.height//2, text = \
    f"""        infinity room 
    of trash  ~""", \
    font = 'Times 20 bold', fill="#cecee2")

    if not app.moving:
        sprite = app.sprites[app.spriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))

    else:
        sprite = app.movingSprites[app.movingSpriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))

def loadAlbumCovers(app):
    albumCovers = []
    for song in app.reccos:
        temp = app.sp.track(song[1])
        albumCovers.append(temp['album']['images'][1]["url"])
    try:
        app.songReco1 = app.loadImage(albumCovers[0])
        app.songReco2 = app.loadImage(albumCovers[1])
        app.songReco3 = app.loadImage(albumCovers[2])
        app.songReco4 = app.loadImage(albumCovers[3])
    except:
        print("out of songs, restart ")

def mainRoomMode_keyPressed(app,event):
    
    if event.key == "Right":
        app.x += 10
        app.moving = True
        if app.x >= app.width - 30 and app.mode == "mainRoomMode":
            app.mode ="songReccoMode"
            app.x= 0
            loadAlbumCovers(app)

    if event.key == "Left":
        app.x -= 10
        app.moving = True
        if app.x <= 30 and app.mode == "mainRoomMode":
            app.mode ="badSongsMode"
            app.x= app.width//2
            app.y = app.height*3//4
    
    if event.key == "Down":
        app.y += 10
        app.moving = True
        if app.y >= app.height - 40 and app.mode == "mainRoomMode":
            app.mode = "musicRoomMode"
            app.y= 0
    
    if event.key == "Up":
        app.y -= 10
        app.moving = True
        if app.y <= 40 and app.mode == "mainRoomMode":
            app.mode = "showcaseMode"
            app.y = app.height

    if event.key == "6":
        app.x = app.width-20
    if event.key == "4":
        app.x = 20
    if event.key == "2":
        app.y = app.height-20
    if event.key == "8":
        app.y = 20
            
def mainRoomMode_keyReleased(app, event):
    if event.key == "Right":
        app.moving = False
    if event.key == "Left":
        app.moving = False
    if event.key == "Down":
        app.moving = False
    if event.key == "Up":
        app.moving = False

def mainRoomMode_timerFired(app):
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
    app.movingSpriteCounter = (1 + app.movingSpriteCounter) % len(app.movingSprites)


##########################################
# screen for generating song reccomendations(songReccoMode)
##########################################

def songReccoMode_redrawAll(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = "#353148")

    for i in range(len(app.reccos)):
        if len(app.reccos[i][0]) < 25:
            canvas.create_text(app.width* (i+1)//5, app.height//2, text = f"{app.reccos[i][0]}", font = "Times 16 bold", fill="#cecee2")
        else:
            canvas.create_text(app.width* (i+1)//5, app.height//2, text = f"{app.reccos[i][0][:16]} \n {app.reccos[i][0][16:]}", font = "Times 16 bold", fill="#cecee2")

    canvas.create_image(app.width//5, app.height*3//4, image=ImageTk.PhotoImage(app.songReco1))
    canvas.create_image(app.width*2//5, app.height*3//4, image=ImageTk.PhotoImage(app.songReco2))
    canvas.create_image(app.width*3//5, app.height*3//4, image=ImageTk.PhotoImage(app.songReco3))
    canvas.create_image(app.width*4//5, app.height*3//4, image=ImageTk.PhotoImage(app.songReco4))

    if not app.moving:
        sprite = app.sprites[app.spriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))

    else:
        sprite = app.movingSprites[app.spriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))

    canvas.create_text(app.width//2, app.height//4,
        text = f"these are your recommendations curated for you according to both your personality type + recently played songs",\
        font = 'Times 22 bold', fill="#cecee2")
    canvas.create_text(app.width//2, app.height//4-50,
    text = f"move good boi to the album art of the song you want to play, press space to start playing",\
    font = 'Times 16 ', fill="#cecee2")
    canvas.create_text(app.width//2, app.height//4-100,
    text = f"press z to get new suggestions, x to dislike a song, and c to like a song. disliked songs won't appear here again. ",\
    font = 'Times 16 ', fill="#cecee2")
    canvas.create_text(app.width//2, app.height//4 + 50,
    text = f"press L to turn your liked songs into a playlist! ",\
    font = 'Times 16 ', fill="#cecee2")
    
def songReccoMode_keyPressed(app,event):
    if event.key == "Right":
        app.x += 10
        app.moving = True
        if app.x >= app.width - 30:
            app.x -= 10

    if event.key == "Left":
        app.x -= 10
        app.moving = True
        if app.x <= 30 and app.mode == "songReccoMode":
            app.mode ="mainRoomMode"
            app.x= app.width
            app.y = app.height//2

    if event.key == "Down":
        app.y += 10
        app.moving = True
        if app.y >= app.height - 40:
            app.y -= 10
            

    if event.key == "Up":
        app.y -= 10
        app.moving = True
        if app.y <= 40:
            app.y+= 10

    if event.key == "Space":
        if app.y > app.height*3//4 - 150 and app.y < app.height*3//4 +150 and app.mode == "songReccoMode":
            if app.x > app.width//5-150 and app.x < app.width//5+150:
                try:
                    app.sp.start_playback(uris=[f"{app.reccos[0][1]}"])
                except:
                    print("open an active spotify player!")
            elif app.x > app.width*2//5-150 and app.x < app.width*2//5+150:
                try:
                    app.sp.start_playback(uris=[f"{app.reccos[1][1]}"])
                except:
                    print("open an active spotify player!")
            elif app.x > app.width*3//5-150 and app.x < app.width*3//5+150:
                try: 
                    app.sp.start_playback(uris=[f"{app.reccos[2][1]}"])
                except:
                    print("open an active spotify player!")
            elif app.x > app.width*4//5-150 and app.x < app.width*4//5+150:
                try:
                    app.sp.start_playback(uris=[f"{app.reccos[3][1]}"])
                except:
                    print("open an active spotify player!")

    if event.key == "z" and app.mode == "songReccoMode":
        app.counter += 4
        try:
            loadSongs(app)
        except:
            songRec(app)
        loadAlbumCovers(app)

    if event.key == "x":
        f= open("dislikes.txt","a+")
        if app.y > app.height*3//4 - 150 and app.y < app.height*3//4 +150 and app.mode == "songReccoMode":
            if app.x > app.width//5-150 and app.x < app.width//5+150:
                f.write(f"{app.reccos[0][1]}\n")
            elif app.x > app.width*2//5-150 and app.x < app.width*2//5+150:
                f.write(f"{app.reccos[1][1]}\n")
            elif app.x > app.width*3//5-150 and app.x < app.width*3//5+150:
                f.write(f"{app.reccos[2][1]}\n")
            elif app.x > app.width*4//5-150 and app.x < app.width*4//5+150:
                f.write(f"{app.reccos[3][1]}\n")
        f.close()

    if event.key == "c":
        f= open("likes.txt","a+")
        if app.y > app.height*3//4 - 150 and app.y < app.height*3//4 +150 and app.mode == "songReccoMode":
            if app.x > app.width//5-150 and app.x < app.width//5+150:
                f.write(f"{app.reccos[0][1]}\n")
            elif app.x > app.width*2//5-150 and app.x < app.width*2//5+150:
                f.write(f"{app.reccos[1][1]}\n")
            elif app.x > app.width*3//5-150 and app.x < app.width*3//5+150:
                f.write(f"{app.reccos[2][1]}\n")
            elif app.x > app.width*4//5-150 and app.x < app.width*4//5+150:
                f.write(f"{app.reccos[3][1]}\n")
        f.close()

    #creates playlist
    if event.key == "l":
        playlistName = app.getUserInput("what do you want your playlist to be called?")
        playlistDescription = app.getUserInput("give it a description!")
        playlist = app.sp.user_playlist_create(app.userID, playlistName, description = playlistDescription)
        app.sp.playlist_add_items(playlist["id"],app.likes)
    
    if event.key == "6":
        app.x = app.width-20
    if event.key == "4":
        app.x = 20
    if event.key == "2":
        app.y = app.height-20
    if event.key == "8":
        app.y = 20

def songReccoMode_keyReleased(app, event):

    if event.key == "Right":
        app.moving = False
    if event.key == "Left":
        app.moving = False
    if event.key == "Down":
        app.moving = False
    if event.key == "Up":
        app.moving = False
    if event.key == "6":
        app.x = app.width-20
    if event.key == "4":
        app.x = 20
    if event.key == "2":
        app.y = app.height-20
    if event.key == "8":
        app.y = 20

def songReccoMode_timerFired(app):

    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
    app.movingSpriteCounter = (1 + app.movingSpriteCounter) % len(app.movingSprites)


##########################################
# my liked music room (musicRoomMode)
##########################################

def musicRoomMode_redrawAll(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = "#353148")
    width = 150
    height = 150
    if len(app.likedSongsPics) >= app.end:
        for i in range(app.start,app.end):
            canvas.create_image(width, height, image = ImageTk.PhotoImage(app.likedSongsPics[i]))
            if width != 1350:
                width += 300
            else:
                height += 300
                width = 150

    else:
        for i in range(app.start,len(app.likedSongsPics)):
            canvas.create_image(width, height, image = ImageTk.PhotoImage(app.likedSongsPics[i]))
            if width != 1350:
                width += 300
            else:
                height += 300
                width = 150
    if not app.moving:
        sprite = app.sprites[app.spriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))

    else:
        sprite = app.movingSprites[app.spriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))
 
def musicRoomMode_keyPressed(app,event):
    if event.key == "Right":
        app.x += 10
        app.moving = True
        if app.x >= app.width - 30:
            app.x -= 10
    if event.key == "Left":
        app.x -= 10
        app.moving = True
        if app.x <= 30:
            app.x += 10
    if event.key == "Down":
        if app.popUpCounter == 0:
            #from 112 lecture page
            messagebox.showinfo("toggling screens", "move over the song image and press space to play. else, press a or d to toggle screens if you've liked that many songs!", icon = "info")
            app.popUpCounter += 1
        app.y += 10
        app.moving = True
        if app.y >= app.height - 40:
            app.y -=10
    if event.key == "Up":
        app.y -= 10
        app.moving = True
        if app.y <= 40 and app.mode == "musicRoomMode":
            app.mode = "mainRoomMode"
            app.y = app.height
    if event.key == "m":
        storeLikedSongs(app)
    if event.key == "a":
        if app.start != 0:
            app.start -= 16
            app.end -= 16
            app.songIndex -= 1
    if event.key == "d":
        if app.end < len(app.likedSongsPics):
            app.start +=16
            app.end+=16
            app.songIndex += 1
    
    if event.key == "Space":
        col = app.x//300
        row = app.y//300
        app.final = col + row*5 + app.songIndex*16
        try:
            app.sp.start_playback(uris=[f"{app.likes[app.final][:36]}"])
        except:
            print("Have an active Spotify player")


    if event.key == "6":
        app.x = app.width-20
    if event.key == "4":
        app.x = 20
    if event.key == "2":
        app.y = app.height-20
    if event.key == "8":
        app.y = 20

def musicRoomMode_keyReleased(app, event):
    if event.key == "Right":
        app.moving = False
    if event.key == "Left":
        app.moving = False
    if event.key == "Down":
        app.moving = False
    if event.key == "Up":
        app.moving = False

def musicRoomMode_timerFired(app):
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
    app.movingSpriteCounter = (1 + app.movingSpriteCounter) % len(app.movingSprites)

##########################################
# screen for showing results (showcaseMode)
##########################################

def showcaseMode_redrawAll(app, canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = "#353148")

    if not app.moving:
        sprite = app.sprites[app.spriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))

    else:
        sprite = app.movingSprites[app.movingSpriteCounter]
        canvas.create_image(app.x, app.y, image=ImageTk.PhotoImage(sprite))

    canvas.create_text(app.width//2, app.height//4,
        text = f"so you're a {app.winner} huh {app.userName}. seems about right.", \
        font = 'Times 22 bold', fill="#cecee2")

    canvas.create_text(app.width//2, app.height//2,
        text = f"{app.winner}s are called {app.personalityDict[app.winner][0]}s", \
        font = 'Times 20 bold', fill="#cecee2")

    canvas.create_text(app.width//2, app.height//2+70,
        text = f"{app.personalityDict[app.winner][1]}", \
        font = 'Times 18', fill="#cecee2")
    

    canvas.create_text(app.width//2, app.height*3//4,
        text = f"i'm sorry? you think our super complicated and extremely scientifically accurate algorithm is wrong???", \
        font = 'Times 14', fill="#cecee2")

    canvas.create_text(app.width//2, app.height*3//4+65,
        text = f"fine... press space and i'll sort you to your next closest personality.", \
        font = 'Times 14', fill="#cecee2")  

def showcaseMode_keyPressed(app,event):
    if event.key == "Right":
        app.x += 10
        app.moving = True
        if app.x >= app.width - 30:
            app.x-=10
    if event.key == "Left":
        app.x -= 10
        app.moving = True
        if app.x <= 30:
            app.x += 10
    if event.key == "Down":
        app.y += 10
        app.moving = True
        if app.y >= app.height - 40:
            app.y = 0
            app.mode = "mainRoomMode"
    if event.key == "Up":
        app.y -= 10
        app.moving = True
        if app.y <= 40:
            app.y+= 10

    if event.key == "s":
        app.saveSnapshot()

    if event.key == "Space":
        reset(app)

    if event.key == "6":
        app.x = app.width-20
    if event.key == "4":
        app.x = 20
    if event.key == "2":
        app.y = app.height-20
    if event.key == "8":
        app.y = 20

def showcaseMode_keyReleased(app, event):
    if event.key == "Right":
        app.moving = False
    if event.key == "Left":
        app.moving = False
    if event.key == "Down":
        app.moving = False
    if event.key == "Up":
        app.moving = False

def showcaseMode_timerFired(app):
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
    app.movingSpriteCounter = (1 + app.movingSpriteCounter) % len(app.movingSprites)

def reset(app):
            if app.mode == "showcaseMode":
                app.index-=1
                app.mode = "generatingResultsMode"
                app.x = app.width//2
                app.y = app.height//2


##########################################
# my disliked songs room (badSongsMode)
##########################################

def badSongsMode_redrawAll(app,canvas):
    #sidescroller learnt from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
    canvas.create_rectangle(0,0,app.width,app.height, fill = "#353148")
    width = 150 - app.scrollX
    height = 450

    canvas.create_polygon(app.width//2,20,app.width//2-50,20 +50,app.width//2+50,20+50, fill="#cecee2")
    canvas.create_text(app.width//2, 100, text = f"exit here", 
    font = 'Times 20 bold', fill="#cecee2")

    #creates text boxes
    for i in range(len(app.dislikedSongsPics)):
        canvas.create_image(width, height, image = ImageTk.PhotoImage(app.dislikedSongsPics[i]))
        if len(app.dislikedSongNames[i]) < 25:
            canvas.create_text(width, height-200, text = f"{app.dislikedSongNames[i]}", font = 'Times 14 bold', fill="#cecee2")
        else:
            canvas.create_text(width, height-200, text = f"{app.dislikedSongNames[i][:24]} \n {app.dislikedSongNames[i][24:]}", font = 'Times 14 bold', fill="#cecee2")
        width += 300
       
    if not app.moving:
        sprite = app.sprites[app.spriteCounter]
        canvas.create_image(app.x-app.scrollX, app.y, image=ImageTk.PhotoImage(sprite))

    else:
        sprite = app.movingSprites[app.spriteCounter]
        canvas.create_image(app.x-app.scrollX, app.y, image=ImageTk.PhotoImage(sprite))
 
def badSongsMode_keyPressed(app,event):
    if event.key == "Right":
        movePlayer(app, +10, 0)
        app.moving = True
    if event.key == "Left":
        movePlayer(app, -10, 0)
        app.moving = True
    if event.key == "Down":
        app.y += 10
        app.moving = True
        if app.y >= app.height - 40:
            app.y -=10
    if event.key == "Up":
        if app.popUpCounter2 == 0:
            #shows pop up for instructions
            messagebox.showinfo("hall of trash", "your personal song hell. room is infinite, move over the song image and press space to play, press m to reload.", icon = "info")
            app.popUpCounter2 += 1
        app.y -= 10
        app.moving = True
        if app.y <= 40 and app.mode == "badSongsMode":
            app.mode = "mainRoomMode"
            app.y = app.height//2
            app.x = 0
    #restarts page
    if event.key == "m":
        storeDislikedSongs(app)
    if event.key == "Space":
        col = app.x//300
        try:
            #starts playback
            app.sp.start_playback(uris=[f"{app.dislikes[col][:36]}"])
        except:
            print("Have an active Spotify player")
    if event.key == "2":
        app.y = app.height-20
    if event.key == "8":
        app.y = 20
    if event.key == "4":
        app.x = 20

#learnt from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
def movePlayer(app, dx, dy):
    app.x += dx
    makePlayerVisible(app)

#learnt from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
def makePlayerVisible(app):
    if (app.x < app.scrollX + app.scrollMargin):
        app.scrollX = app.x - app.scrollMargin
    if (app.x > app.scrollX + app.width - app.scrollMargin):
        app.scrollX = app.x - app.width + app.scrollMargin

def badSongsMode_keyReleased(app, event):
    if event.key == "Right":
        app.moving = False
    if event.key == "Left":
        app.moving = False
    if event.key == "Down":
        app.moving = False
    if event.key == "Up":
        app.moving = False

def badSongsMode_timerFired(app):
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
    app.movingSpriteCounter = (1 + app.movingSpriteCounter) % len(app.movingSprites)

##########################################
# Main App (initialises stuff i need for the game)
##########################################

def appStarted(app):
    
    #starts my initial screen
    app.mode = "startingScreenMode"
    #selects the personality that's displayed at the end - this is the lowest variance one
    app.index = 15
    app.counter = 0
    app.start = 0
    app.songIndex = 0
    app.popUpCounter = 0
    app.popUpCounter2 = 0
    app.end = 16
    app.scrollX = 0
    app.scrollMargin = 100
    #helps control my sprite
    app.loading = False
    app.moving = False
    #loads my spritesheets, every sprite after comes from credits to this webpage https://penusbmic.itch.io/characterpack1
    spritestrip = app.loadImage("Idle.png")
    spritestripMove = app.loadImage("Run.png")
    #loads and scales my background, every time i used a background has credits to this webpage https://s4m-ur4i.itch.io/pixelart-clouds-background
    background = app.loadImage("background.png")
    app.background = app.scaleImage(background, 4)

    #idle sprite list and cropping + scaling
    app.sprites = [ ]
    app.spriteCounter = 0
    sprite1 = spritestrip.crop((5, 15, 29, 35))
    sprite2 = spritestrip.crop((5, 60, 29, 80))
    sprite3 = spritestrip.crop((5, 104, 29, 124))
    sprite4 = spritestrip.crop((5, 148, 29, 168))
    app.sprites.append(app.scaleImage(sprite1,5))
    app.sprites.append(app.scaleImage(sprite2,5))
    app.sprites.append(app.scaleImage(sprite3,5))
    app.sprites.append(app.scaleImage(sprite4,5))
    
    #setting the sprite to appear in the middle of the map first
    app.x = app.width//2
    app.y = app.height//2

    #moving sprite list and cropping + scaling
    app.movingSprites = [ ]
    app.movingSpriteCounter = 0
    for i in range(6):
        #values are according to the places the sprites were on the sprite sheet
        sprite = spritestripMove.crop((9, 15+i*45, 24, 15+i*45 + 20))
        sprite = app.scaleImage(sprite,5)
        app.movingSprites.append(sprite)

    
    if not os.path.isfile('dislikes.txt'):
        f=open("dislikes.txt","w+")
        f.close()
    if not os.path.isfile('likes.txt'):
        f=open("likes.txt", "w+")
        f.close()

    #personality description and details come from https://www.16personalities.com/personality-types
    app.personalityDict = {
        "ESFP": ("The Entertainer", "Spontaneous, energetic and enthusiastic people – life is never boring around them."),
        "ISFP": ("The Adventurer", "Flexible and charming artists, always ready to explore and experience something new."),
        "ESTP": ("The Entrepreneur","Smart, energetic and very perceptive people, who truly enjoy living on the edge." ),
        "ISTP": ("The Virtuoso", "Bold and practical experimenters, masters of all kinds of tools."),
        "ENFP": ("The Campaigner","Enthusiastic, creative and sociable free spirits, who can always find a reason to smile." ),
        "INFP": ("The Mediator", "Poetic, kind and altruistic people, always eager to help a good cause." ),
        "ENFJ": ("The Protagonist","Charismatic and inspiring leaders, able to mesmerize their listeners." ),
        "INFJ": ("The Advocate", "Quiet and mystical, yet very inspiring and tireless idealists."),
        "ENTP": ("The Debater", "Smart and curious thinkers who cannot resist an intellectual challenge."),
        "INTP": ("The Logician", "Innovative inventors with an unquenchable thirst for knowledge." ),
        "ENTJ": ("The Commander", "Bold, imaginative and strong-willed leaders, always finding a way – or making one."),
        "INTJ": ("The Architect", "Imaginative and strategic thinkers, with a plan for everything."),
        "ESTJ": ("The Executive","Excellent administrators, unsurpassed at managing things – or people." ),
        "ISTJ": ("The Logistician", "Practical and fact-minded individuals, whose reliability cannot be doubted." ),
        "ESFJ": ("The Consul", "Extraordinarily caring, social and popular people, always eager to help."),
        "ISFJ": ("The Defender","Very dedicated and warm protectors, always ready to defend their loved ones." )
        }   


runApp(width=1500, height=900)
