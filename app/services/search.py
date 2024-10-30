from utils import remove_non_alphabetic

def search_by_artist(artist_name, tracks):
    tracks_by_artist = [track.name for track in tracks if track.artist.lower() == artist_name.lower()]
    if not tracks_by_artist:
        print(f"No tracks found for artist '{artist_name}'.")
        return
    
    print(f"Artist: {artist_name}")
    for i in range(0, len(tracks_by_artist), 4):
        print(" - ".join(tracks_by_artist[i:i + 4]))

def search_by_tag(tag, tag_dict):
    formatted_tag = remove_non_alphabetic(tag.lower())
    
    # Find all tags containing the search substring
    matching_tags = [key for key in tag_dict.keys() if formatted_tag in key]
    
    if matching_tags:
        if len(matching_tags) == 1:
            # If only one matching tag, display it directly
            selected_tag = matching_tags[0]
            print(f"\nTag found: {selected_tag}")
        else:
            # If multiple matching tags, display them with a selector
            print("\nMultiple matching tags found:")
            for i, tag in enumerate(matching_tags, 1):
                print(f"{i}: {tag}")

            while True:
                choice = input("Enter the number of the tag you want to view, or 'n' to skip: ").strip().lower()
                if choice == 'n':
                    print("No tag selected.")
                    return
                if not choice.isdigit() or not (0 < int(choice) <= len(matching_tags)):
                    print(f"Invalid choice. Please enter a number between 1 and {len(matching_tags)} or 'n' to skip.")
                    continue

                # Get the selected tag
                selected_tag = matching_tags[int(choice) - 1]
                print(f"\nTag selected: {selected_tag}")
                for track in sorted(tag_dict[selected_tag]):
                    print(track)
                break
    else:
        print(f"No tags found containing '{tag}'.")


def search_by_name(track_name, tracks, artist_dict):
    found = False
    for track in tracks:
        # Check if the track name contains the search term
        matching = [track for track in tracks if track_name in track.name.lower()]
        if len(matching) == 1:
            track = matching[0]
            print(f"\nTrack found: {track}")
            print(f"Tags: {', '.join(track.tags)}")
            # Print additional possible tags using the artist's tags
            artist_tags = artist_dict.get(track.artist)
            if artist_tags:
                print(f"Artist tags: {', '.join(artist_tags)}")
            found = True
        else:
            print(f"Multiple tracks found for '{track_name}':")
            for i, track in enumerate(matching, 1):
                print(f"{i}: {track} by {track.artist}")

            while True:
                choice = input("Enter the number of the track you want to view, or 'n' to skip: ").strip().lower()
                if choice == 'n':
                    break
                if not choice.isdigit() or not (0 < int(choice) <= len(matching)):
                    print(f"Invalid choice. Please enter a number between 1 and {len(matching)} or 'n' to skip.")
                    continue

                # Get the selected track and display details
                track = matching[int(choice) - 1]
                print(f"\nTrack found: {track}")
                print(f"Tags: {', '.join(track.tags)}")

                # Display additional possible tags from the artist's tags
                artist_tags = artist_dict.get(track.artist)
                if artist_tags:
                    print(f"Artist tags: {', '.join(artist_tags)}")
                
                # Break the outer loop after selecting and displaying the track
                found = True
                break
            break
    if not found:
        print("Track not found.")