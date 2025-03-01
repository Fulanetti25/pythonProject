from moviepy.editor import  AudioFileClip, ImageClip, VideoFileClip, CompositeVideoClip, clips_array, TextClip, ColorClip, concatenate_videoclips
import moviepy.config as mpy_config

mpy_config.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})  # Ajuste o caminho conforme sua instalação

video_1 = VideoFileClip(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\v1.mp4').subclip(0,15)
video_2 = VideoFileClip(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\v2.mp4').subclip(0,15)
video_inferior = VideoFileClip(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\v_inferior.mp4').subclip(15,30)
video_1 = video_1.set_fps(24)
video_2 = video_2.set_fps(24)
video_inferior = video_inferior.set_fps(24)

audio = AudioFileClip(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\a1.mp3').subclip(8,13)
duration_part = audio.duration / 3  # Divide em 3 partes

image = ImageClip(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\i1.png', duration = 10)

intro = TextClip('Intro:\nMeu cool no seu pinto!', color = 'white', fontsize=100, font='Arial', size=(1280, 720)).set_duration(audio.duration)
credito = TextClip('Creditos:\nClica no zino e \ntarimba o naique!', color = 'white', fontsize=100, font='Arial', size=(1280, 720)).set_duration(audio.duration)
color_0 = ColorClip(size=intro.size, color=(0, 255, 0), duration=duration_part).set_start(0).set_fps(24)
color_1 = ColorClip(size=intro.size, color=(0, 150, 150), duration=duration_part).set_start(duration_part).crossfadein(1).set_fps(24)
color_2 = ColorClip(size=intro.size, color=(0, 0, 255), duration=duration_part).set_start(2 * duration_part).crossfadein(1).set_fps(24)

compose_intro = CompositeVideoClip([color_2, color_1, intro]).set_fps(24)
compose_intro.audio = audio
compose_credito = CompositeVideoClip([color_2, color_1, credito]).set_fps(24)
compose_credito.audio = audio

# compose = CompositeVideoClip([video,image])
# compose = clips_array([[video_1],[video_inferior]])
# compose = CompositeVideoClip([video_1,color_2, color_1, text])
compose = concatenate_videoclips([video_1,video_2])


compose.preview()
# compose.write_videofile(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\resultado.mp4', fps=24)