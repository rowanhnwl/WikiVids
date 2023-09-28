import os
import gtts
import pyttsx3
import cv2
from moviepy.video.VideoClip import ImageClip
from moviepy.editor import *
from mutagen.mp3 import MP3
import numpy as np

import parsegpt

# Class for a individual video sections
class vid_element:
    # Length of the title gap
    TITLE_LENGTH = MP3("files/base/gap.mp3").info.length

    # Class constructor
    def __init__(self, title, text, audio, images, length, start):
        self.title = title
        self.text = text
        self.audio = audio
        self.images = images
        self.length = length
        self.start = start

    # Set the path to the respective audio file
    def set_audio(self, index):
        tts_audio = gtts.gTTS(self.text)
        audio_save_path = "files/audio/audio_clip_" + str(format(index, '02d')) + ".mp3"
        tts_audio.save(audio_save_path)

        self.audio = audio_save_path

    # Set the title
    def set_title(self):

        self.title = parsegpt.get_summary(self.text)

    # Set the length (s) of the audio
    def set_length(self):
        tts_audio = MP3(self.audio)

        self.length = tts_audio.info.length
    
# Generate the stream of images
def image_stream(elems):
    # Path to the images
    image_path = "files/images"
    
    images = os.listdir(image_path)
    images.sort()
    n_images = len(images)

    image_clips = []
    image_count = 0

    # Add a title and image for each audio section
    for elem in elems:
        title_clip = get_title_text(elem)
        image_clips.append(title_clip)

        full_path = os.path.join(image_path, images[image_count % n_images])
        image_clip = ImageClip(img=full_path, duration=elem.length)
        image_clips.append(image_clip)

        image_count += 1

    # Add the outro frame
    outro_image = cv2.imread("files/base/outro.png")
    outro_image = cv2.cvtColor(outro_image, cv2.COLOR_BGR2RGB)
    shape = cv2.imread(os.path.join("files/images", os.listdir("files/images")[0])).shape[:2]
    outro_image = cv2.resize(outro_image, (shape[1], shape[0]))

    outro_clip = ImageClip(img=outro_image, duration=vid_element.TITLE_LENGTH)
    image_clips.append(outro_clip)

    # Concatenate the clips
    full_image_stream = concatenate_videoclips(image_clips)
    full_image_stream.fps = 10

    full_image_stream.close()

    return full_image_stream

# Add borders to images such that they are all the same resolution
def set_image_sizes():
    # Path to the images
    image_path = "files/images"
    images = os.listdir(image_path)

    # Find the maximum height and width of the images
    max_height = 0
    max_width = 0
    for image in images:
        print(image)
        im = cv2.imread(os.path.join(image_path, image))
        h = im.shape[0]
        w = im.shape[1]

        if h > max_height:
            max_height = h
        if w > max_width:
            max_width = w

    # Resize all of the images accordingly
    for image in images:
        im = cv2.imread(os.path.join(image_path, image))
        delta_h = max_height - im.shape[0]
        delta_w = max_width - im.shape[1]

        im_padded = []

        if delta_w % 2 == 0:
            im_padded = cv2.copyMakeBorder(im, 0, 0, int(delta_w / 2), int(delta_w / 2), borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
        else:
            im_padded = cv2.copyMakeBorder(im, 0, 0, int(delta_w / 2), int(delta_w / 2) + 1, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
        
        if delta_h % 2 == 0:
            im_padded = cv2.copyMakeBorder(im_padded, int(delta_h / 2), int(delta_h / 2), 0, 0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
        else:
            im_padded = cv2.copyMakeBorder(im_padded, int(delta_h / 2), int(delta_h / 2) + 1, 0, 0, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
            
        cv2.imwrite(os.path.join(image_path, image), im_padded)

# Find the font scale for each title
def get_optimal_font_scale(text, width):
    s_range = np.arange(0.0, 60.0, 0.5)
    s_range = s_range[::-1]

    # Decrease a font scale until the text is less wide than the frame
    for scale in s_range:
        text_size = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=scale/10, thickness=1)
        new_width = text_size[0][0]

        if (new_width <= width):
            return scale/10, new_width

    return 1, width

# Create an image clip for each title
def get_title_text(elem):
    # Path to the background image
    bg_path = "files/base/title_bg.png"
    bg = cv2.imread(bg_path)

    # Get the resolution
    shape = cv2.imread(os.path.join("files/images", os.listdir("files/images")[0])).shape[:2]

    # Add text to the background
    title_image = bg.copy()
    title_image = cv2.resize(title_image, (shape[1], shape[0]))
    scale, t_width = get_optimal_font_scale(elem.title, shape[1])
    title_image = cv2.putText(title_image, elem.title, (int((shape[1] - t_width) / 2), int(shape[0] / 2) + int(scale * 10)), cv2.FONT_HERSHEY_COMPLEX, scale, (0, 0, 255), 2)
    title_clip = ImageClip(img=title_image, duration=vid_element.TITLE_LENGTH)

    return title_clip
        
# Create the stream of audio files
def audio_stream(elems):
    # Path to the title gap
    silence_path = "files/base/gap.mp3"
    silence = AudioFileClip(silence_path, fps=44100)

    audio_clips = []

    # Append audio clips, with silence between them
    for elem in elems:   
        audio_clips.append(silence)

        audio_clip = AudioFileClip(elem.audio, fps=44100)
        audio_clips.append(audio_clip)

    audio_clips.append(silence)

    # Concatenate the clips
    full_audio = concatenate_audioclips(audio_clips)

    return full_audio