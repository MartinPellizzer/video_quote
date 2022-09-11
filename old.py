

#########################################################################
# QUOTE IMAGE
#########################################################################

# download unsplash random image
def download_unsplash_random_image():
    url = f'https://api.unsplash.com/photos/random?client_id={ACCESS_KEY}'
    response = requests.get(url)
    data = response.json()
    image_url = data['urls']['full']
    image_response = requests.get(image_url, stream=True)
    if image_response.status_code == 200:
        with open(BG_RAW_FILENAME, 'wb') as image_file:
            for chunk in image_response:
                image_file.write(chunk)


# backgroud image
def edit_image():
    bg = Image.open(BG_RAW_FILENAME).convert('RGBA')
    bg = ImageOps.fit(image=bg, size=IMAGE_SIZE)
    bg_overlay = Image.new('RGBA', size=IMAGE_SIZE, color=(0, 0, 0, 255))
    bg = ImageChops.blend(bg, bg_overlay, OPACITY_VAL).convert('RGB')
    bg.save(BG_FINAL_FILENAME)


def get_handmade_image():
	return './assets/bg/bg' 
    

'''
os.system(f'ffmpeg -y \
            -i ./assets/tmp/clips/00.mp4 \
            -vf \
                drawtext="\
                    text=\'{quote_text}\':\
                    fontfile=./fonts/lato/Lato-Regular.ttf:\
                    fontsize={font_size}:\
                    fontcolor=white:\
                    x=(w-text_w)/2:\
                    y=(h-text_h)/2\
                "\
            output.mp4 \
        ')
'''

'''
os.system(f'ffmpeg -y \
            -i ./assets/tmp/clips/00.mp4 \
            -vf \
                drawtext="\
                    text=\'{quote_text}\':\
                    fontfile=.fonts/lato/Lato-Regular.ttf:\
                    fontsize=120:\
                    fontcolor=purple:\
                    x=(w-text_w)/2:\
                    y=(h-text_h)/2:\
                    shadowcolor=black:\
                    shadowx=2:\
                    shadowy=2:\
                    box=1:\
                    boxcolor=white@0.8:\
                    boxborderw=5\
                "\
            output.mp4 \
        ')
'''

