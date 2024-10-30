from app.models import Track, Artist
from utils import remove_non_alphabetic

def process_file(path: str):
    lines = []
    with open(path, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    tracks = []
    artist_dict = {}  # Dictionary to store unique artists and their tags
    tag_dict = {}     # Dictionary to store tags and associated tracks (as sets to avoid duplicates)

    for line in lines:
        line = line.strip()  # Remove any leading/trailing whitespace
        if not line:  # Skip empty lines
            continue

        parts = line.split(' - ')
        if len(parts) < 2:  # Skip lines without both artist and track
            print(f"Skipping malformed line: {line}")
            continue

        artist_name, track_name = parts[0], parts[1]
        tags = parts[2].split(', ') if len(parts) > 2 else []  # Use an empty list if no tags

        # Create Track and add tags
        track = Track(track_name, artist_name)
        for tag in tags:
            track.add_tag(tag.lower())
        tracks.append(track)

        # Add tags to the artist's entry in the dictionary
        if artist_name not in artist_dict:
            artist_dict[artist_name] = set()
        
        artist_dict[artist_name].update(tags)

        # Add track to each tag's entry in the tag dictionary as a set to avoid duplicates
        for tag in tags:
            tag = remove_non_alphabetic(tag.lower())
            if tag not in tag_dict:
                tag_dict[tag] = set()
            tag_dict[tag].add(f"{artist_name} - {track_name}")

    # Convert the artist dictionary to a list of Artist objects
    artists = []
    for artist_name, tags in artist_dict.items():
        artist = Artist(artist_name)
        for tag in tags:
            artist.add_tag(tag)
        artists.append(artist)

    with open('output_tracks.txt', 'w', encoding='utf-8') as f:
        for track in tracks:
            f.write(f"{track}\n")

    with open('output_artists.txt', 'w', encoding='utf-8') as f:
        for artist in artists:
            f.write(f"{artist}\n")

    return tracks, artists, tag_dict, artist_dict

def run_spotify_api():
    # Placeholder for running Spotify API functions
    pass