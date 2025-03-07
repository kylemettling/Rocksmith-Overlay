import sys
import socket
import time
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
import json
import logging
from PyQt5.QtCore import pyqtSignal, QObject
import openai

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, resources={r"/*": {"origins": "*"}})

# Global state for Live AI and last known good data
LIVE_AI_ENABLED = False
last_known_data = {
    "song": "N/A",
    "artist": "N/A",
    "album": "N/A",
    "hitrate": 0.0,
    "streak": 0,
    "highest_streak": 0,
    "hitrate_history": [],
    "theory": "N/A",
    "trivia": "N/A",
    "live_ai": False
}
hitrate_history = []  # Track the last 10 hitrate values

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return False
        except socket.error:
            return True

class Closer(QObject):
    close_signal = pyqtSignal()

@app.route("/data")
def get_data():
    global last_known_data, hitrate_history

    # Retry fetching data from RockSniffer up to 5 times with increasing delay
    full_response = None
    memory_readout = None
    song_details = {}
    for attempt in range(5):
        try:
            response = requests.get("http://127.0.0.1:9938", timeout=1)
            response.raise_for_status()
            full_response = response.json()
            logging.debug(f"Attempt {attempt + 1} - Full RockSniffer response: {full_response}")
            memory_readout = full_response.get("memoryReadout", {})
            # Check for case variations of songDetails
            song_details = next((v for k, v in full_response.items() if k.lower() == "songdetails"), memory_readout.get("songDetails", {}))
            logging.debug(f"Attempt {attempt + 1} - memory_readout: {memory_readout}")
            logging.debug(f"Attempt {attempt + 1} - song_details: {song_details}")
            # Break if we have songDetails with a songName or songID
            if song_details and (song_details.get("songName") or song_details.get("songID")):
                break
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} - Failed to fetch data: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s, 8s, 16s
    else:
        logging.error("Failed to fetch data after 5 retries, using last known data")
        return jsonify(last_known_data)

    song = song_details.get("songName", memory_readout.get("songID", "N/A"))
    artist = song_details.get("artistName", "N/A")
    album = song_details.get("albumName", "N/A")

    note_data = memory_readout.get("noteData", {})
    hitrate = note_data.get("Accuracy", 0.0)
    streak = note_data.get("CurrentHitStreak", 0)
    highest_streak = note_data.get("HighestHitStreak", 0)
    
    # Update hitrate_history
    hitrate_history.append(float(hitrate))
    if len(hitrate_history) > 10:  # Keep only the last 10 values
        hitrate_history.pop(0)
    logging.debug(f"Updated hitrate_history: {hitrate_history}")

    song_tips = {}
    try:
        with open("song_tips.json", "r") as f:
            song_tips = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    theory = song_tips.get(song, {}).get("theory", "N/A")
    trivia = song_tips.get(song, {}).get("trivia", "N/A")

    data = {
        "song": song,
        "artist": artist,
        "album": album,
        "theory": theory,
        "trivia": trivia,
        "hitrate": float(hitrate),
        "hitrate_history": hitrate_history,  # Use the updated history
        "streak": int(streak),
        "highest_streak": int(highest_streak),  # Use the current highest streak
        "live_ai": LIVE_AI_ENABLED
    }
    logging.debug(f"Returning data: {data}")

    # Update last known data if we have valid songDetails
    if song_details and (song_details.get("songName") or song_details.get("songID")):
        last_known_data = data

    return jsonify(data)

def fetch_tips(song, artist):
    try:
        theory_prompt = f"Provide a short guitar playing tip for the song '{song}' by {artist}."
        trivia_prompt = f"Provide a short piece of trivia about the song '{song}' by {artist}."
        theory_response = openai.chat.completions.create(
            messages=[{"role": "user", "content": theory_prompt}],
            model="gpt-3.5-turbo",
        )
        trivia_response = openai.chat.completions.create(
            messages=[{"role": "user", "content": trivia_prompt}],
            model="gpt-3.5-turbo",
        )
        theory = theory_response.choices[0].message.content.strip()
        trivia = trivia_response.choices[0].message.content.strip()
        return theory, trivia
    except Exception as e:
        logging.error(f"OpenAI error: {str(e)}")
        return "N/A", "N/A"

def update_tips(song, theory, trivia):
    try:
        with open("song_tips.json", "r") as f:
            song_tips = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        song_tips = {}
    song_tips[song] = {"theory": theory, "trivia": trivia}
    with open("song_tips.json", "w") as f:
        json.dump(song_tips, f, indent=2)
    logging.info(f"Updated song_tips.json with {song}: {song_tips[song]}")

@app.route("/toggle_live_ai", methods=["POST"])
def toggle_live_ai():
    global LIVE_AI_ENABLED
    data = request.get_json()
    song = data.get("song", "N/A")
    artist = data.get("artist", "N/A")
    LIVE_AI_ENABLED = not LIVE_AI_ENABLED
    if LIVE_AI_ENABLED:
        theory, trivia = fetch_tips(song, artist)
        update_tips(song, theory, trivia)
    return jsonify({"live_ai": LIVE_AI_ENABLED})

@app.route("/close", methods=["POST"])
def close():
    logging.info("Close endpoint called")
    app.closer.close_signal.emit()
    import os
    os._exit(0)  # Temporary workaround to force exit
    return jsonify({"status": "closed"})

@app.route("/overlay")
def overlay():
    return render_template("overlay.html")

def run_flask(port):
    if is_port_in_use(port):
        logging.error(f"Port {port} is already in use. Please free the port or change it.")
        return
    logging.info(f"Starting Flask server on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)

if __name__ == "__main__":
    port = 5000
    if is_port_in_use(port):
        logging.error(f"Port {port} is already in use. Please free the port or change it.")
        sys.exit(1)
    run_flask(port)