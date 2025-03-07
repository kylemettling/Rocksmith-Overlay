import requests
import json
import time

def get_rocksniffer_data():
    url = "http://127.0.0.1:9938"
    retries = 5  # Increased retries
    initial_wait = 5  # Wait 5 seconds initially to let RockSniffer start
    time.sleep(initial_wait)
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=2)  # Increased timeout to 2s
            response.raise_for_status()
            data = response.json()
            print(f"Debug: Successfully fetched RockSniffer data on attempt {attempt + 1}, success={data.get('success', False)}")
            return data
        except requests.exceptions.RequestException as e:
            print(f"RockSniffer fetch failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2)  # Backoff with 2s between retries
            continue
    print(f"Warning: Failed to connect to RockSniffer after {retries} attempts")
    return None

def update_data():
    last_data = None
    while True:
        data = get_rocksniffer_data()
        if data:
            memory_readout = data.get("memoryReadout", {})
            song_details = data.get("songDetails", {})
            if not song_details:  # Fallback to memoryReadout if songDetails is null
                song_details = memory_readout.get("songDetails", {})
            note_data = memory_readout.get("noteData", {})
            game_state = memory_readout.get("gameStage", "menu")
            # Use songID from memoryReadout as primary if songDetails is incomplete
            song = song_details.get("songName", memory_readout.get("songID", "N/A").replace("CST1_", ""))
            # Force update if data structure changes significantly
            should_update = last_data is None or last_data.get("memoryReadout", {}).get("songTimer", -1) != memory_readout.get("songTimer", -1)
            if should_update:
                print(f"Debug: Updating data - Song={song}, gameStage={game_state}, is_playing={game_state == 'las_game'}")
                output = {
                    "song": song,
                    "artist": song_details.get("artistName", "N/A"),
                    "album": song_details.get("albumName", "N/A"),
                    "hitrate": note_data.get("Accuracy", "N/A"),
                    "streak": note_data.get("CurrentHitStreak", "N/A"),
                    "highest_streak": note_data.get("HighestHitStreak", "N/A"),
                    "is_playing": game_state == "las_game",
                    "status": "connected"
                }
                last_data = data.copy()  # Store last successful data
            else:
                output = last_data  # Reuse last data if no significant change
        else:
            output = {
                "song": "N/A",
                "is_playing": False,
                "status": "waiting"
            }
            last_data = None
        with open("data.json", "w") as f:
            json.dump(output, f)
        time.sleep(1)

if __name__ == "__main__":
    print("Starting RockSniffer reader...")
    update_data()