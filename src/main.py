import wikipediaapi
import requests
import os
import argparse

import wikicalls
import parsegpt
import videoelements

# Enable argument parsing
def argument_parsing():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', type=str, default='Turkmenistan', help="The topic of the video")
    parser.add_argument('--word_count', type=int, default=700, help="The number of words in the script")
    parser.add_argument('--max_pictures', type=int, default=100, help="The maximum number of pictures to be displayed")

    args = vars(parser.parse_args())

    title = args["title"]
    word_count = args["word_count"]
    max_pictures = args["max_pictures"]

    return title, word_count, max_pictures

# Initialize the application
def init_process():
    # Set a request session
    S = requests.Session()

    # API endpoint
    URL = "https://en.wikipedia.org/w/api.php"

    # Credentials
    tf = open('authorization/token.txt', 'r')
    token = tf.read()

    ef = open('authorization/email.txt', 'r')
    email = ef.read()

    headers = {
        'Authorization' : 'Bearer ' + token,
        'User-Agent' : 'WikiVids (' + email + ')'
    }

    # Clear media directories
    for file in os.listdir('files/images'):
        os.remove(os.path.join('files/images', file))
    
    for file in os.listdir('files/audio'):
        os.remove(os.path.join('files/audio', file))

    return S, URL, headers

# Validate the wikimedia call
def w_validate(title):
    # Initialize a wikipedia object
    wiki_init = wikipediaapi.Wikipedia('en')

    # Generate a page object
    page = wiki_init.page(title)
    assert page.exists()

# Query the GPT API
def gpt_query(title, word_count):
    # GPT Text Generation
    script = parsegpt.get_script(title, word_count)
    paragraphs = parsegpt.split_paragraphs(script)

    word_threshold = 10
    paragraphs = parsegpt.remove_titles(paragraphs, word_threshold)

    return paragraphs

# Generate the video elements
def get_vid_elements(title, paragraphs):
    # Create video elements
    video_elements = []

    pg_count = 0
    time_count = 0
    
    # Get video elements
    for pg in paragraphs:
        # Create a new video element object
        new_vid_element = videoelements.vid_element(None, None, None, None, None, None)
    
        # Set the members
        new_vid_element.text = pg
        if pg_count == 0:
            new_vid_element.title = title
        elif pg_count == len(paragraphs) - 1:
            new_vid_element.title = "Conclusion"
        else:
            new_vid_element.set_title()
        new_vid_element.set_audio(pg_count)
        new_vid_element.set_length()
        new_vid_element.start = time_count

        video_elements.append(new_vid_element)

        pg_count += 1
        time_count += new_vid_element.length + videoelements.vid_element.TITLE_LENGTH

    return video_elements

# Generate the full video (visuals and audio)
def get_full_video(video_elements):
    # Generate the audio stream
    audio_stream = videoelements.audio_stream(video_elements)

    # Generate the image stream
    videoelements.set_image_sizes()
    image_stream = videoelements.image_stream(video_elements)

    # Overlay the audio
    image_stream.audio = audio_stream

    return image_stream

def main():
    # Get the command line arguments
    title, word_count, max_pictures = argument_parsing()

    # Initialize API parameters and directories
    S, URL, headers = init_process()

    # Ensure that the wikipedia content exists
    w_validate(title)

    # Get images
    wikicalls.get_images(S, URL, title, headers, max_pictures)

    # GPT Text Generation
    paragraphs = gpt_query(title, word_count)

    # Generate the video elements
    video_elements = get_vid_elements(title, paragraphs)

    # Generate the full video
    full_video = get_full_video(video_elements)

    # Save the video
    full_video.write_videofile("files/video/Geology/" + title + ".mp4", codec='libx264')

if __name__ == "__main__":
    main()