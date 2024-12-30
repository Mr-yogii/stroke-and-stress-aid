from flask import Flask, render_template, jsonify, request
import os
import pygame
import json
import time

app = Flask(__name__)

# Set up Pygame mixer for music playback
pygame.mixer.init()

# Location for music files
MUSIC_DIR = '/home/yogii/music/'  # Update this to your actual music directory
current_music = None

# Music files for each mood 
CALM_MUSIC = 'calm.mp3'  # Replace with your actual calm music file
ANGRY_MUSIC = 'angry.mp3'  # Replace with your actual angry music file
SAD_MUSIC = 'sad.mp3'  # Replace with your actual sad music file
STROKE_INSTRUCTION = 'stroke_instruction.mp3'  # Replace with your stroke first-aid instruction file

# Variables for muscle signal data
muscle_signal = 0

# Endpoint to display the dashboard
@app.route('/')
def index():
    return render_template('index.html', muscle_signal=muscle_signal)

# Endpoint to handle pre-process (music selection)
@app.route('/pre_process')
def pre_process():
    return render_template('pre_process.html', muscle_signal=muscle_signal)

# Endpoint to handle post-process (alerts and voice instructions)
@app.route('/post_process')
def post_process():
    return render_template('post_process.html', muscle_signal=muscle_signal)

# Endpoint to receive sensor data from ESP32
@app.route('/upload_data', methods=['POST'])
def upload_data():
    global muscle_signal
    data = request.get_json()
    muscle_signal = data.get('muscleSignal')
    
    # Log the data
    print(f"Received muscle signal: {muscle_signal}")
    
    # Decide what music to play based on the muscle signal
    if muscle_signal < 350:
        play_music(CALM_MUSIC)  # Calm music
    elif 350 <= muscle_signal <= 400:
        play_music(ANGRY_MUSIC)  # Angry music
    else:
        play_music(SAD_MUSIC)  # Sad music
    
    return jsonify({"status": "success", "muscle_signal": muscle_signal})

# Endpoint to fetch the current muscle signal
@app.route('/muscle_signal', methods=['GET'])
def get_muscle_signal():
    global muscle_signal
    return jsonify({"muscle_signal": muscle_signal})

# Endpoint to fetch the current playing music
@app.route('/current_music', methods=['GET'])
def get_current_music():
    global current_music
    return jsonify({"current_music": current_music})

# Endpoint to handle play music requests from frontend
@app.route('/play_music', methods=['POST'])
def play_music_endpoint():
    music_file = request.form.get('music_file')
    if music_file:
        success = play_music(music_file)
        if success:
            return jsonify({"status": "playing", "music_file": music_file})
        else:
            return jsonify({"status": "error", "message": "Failed to play music"})
    return jsonify({"status": "error", "message": "No music file specified"})

# Function to play music based on the selected file
def play_music(music_file):
    global current_music
    music_path = os.path.join(MUSIC_DIR, music_file)  # Correctly join path
    # Check if the file exists
    if os.path.exists(music_path):
        # Stop any current music
        if current_music:
            pygame.mixer.music.stop()

        # Play new music
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play()
        current_music = music_file
        return True
    else:
        print(f"Music file {music_file} not found.")
        return False

# Endpoint to trigger stroke first-aid instructions
@app.route('/play_stroke_instruction', methods=['POST'])
def play_stroke_instruction():
    success = play_music(STROKE_INSTRUCTION)
    if success:
        return jsonify({"status": "playing", "instruction": STROKE_INSTRUCTION})
    else:
        return jsonify({"status": "error", "message": "Failed to play stroke instruction"})

# Run the Flask web server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
