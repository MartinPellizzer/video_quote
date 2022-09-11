from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops

# import pyttsx3
import csv
import random
import subprocess
import os
import shutil
import re

import requests
from bs4 import BeautifulSoup

import pandas as pd
import time

ACCESS_KEY = 'Yg_eQCJYfLgimuVXSGDlDnJNMndeyc1fefL7fi9JZhs'
BG_RAW_FILENAME = './data/tmp/bg_raw.jpg'
BG_FINAL_FILENAME = './data/tmp/bg_final.jpg'
BG_RAW_VIDEO_FILENAME = './data/tmp/bg_raw.mp4'

IMAGE_SIZE = (1080, 1920)
OPACITY_VAL = 0.7
FONT_SIZE = int(IMAGE_SIZE[0]*0.06)
NUM_CHARS_X_LINE = IMAGE_SIZE[0]//FONT_SIZE*2
FONT_FAMILY = './fonts/Roboto-Regular.ttf'



#########################################################################
# SCRAPE QUOTES
#########################################################################

def sanitize_string(s):
    chars_to_remove = ['“', '”', '"']
    new_string = ''
    for c in s:
        if c not in chars_to_remove:
            new_string += c

    new_string = new_string.strip()
    return new_string

def scrape_quotes():
    filename = 'quotes.csv'

    try: os.remove(filename)
    except: pass

    for i in range(10):
        try: print(f'Scraping page {i}...')
        except: pass
        time.sleep(2)
        params = {
            'q': 'fyodor dostoyevsky',
            'page': i,
        }

        response = requests.get('https://goodreads.com/quotes/search', params=params)
        soup = BeautifulSoup(response.content, 'html.parser')

        quotes_text = [sanitize_string(q.contents[0]) for q in soup.find_all(class_='quoteText')]
        quotes_author = [q.getText().strip().replace(',', '') for q in soup.find_all(name='span', class_='authorOrTitle')]

        quotes = []
        for i in range(len(quotes_text)):
            print(quotes_text[i], quotes_author[i])
            quotes.append([quotes_text[i], quotes_author[i]])

        with open(filename, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerows(quotes)


#########################################################################
# QUOTE TEXT
#########################################################################

def get_random_quote():
	df = pd.read_csv('./data/quotes.csv', encoding='cp1252', on_bad_lines='skip', sep='|', header=None)
	quote = random.choice(df.values.tolist())

	# DEBUG --------------------------------
	print()
	for q in quote:
		print(q)
	print()
	# --------------------------------------

	return quote



#########################################################################
# QUOTE AUDIO
#########################################################################

def create_text_file(quote):
	textfile_path = './data/tmp/00.txt'
	with open(textfile_path, 'w') as f: 
		f.write(quote[0])

	# DEBUG --------------------------------
	print(f'text file created in path: {textfile_path}')
	print()
	# --------------------------------------
        

def create_audio_file(quote):
	audiofile_path = './data/tmp/00.mp3'
	engine = pyttsx3.init()
	engine.save_to_file(quote[0], audiofile_path)
	engine.runAndWait()


	# DEBUG --------------------------------
	print(f'audio file created in path: {audiofile_path}')
	print()
	# --------------------------------------


#########################################################################
# QUOTE VIDEO
#########################################################################
def download_pexels_video():  
    response = requests.get('https://api.pexels.com/videos/popular', 
        headers = {'Authorization': '563492ad6f91700001000001f82c18c9ebb1445db510d2e8e54e9902'},
    )
    data = response.json()
    print(data)
    print()
    print()
    print()
    print(data['videos'][0]['video_files'][0]['link'])
    
    for i, video in enumerate(data['videos']):
        url = video['video_files'][0]['link']
        print(url)

        # url = 'https://player.vimeo.com/external/296210754.hd.mp4?s=08c03c14c04f15d65901f25b542eb2305090a3d7&profile_id=175&oauth2_token_id=57447761'
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(f'./assets/tmp/03_bg_videos/{i:02d}.mp4', 'wb') as f:
                for chunk in response:
                    f.write(chunk)


#########################################################################
# QUOTE VIDEO + AUDIO + TEXT
#########################################################################
def create_clips(num_attempts):
    with open(f'./assets/tmp/csv/quotes.csv', encoding='utf-8') as f:
        rows = csv.reader(f, delimiter='|')
        quotes = [quote for quote in rows]

    for i, quote in enumerate(quotes):
        if i >= num_attempts: break

        quote_content = quote[0].replace('“', '').replace('”', '').replace('"', '')
        quote_author = quote[1]
        print("------------------------------------------------------------------")
        print(i)
        print(quote_content)
        print(quote_author)
        print(len(quote_content))
        print("------------------------------------------------------------------")

        if len(quote_content) < 240:
            create_clip(quote_content, i)

def create_clip(quote_content, i):
    gap_sec = 2

    # audio ---------------------------------------
    tts_audio_clip = AudioFileClip(f'./assets/tmp/tts/{i:02d}.wav')

    # image ---------------------------------------
    BG_IMAGE = './assets/bg/bg.png' 
    image_clip = ImageClip(BG_IMAGE)
    image_clip = image_clip.set_duration(tts_audio_clip.duration + gap_sec*2)
    image_clip = image_clip.set_audio(tts_audio_clip)

    # text ----------------------------------------
    image_size = (1920, 1080)
    # quote_text = f'"{quote_content}"\n\n- {quote_author}'
    quote_text = f'"{quote_content}"'
    text_clip = TextClip(
        quote_text, 
        size=(image_size[0]//2 - image_size[0]//8, image_size[1]), 
        fontsize=FONT_SIZE, 
        color='white', 
        method='caption', 
        align='center',
    )
    text_clip = text_clip.set_position((image_size[0]//2 + image_size[0]//8//2, 0))
    text_clip = text_clip.set_duration(tts_audio_clip.duration + gap_sec*2)

    # video ---------------------------------------
    video_clip = image_clip.set_audio(tts_audio_clip.set_start(gap_sec))
    final_clip = CompositeVideoClip([video_clip, text_clip.set_start(0).crossfadein(gap_sec).crossfadeout(gap_sec)])

    print(f'./assets/tmp/clips/{i:02d}.mp4')
    final_clip.write_videofile(f'./assets/tmp/clips/{i:02d}.mp4', fps=24, codec='libx264', audio_codec='aac')


def concate_clips(clips_num):
    # tts_audio_clip = AudioFileClip(f'./assets/tmp/tts/{i:02d}.wav')
    # background_audio_clip = AudioFileClip('./data/audio/bg.mp3')
    # background_audio_clip = background_audio_clip.subclip(0, tts_audio_clip.duration + gap_sec*2)
    # background_audio_clip = background_audio_clip.volumex(0.5) 
    # final_audio = CompositeAudioClip([tts_audio_clip.set_start(gap_sec), background_audio_clip])
    
    clips_path = [f'./assets/tmp/clips/{clip}' for clip in os.listdir('./assets/tmp/clips/')[:clips_num]]
    clips = [VideoFileClip(clip_path) for clip_path in clips_path]
    concat_clip = concatenate_videoclips(clips, method='compose')

    concat_clip.write_videofile("final.mp4")


# scrape_quotes()

# quote = get_random_quote()
# create_text_file(quote)
# create_audio_file(quote)
# download_unsplash_random_image()
# download_pexels_video()
# edit_image()

'''
for f in os.listdir(f'./assets/tmp/clips/'):
    os.remove(f'./assets/tmp/clips/{f}')

for i in range(len(os.listdir(f'./assets/tmp/tts/'))):
    create_clip(i)

'''

# create_clips(3)

# concate_clips(len(os.listdir(f'./assets/tmp/tts/')))

# create_video2(quote)

command = ' \
ffmpeg -y \
-loop 1 \
-framerate 24 \
-i ./assets/bg/bg.png \
-i ./assets/tmp/tts_mp3/00.mp3 \
-c:v libx264 \
-preset fast \
-tune stillimage \
-crf 18 \
-c:a copy \
-shortest \
-pix_fmt yuv420p \
output.mp4 \
'

def wav_to_mp3():
    for f in os.listdir("./assets/tmp/tts_wav/"):
        f_out = f.replace('.wav', '.mp3')
        os.system(f'ffmpeg -y -i ./assets/tmp/tts_wav/{f} ./assets/tmp/tts_mp3/{f_out}')


# def image_to_va():
#     for f in os.listdir("./assets/tmp/tts_mp3/"):
#         f_out = f.replace('.mp3', '.mp4')
#         os.system(f' \
#             ffmpeg \
#             -y \
#             -loop 1 \
#             -framerate 24 \
#             -i ./assets/bg/bg.png \
#             -i ./assets/tmp/tts_mp3/{f} \
#             -c:v libx264 \
#             -preset fast \
#             -tune stillimage \
#             -crf 18 \
#             -c:a copy \
#             -shortest \
#             -pix_fmt yuv420p \
#             ./assets/tmp/clips/{f_out} \
#         ')






key_word = 'fyodor dostoevsky'


video_raw_path = './assets/tmp/bg/00_videos_raw/'
normalize_path = './assets/tmp/bg/01_videos_normalize/'
dark_path = './assets/tmp/bg/02_videos_normalize_dark/'
videos_text_path = './assets/tmp/bg/videos_text/'
video_tts_path = './assets/tmp/bg/03_videos_tts/'
tts_wav_path = './assets/tmp/tts_wav/'
tts_mp3_path = './assets/tmp/tts_mp3/'
h264_an_folder = './assets/tmp/bg/h264_an/'


def wav_to_mp3_advanced():
    for f in os.listdir("./assets/tmp/tts_wav/"):
        f_out = f.replace('.wav', '.mp3')
        os.system(f'ffmpeg -y \
                    -i {tts_wav_path}{f} \
                    -af loudnorm \
                    -c:a mp3 \
                    -b:a 256k \
                    -ar 48000 \
                    -ac 2 \
                    {tts_mp3_path}{f_out} \
                ')
# wav_to_mp3_advanced()


def normalize():
    input_folder = './assets/tmp/bg/00_videos_raw/'
    output_folder = normalize_path
    for video in os.listdir(input_folder):
        os.system(f'ffmpeg -y \
                    -i {input_folder}{video} \
                    -to 00:00:15 \
                    -map 0:0 \
                    -c:v h264 \
                    -crf 18 \
                    -b:v 500k \
                    -pix_fmt yuv420p \
                    -vf " \
                        yadif, \
                        scale=1280:-1, \
                        crop=1280:720 \
                    " \
                    -video_track_timescale 60000 \
                    -an \
                    {output_folder}{video} \
                ') 
# normalize()

def convert_h264_an():
    input_folder = video_raw_path
    output_folder = h264_an_folder
    for video in os.listdir(input_folder):
        os.system(f'ffmpeg -y \
                    -i {input_folder}{video} \
                    -c:v h264 \
                    -b:v 1M \
                    -preset medium \
                    -tune film \
                    -crf 23 \
                    -an \
                    {output_folder}{video} \
                ') 

# convert_h264_an()



def normalize_2():
    input_folder = './assets/tmp/bg/00_videos_raw/'
    output_folder = normalize_path
    for video in os.listdir(input_folder):
        os.system(f'ffmpeg -y \
                    -i {input_folder}{video} \
                    -to 00:00:15 \
                    -map 0:0 \
                    -c:v h264 \
                    -crf 18 \
                    -b:v 500k \
                    -pix_fmt yuv420p \
                    -vf " \
                        yadif, \
                        scale=1280:-1, \
                        crop=1280:720 \
                    " \
                    -video_track_timescale 60000 \
                    -an \
                    {output_folder}{video} \
                ') 
# normalize_2()
# fps=24, \

# os.system(f'ffprobe {normalize_path}00.mp4 -hide_banner')
# os.system(f'ffprobe {normalize_path}01.mp4 -hide_banner')

def dark():
    input_folder = normalize_path
    output_folder = dark_path
    for video in os.listdir(input_folder):
        os.system(f'ffmpeg \
                    -y \
                    -i {input_folder}{video} \
                    -f lavfi \
                    -i "color=black:s=1280x720" \
                    -filter_complex " \
                        blend=shortest=1: \
                        all_mode=normal: \
                        all_opacity=0.33 \
                    " \
                    {output_folder}{video} \
                ')
# dark()




def concat(input_folder):
    with open("concat_list.txt", "w") as f:
        for clip in os.listdir(input_folder):
            f.write(f"file '{input_folder}{clip}'\n")


    os.system(f'ffmpeg -y \
                -f concat \
                -safe 0 \
                -segment_time_metadata 1 \
                -i concat_list.txt \
                -vf "select=concatdec_select,setpts=N/FR/TB" \
                -af "aselect=concatdec_select,aresample=async=1" \
                output.mp4 \
            ')

# -vf "select=concatdec_select,setpts=N/FR/TB" \
# -af "aselect=concatdec_select,aresample=async=1" \
# -segment_time_metadata 1 \
# concat(video_tts_path)

# lufs
('ffmpeg \
    -i audio.mp3 \
    -af " \
        loudnorm= \
            I=-14: \
            TP=-3: \
            LRA=11: \
            print_format=json \
    " \
    -f mp3 \
    output.mp3 \
')

# concat
('ffmpeg \
    -i 1.mp3 -i 2.mp3 -i 3.mp3 \
    -filter_complex " \
        [0:0][1:0][2:0]concat=n=4:v=0:a=1[out] \
    " \
    -map "[out]" \
    output.mp3 \
')

# mix
('ffmpeg \
    -i 1.mp3 -i 2.mp3 -i 3.mp3 \
    -filter_complex " \
        amix= \
            inputs=3: \
            duration=first: \
            dropout_transition=3 \
    " \
    output.mp3 \
')


# def normalize_audio():
#     input_folder = './assets/tmp/bg/01_videos_trim_scale_crop/'
#     output_folder = './assets/tmp/bg/09_videos_output/'
#     for video in os.listdir(input_folder):
#         os.system(f'ffmpeg -y \
#                     -i {input_folder}{video} \
#                     -c:v copy \
#                     -c:a mp3 -b:a 192k -ar 44100 -ac 2 \
#                     {output_folder}{video} \
#                 ')



####################################################################################
# RESIZE
####################################################################################
def normalize_3():
    input_folder = video_raw_path
    output_folder = normalize_path
    for video in os.listdir(input_folder):
        os.system(f'ffmpeg -y \
                    -i {input_folder}{video} \
                    -to 00:00:15 \
                    -c:v h264 \
                    -crf 18 \
                    -vf " \
                        scale=1280:-1, \
                        crop=1280:720 \
                    " \
                    -aspect 1280:720 \
                    -an \
                    {output_folder}{video} \
                ')
# normalize_3()

def dark_2():
    input_folder = normalize_path
    output_folder = dark_path
    for video in os.listdir(input_folder):
        os.system(f'ffmpeg \
                    -y \
                    -i {input_folder}{video} \
                    -f lavfi \
                    -i "color=black:s=1280x720" \
                    -filter_complex " \
                        blend=shortest=1: \
                        all_mode=normal: \
                        all_opacity=0.33 \
                    " \
                    {output_folder}{video} \
                ')
# dark_2()


def add_text_to_videos():
    with open(f'./assets/tmp/csv/quotes.csv', encoding='utf-8') as f:
        rows = csv.reader(f, delimiter='|')
        quotes = [quote for quote in rows]

    input_folder = dark_path
    output_folder = videos_text_path
    for i, video in enumerate(os.listdir(input_folder)):
        quote = quotes[i][0].replace(':', '\\:').replace("'", "\u2019")
        lines = []
        tmp_line = ''
        for word in quote.split(' '):
            if len(tmp_line) + len(word) < 36:
                tmp_line += word + ' '
            else:
                lines.append(tmp_line)
                tmp_line = word + ' '
        lines.append(tmp_line)

        font_family = './fonts/arial/arial.ttf'
        font_size = 56

        print()
        print()
        print(quote)
        print()
        for q in lines:
            print(q)
        print()

        line_height = 1.0
        drawtext_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                drawtext_lines.append(f'text=\'{line}\':\
                                        fontfile=:{font_family}:\
                                        fontsize={font_size}:\
                                        fontcolor=white:\
                                        x=w*0.5-text_w/2:\
                                        y=(h-text_h)/2+({font_size*i*line_height})-({font_size//2*len(lines)})\
                                    ')
            else:
                drawtext_lines.append(f',drawtext=\
                                            text=\'{line}\':\
                                            fontfile={font_family}:\
                                            fontsize={font_size}:\
                                            fontcolor=white:\
                                            x=w*0.5-text_w/2:\
                                            y=(h-text_h)/2+({font_size*i*line_height})-({font_size//2*len(lines)})\
                                    ')
        lines = ''.join(drawtext_lines)
        
        command = (f'ffmpeg -y -hide_banner \
                    -i {input_folder}{video} \
                    -vf drawtext="{lines}" \
                    {output_folder}{video} \
                ')

        print(re.sub(' +', ' ', command))
        print()
        print()

        os.system(command)
# add_text_to_videos()


def add_tts():
    input_video_folder = videos_text_path
    input_audio_folder = tts_mp3_path
    output_folder = video_tts_path
    for i in range(len(os.listdir(input_video_folder))):
        os.system(f'ffmpeg -y \
                    -i {input_video_folder}{i:02d}.mp4 \
                    -i {input_audio_folder}{i:02d}.mp3 \
                    -c:v copy \
                    -map 0:v:0 \
                    -map 1:a:0 \
                    -shortest \
                    {output_folder}{i:02d}.mp4  \
                ')
add_tts()

####################################################################################
# CONCAT
####################################################################################
inputs_list = [f'{video_tts_path}{video}' for video in os.listdir(video_tts_path)]


# for i in inputs_list:
#     print(i)

# quit()
# inputs_str += f'-i {video_tts_path}{video} '
    
# print(inputs_str)
# quit()

# quit()

input_folder = video_tts_path
os.system(f'ffmpeg -y \
            -i {input_folder}00.mp4 \
            -i {input_folder}01.mp4 \
            -i {input_folder}02.mp4 \
            -i {input_folder}03.mp4 \
            -i {input_folder}04.mp4 \
            -i {input_folder}05.mp4 \
            -i {input_folder}06.mp4 \
            -i {input_folder}07.mp4 \
            -i {input_folder}08.mp4 \
            -i {input_folder}09.mp4 \
            -i {input_folder}10.mp4 \
            -i {input_folder}11.mp4 \
            -i {input_folder}12.mp4 \
            -i {input_folder}13.mp4 \
            -i {input_folder}14.mp4 \
            -filter_complex " \
                [0:v] [0:a] \
                [1:v] [1:a] \
                [2:v] [2:a] \
                [3:v] [3:a] \
                [4:v] [4:a] \
                [5:v] [5:a] \
                [6:v] [6:a] \
                [7:v] [7:a] \
                [8:v] [8:a] \
                [9:v] [9:a] \
                [10:v] [10:a] \
                [11:v] [11:a] \
                [12:v] [12:a] \
                [13:v] [13:a] \
                [14:v] [14:a] \
                concat=n=15:v=1:a=1 [v] [a] \
            " \
            -map "[v]" -map "[a]" \
            output.mp4 \
        ') 



# -i ./assets/tmp/bg/03_videos_tts/04.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/05.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/06.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/07.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/08.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/09.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/10.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/11.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/12.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/13.mp4 \
# -i ./assets/tmp/bg/03_videos_tts/14.mp4 \





'''
ffmpeg -i opening.mkv -i episode.mkv -i ending.mkv \
-filter_complex "[0:v] [0:a] [1:v] [1:a] [2:v] [2:a] \
concat=n=3:v=1:a=1 [v] [a]" \
-map "[v]" -map "[a]" output.mkv
'''