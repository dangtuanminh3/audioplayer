import os
import time
from tkinter import *
from tkinter import filedialog as fd
import customtkinter as ctk
from mutagen.mp3 import MP3
from pygame import mixer

# Initialize the mixer
mixer.init()

# Global variables
queue = []
song_length = 0
current_song_mut = None
slider_dragging = False
seek_offset = 0  # Store the position after seeking

def add_songs():
    songs = fd.askopenfilenames(title="Add songs to queue", filetypes=(("mp3 Files", "*.mp3"),))
    for song in songs:
        if song.endswith(".mp3") and song not in queue:
            queue.append(song)
            playlist.insert(END, os.path.basename(song))
    print(queue)

def play_song():
    music_name = playlist.get(ACTIVE)
    for song in queue:
        if music_name in song:
            playlist.activate(playlist.curselection())
            playlist.selection_set(playlist.curselection(), last=None)
            global current_song_mut, seek_offset
            current_song_mut = MP3(song)
            mixer.music.load(song)
            mixer.music.play()
            seek_offset = 0
            music_title.configure(text=music_name)
            global song_length
            song_length = current_song_mut.info.length
            slider.configure(to=song_length)
            play_time()
            play_button.configure(image=pause_button_img, command=pause_song)
            break

def pause_song():
    if mixer.music.get_busy():
        mixer.music.pause()
        play_button.configure(image=play_button_img, command=resume_song)

def resume_song():
    if mixer.music.get_busy() and mixer.music.get_pos() != 0:
        mixer.music.unpause()
        play_button.configure(image=pause_button_img, command=pause_song)

def stop_song():
    mixer.music.stop()
    play_button.configure(image=play_button_img, command=play_song)
    slider.set(0)

def next_song():
    current_index = playlist.curselection()[0]
    next_index = current_index + 1
    if next_index < playlist.size():
        play_specific_song(next_index)

def previous_song():
    current_index = playlist.curselection()[0]
    previous_index = current_index - 1
    if previous_index >= 0:
        play_specific_song(previous_index)

def play_specific_song(index):
    playlist.selection_clear(0, END)
    playlist.activate(index)
    playlist.selection_set(index, last=None)
    play_song()

def delete_song():
    playlist.delete(ACTIVE)
    music_name = playlist.get(ACTIVE)
    if music_name in queue:
        queue.remove(music_name)
    mixer.music.unload()
    play_button.configure(image=play_button_img, command=play_song)

def play_time():
    if not mixer.music.get_busy():
        return

    try:
        current_time = mixer.music.get_pos() / 1000 + seek_offset  # Add seek offset to the current time

        if not slider_dragging:  # Only update the slider if the user isn't dragging it
            slider.set(current_time)

        converted_current_time = time.strftime('%H:%M:%S', time.gmtime(current_time))
        converted_song_length = time.strftime('%H:%M:%S', time.gmtime(song_length))
        length_text.configure(text=f'{converted_current_time} of {converted_song_length}')
        
        if current_time < song_length:
            length_text.after(500, play_time)
        else:
            stop_song()

    except Exception as e:
        print(f"Error in play_time: {e}")

def seek(event):
    global seek_offset
    position = slider.get()  # Get the position from the slider
    mixer.music.stop()  # Stop the music
    mixer.music.play(start=position)  # Restart the music from the new position
    seek_offset = position  # Update the seek offset with the new position
    slider.set(position)  # Manually set the slider value to the new position

def slider_pressed(event):
    global slider_dragging
    slider_dragging = True

def slider_released(event):
    global slider_dragging
    slider_dragging = False
    seek(event)

# Configure the window
root = ctk.CTk()
root.title("Music Player")
root.configure(background="white")
root.geometry("700x415")

# Frames
frm_music = Frame(root, relief=RIDGE)
frm_music.pack(fill='x')

frm_buttons = Frame(root, relief=RIDGE, bg="#151515", bd=3)
frm_buttons.pack(fill='x', side=BOTTOM)

# Playlist and Scrollbar
scroll = Scrollbar(frm_music)
playlist = Listbox(frm_music, width=500, height=15, font=('Arial', 14), bg='#202020', fg='white', selectbackground="lightblue", cursor="hand2", bd=0, yscrollcommand=scroll.set, selectmode=SINGLE)
scroll.config(command=playlist.yview)
scroll.pack(side=RIGHT, fill=Y)
playlist.pack(side=LEFT, fill=X)

# Text
music_title = Label(root, text="...", bg="#242424", fg="white")
music_title.pack(fill=X, side=BOTTOM)

length_text = Label(root, text="...", bg="#242424", fg="white")
length_text.pack(fill=X, side=BOTTOM)

# Slider for Progress
slider = ctk.CTkSlider(master=root, from_=0, to=100, orientation='horizontal', width=700)
slider.pack(fill=X, side=BOTTOM, pady=2)
slider.bind("<Button-1>", slider_pressed)
slider.bind("<ButtonRelease-1>", slider_released)

# Menu
player_menu = Menu(root)
root.config(menu=player_menu)

add_song_menu = Menu(player_menu)
player_menu.add_cascade(label="Files", menu=add_song_menu)
add_song_menu.add_command(label="Add Songs", command=add_songs)
add_song_menu.add_command(label="Delete Song", command=delete_song)

# Buttons
back_button_img = PhotoImage(file='images/previous.png')
play_button_img = PhotoImage(file='images/play.png')
pause_button_img = PhotoImage(file='images/pause.png')
stop_button_img = PhotoImage(file='images/stop.png') 
next_button_img = PhotoImage(file='images/next.png')

play_button = ctk.CTkButton(frm_buttons, text="", command=play_song, image=play_button_img, width=50, fg_color="white")
stop_button = ctk.CTkButton(frm_buttons, text="", command=stop_song, image=stop_button_img, width=50, fg_color="white")
next_button = ctk.CTkButton(frm_buttons, text="", command=next_song, image=next_button_img, width=50, fg_color="white")
previous_button = ctk.CTkButton(frm_buttons, text="", command=previous_song, image=back_button_img, width=50, fg_color="white")

# Pack buttons
previous_button.pack(side=LEFT, padx=(242, 2))
play_button.pack(side=LEFT, padx=2)
stop_button.pack(side=LEFT, padx=2)
next_button.pack(side=LEFT, padx=2)

root.mainloop()