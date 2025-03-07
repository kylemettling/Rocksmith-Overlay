from dotenv import load_dotenv
import os
import json
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def generate_tips(song, artist, num_tips=3):
    prompt_theory = f"Provide {num_tips} concise, single-sentence music theory tips for '{song}' by '{artist}' in Rocksmith 2014."
    prompt_trivia = f"Provide {num_tips} concise, single-sentence fun trivia facts for '{song}' by '{artist}' in Rocksmith 2014."
    
    response_theory = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_theory}],
        max_tokens=150
    )
    response_trivia = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_trivia}],
        max_tokens=150
    )
    
    theory_tips = [line.strip() for line in response_theory.choices[0].message.content.split("\n") if line.strip()][:num_tips]
    trivia_tips = [line.strip() for line in response_trivia.choices[0].message.content.split("\n") if line.strip()][:num_tips]
    
    return {"theory": theory_tips, "trivia": trivia_tips}

def save_tips():
    songs = [
        ("Sweet Home Alabama", "Lynyrd Skynyrd"),
        ("Smells Like Teen Spirit", "Nirvana"),
        # Add your Rocksmith songs here
    ]
    tips = {}
    for song, artist in songs:
        tips[song] = {"artist": artist, **generate_tips(song, artist)}
    
    with open("song_tips.json", "w") as f:
        json.dump(tips, f, indent=4)

if __name__ == "__main__":
    save_tips()