def create_landscape_clip():
	with open('./data/tmp/00.txt') as f:
		quote = f.readlines()

	# DEMO
	quote.append('- unknown')
	
	gap_sec = 2
	
	# audio
	quote_audio_clip = AudioFileClip('./data/tmp/00.wav')
	background_audio_clip = AudioFileClip('./data/audio/bg.mp3')
	background_audio_clip = background_audio_clip.subclip(0, quote_audio_clip.duration + gap_sec*2)
	background_audio_clip = background_audio_clip.volumex(0.5) 
	final_audio = CompositeAudioClip([quote_audio_clip.set_start(gap_sec), background_audio_clip])

	# image ---------------------------------------
	BG_IMAGE = './assets/bg/bg.png' 
	image_clip = ImageClip(BG_IMAGE)
	image_clip = image_clip.set_duration(quote_audio_clip.duration + gap_sec*2)
	image_clip = image_clip.set_audio(quote_audio_clip)

	# text ----------------------------------------
	image_size = (1920, 1080)
	quote_text = f'"{quote[0]}"\n\n- {quote[1]}'
	text_clip = TextClip(
		quote_text, 
		size=(image_size[0]//2 - image_size[0]//8, image_size[1]), 
		fontsize=FONT_SIZE, 
		color='white', 
		method='caption', 
		align='center'
	)
	text_clip = text_clip.set_position((image_size[0]//2 + image_size[0]//8//2, 0))
	text_clip = text_clip.set_duration(quote_audio_clip.duration + gap_sec*2)

	# video ---------------------------------------
	video_clip = image_clip.set_audio(final_audio)
	final_clip = CompositeVideoClip([video_clip, text_clip.set_start(0).crossfadein(gap_sec).crossfadeout(gap_sec)])
	#final_clip = CompositeVideoClip([video_clip, txt_clip.set_start(1).crossfadein(2).crossfadeout(2)])


	final_clip.write_videofile('final_video.mp4', fps=24, codec='libx264', audio_codec='aac')


def create_youtube_video(quote):
	audio_clip = AudioFileClip('./data/tmp/00.mp3')

	# image ---------------------------------------
	BG_IMAGE = './assets/bg/bg' 
	image_clip = ImageClip(BG_IMAGE).set_duration(audio_clip.duration+2).set_audio(audio_clip)
	background_audio_clip = AudioFileClip('./data/audio/bg.mp3').subclip(0, image_clip.duration).volumex(0.5)

	final_audio = CompositeAudioClip([audio_clip.set_start(1), background_audio_clip])
	video_clip = image_clip.set_audio(final_audio)

	quote_text = f'"{quote[0]}"\n\n- {quote[1]}'
	txt_clip = TextClip(quote_text, size=(IMAGE_SIZE[0]-(IMAGE_SIZE[0]//8), IMAGE_SIZE[1]), 
		fontsize=FONT_SIZE, color='white', method='caption', align='center')
	txt_clip = txt_clip.set_position(((IMAGE_SIZE[0]//8)//2, 0)).set_duration(audio_clip.duration+1)
	#final_clip = CompositeVideoClip([video_clip, txt_clip.set_start(1).crossfadein(2).crossfadeout(2)])
	final_clip = CompositeVideoClip([video_clip, txt_clip.set_start(1).crossfadein(2)])

	final_clip.write_videofile('final_video.mp4', fps=24, codec='libx264', audio_codec='aac')


def create_video(quote):
    audio_clip = AudioFileClip('./data/tmp/00.mp3')
    image_clip = ImageClip("./data/tmp/bg_final.jpg").set_duration(audio_clip.duration+2).set_audio(audio_clip)
    background_audio_clip = AudioFileClip('./data/audio/bg.mp3').subclip(0, image_clip.duration).volumex(0.5)

    final_audio = CompositeAudioClip([audio_clip.set_start(1), background_audio_clip])
    video_clip = image_clip.set_audio(final_audio)

    quote_text = f'"{quote[0]}"\n\n- {quote[1]}'
    txt_clip = TextClip(quote_text, size=(IMAGE_SIZE[0]-(IMAGE_SIZE[0]//8), IMAGE_SIZE[1]), 
        fontsize=FONT_SIZE, color='white', method='caption', align='center')
    txt_clip = txt_clip.set_position(((IMAGE_SIZE[0]//8)//2, 0)).set_duration(audio_clip.duration+1)
    #final_clip = CompositeVideoClip([video_clip, txt_clip.set_start(1).crossfadein(2).crossfadeout(2)])
    final_clip = CompositeVideoClip([video_clip, txt_clip.set_start(1).crossfadein(2)])

    final_clip.write_videofile('final_video.mp4', fps=24, codec='libx264', audio_codec='aac')


def create_video2(quote):
    audioclip = AudioFileClip('./data/tmp/00.mp3')
    imageclip = ImageClip("opacity.png").set_duration(audioclip.duration)
    videoclip = VideoFileClip(BG_RAW_VIDEO_FILENAME)
    # 960 x 540
    videoclip = videoclip.resize(height=960)
    w, h = videoclip.size
    videoclip = videoclip.crop(x1=w//2-270, y1=0, x2=w//2+270, y2=h)

    # videoclip = videoclip.fx(vfx.colorx, 1.5)
    # videoclip = videoclip.fx(vfx.lum_contrast, 0, 50, 128)

    audio_duration = audioclip.duration
    videoclip = videoclip.set_duration(audio_duration)
    videoclip.audio = audioclip

    quote_text = f'"{quote[0].strip()}"\n\n- {quote[1]}'
    textclip = TextClip(quote_text, 
        size=(540-540//8, 960), 
        fontsize=50, 
        color='white', 
        method='caption', 
        align='center')
    textclip = textclip.set_position((540//8//2, 0))
    textclip = textclip.set_duration(audio_duration)

    videoclip = CompositeVideoClip([videoclip, imageclip])
    videoclip = CompositeVideoClip([videoclip, textclip.set_start(0).crossfadein(2)])

    videoclip.write_videofile('final_video.mp4')

    print(videoclip.size)




'''
audioclip = AudioFileClip('./data/tmp/00.mp3')
imageclip = ImageClip("./data/tmp/bg_final.jpg").set_duration(audioclip.duration)
videoclip = VideoFileClip('./data/samples/video_sample.mp4')

videoclip2 = imageclip.set_audio(audioclip)

quote_text_newlines = f'"{quote_text}"\n\n- {quote_author}'
#quote_text_newlines = 'Too many of us are not living our dreams because we are living our fears.'

txt_clip = TextClip(quote_text_newlines,
    size=IMAGE_SIZE,
    fontsize=FONT_SIZE, color='white', 
    method='caption', align='center')
txt_clip = txt_clip.set_position((0, 0)).set_duration(3)
video = CompositeVideoClip([videoclip2, txt_clip.set_start(0).crossfadein(3)])

video.write_videofile(f'output.mp4', fps=24)
'''

'''
quote_audio_clip = AudioFileClip('./data/tmp/00.mp3')
video_clip = VideoFileClip('output.mp4')
original_audio = video_clip.audio
original_audio.write_audiofile('original_audio.mp3')

background_audio_clip = AudioFileClip('audio1.mp3')
bg_music = background_audio_clip.subclip(0, video_clip.duration)

bg_music = bg_music.volumex(0.5)

final_audio = CompositeAudioClip([original_audio, bg_music])
final_audio.write_audiofile(f'output_audio.mp3', fps=original_audio.fps)

final_clip = video_clip.set_audio(final_audio)
final_clip.write_videofile('final_video.mp4', codec='libx264', audio_codec='aac')
'''



'''
# generate text and audio files
def create_tts(quotes):
    shutil.rmtree('./data/audio_clips')
    shutil.rmtree('./data/text_clips')
    engine = pyttsx3.init()
    for i, quote in enumerate(quotes):
        with open(f'./quote_clips/{i:02d}.txt', 'w') as f: f.write(quote[0])
        engine.save_to_file(quote, f'./audio_clips/{i:02d}.mp3')
        engine.runAndWait()
'''



'''
# load quotes from csv
def load_quotes():
    quotes = list()
    with open('./data/quotes.csv', 'r') as f:
        reader = csv.reader(f, delimiter="|")
        for row in reader:
            quotes.append(row)
    return quotes

# load quotes with pandas
def load_quotes_df():
    df = pd.read_csv('./data/quotes.csv', encoding='cp1252', on_bad_lines='skip', sep='|', header=None)
    return df.values.tolist()

# get 10 random quotes
def get_random_quotes(quotes):
    random.shuffle(quotes)
    random_quotes = []
    while len(random_quotes) < 10:
        tmp_quote = quotes.pop()
        if len(tmp_quote) < 280:
            random_quotes.append(tmp_quote)
    return random_quotes

def clear_folder():
    for f in os.listdir('./data/tmp'): os.remove(f'./data/tmp/{f}')
clear_folder()
'''



'''
quote = ''
run = True
while run:
    command = input('enter command: ')

    if command == 'q':
        run = False
    elif command == 'g':
        quote = get_random_quote()
        print(quote[0])
    elif command == 'c':
        quote = get_random_quote()
        # create_text_file(quote)
        # create_audio_file(quote)
        # download_unsplash_random_image()
        download_pexels_video()
        # edit_image()
        # create_video2(quote)
'''



'''
audio_clips = os.listdir('audio_clips')
quote_clips = os.listdir('quote_clips')

for audio_clip in audio_clips:
    quote_clip = audio_clip.replace('.mp3', '.txt')
    video_audio_clip = audio_clip.replace('.mp3', '.mp4')
    
    ffmpeg_command = f'ffmpeg -y -loop 1 \
                -i wallpaper.jpg -i ./audio_clips/{audio_clip} \
                -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest \
                ./video_audio_clips/{video_audio_clip}'

    #ffmpeg_command = f'ffmpeg -y -i wallpaper.jpg -i ./audio_clips/{audio_clip} ./video_audio_clips/{video_audio_clip}'
    subprocess.run(ffmpeg_command)
    audio = AudioFileClip(f'./audio_clips/{audio_clip}')
    clip = ImageClip('wallpaper.jpg').set_duration(audio.duration)
    clip = clip.set_audio(audio)
    clip.write_videofile(f'./video_audio_clips/{video_audio_clip}', fps=24)

'''


quit()


clip1 = VideoFileClip(f'./video_audio_clips/00.mp4')
clip2 = VideoFileClip(f'./video_audio_clips/01.mp4')
clips = [clip1, clip2]
final = concatenate_videoclips(clips)
final.write_videofile("merged.mp4")

quit()

# load clip
clip = VideoFileClip('video.mp4')

# get info
w, h = clip.size
print(w, h)
print(clip.duration)
print(clip.fps)


##################################################################################
# add text
##################################################################################
txt_clip = TextClip('Martin Pellizzer', fontsize=100, color='red')
txt_clip = txt_clip.set_position(lambda t: (20*t, 20*t)).set_duration(3)

video = CompositeVideoClip([clip, txt_clip.set_start(3).crossfadein(3)])


##################################################################################
# save clip
##################################################################################
video.write_videofile('export.mp4')




'''
response = requests.get('https://api.pexels.com/videos/popular', 
    headers = {'Authorization': '563492ad6f91700001000001f82c18c9ebb1445db510d2e8e54e9902'},
)
data = response.json()
print(data)

data['videos'][0]
['video_files'][0]['link']



quit()

url = f'https://api.unsplash.com/photos/random?client_id={ACCESS_KEY}'
response = requests.get(url)
data = response.json()
image_url = data['urls']['full']
image_response = requests.get(image_url, stream=True)
if image_response.status_code == 200:
    with open(BG_RAW_FILENAME, 'wb') as image_file:
        for chunk in image_response:
            image_file.write(chunk)


'''

('ffmpeg -y -hide_banner \
-i ./assets/tmp/bg/02_videos_normalize_dark/05.mp4 \
-vf drawtext="text='The world says, You have needs -- ': \
fontfile=:./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(0.0)-(352) \
,\
drawtext= text='satisfy them. You have as much ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(76.8)-(352) ,\
drawtext= text='right as the rich and the mighty. ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(153.6)-(352) ,\
drawtext= text='Don't hesitate to satisfy your ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(230.39999999999998)-(352) ,\
drawtext= text='needs, indeed, expand your needs ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(307.2)-(352) ,\
drawtext= text='and demand more. This is the ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(384.0)-(352) ,\
drawtext= text='worldly doctrine of today. And they ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(460.79999999999995)-(352) ,\
drawtext= text='believe that this is freedom. The ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(537.6)-(352) ,\
drawtext= text='result for the rich is isolation ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(614.4)-(352) ,\
drawtext= text='and suicide, for the poor, envy and ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(691.1999999999999)-(352) ,\
drawtext= text='murder. ': \
fontfile=./fonts/arial/arial.ttf: \
fontsize=64: \
fontcolor=white: \
x=w*0.5-text_w/2: \
y=(h-text_h)/2+(768.0)-(352) " ./assets/tmp/bg/videos_text/05.mp4 \
')