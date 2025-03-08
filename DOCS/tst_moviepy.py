# necessario configurar o complemento FFMPEG, baixado externamente:
# Acesse o site oficial do FFmpeg: Visite https://ffmpeg.org/download.html.
# Selecione a versão adequada para o seu sistema operacional: O FFmpeg oferece pacotes pré-compilados para diferentes sistemas operacionais. Escolha aquele que corresponde ao seu sistema (Windows, macOS, Linux, etc.).
# Siga as instruções de instalação: Cada sistema operacional pode ter procedimentos específicos para instalação. Certifique-se de seguir as orientações fornecidas no site para garantir uma instalação correta.

import pygame #usado como complementar para facilitar o PREVIEW dos dados

# BASICÃO

from moviepy.editor import  AudioFileClip, ImageClip, VideoFileClip, CompositeVideoClip

video = VideoFileClip(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\v1.mp4').subclip(0,10)
# video.size
# video.duration
# video.fps
# video.iter_frames()
audio = AudioFileClip(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\a1.mp3').subclip(8,18)
# audio.fps
# audio.nchannels
image = ImageClip(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\i1.png', duration = 10)
# image.size
# image.duration
# image.img

compose = CompositeVideoClip([video,image])
compose.audio = audio

# compose.preview()
compose.write_videofile(r'C:\Users\paulo\Downloads\PROJETOS\Drumeibes\Always Somewhere\r1.mp4')














from moviepy.editor import  AudioFileClip, ImageClip, VideoFileClip, CompositeVideoClip, clips_array, TextClip, ColorClip, concatenate_videoclips, concatenate_audioclips
import moviepy.config as mpy_config


# CONFIGURACOES E GLOBAIS
mpy_config.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})  # Ajuste o caminho conforme sua instalação


# ENTRADA DE DADOS
    # IMAGENS
image = (
    ImageClip(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\i1.png', duration = 15)
    # .resize(.5)
)
    # VIDEOS
video_1 = (
    VideoFileClip(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\v1.mp4') # (1280, 720)
    .subclip(0,15)
    .resize(.5)
    # .fadein(5)
    # .rotate(0)
    # .speedx(10)
)
video_2 = (
    VideoFileClip(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\v2.mp4') # (1280, 720)
    .subclip(0,15)
    .resize(.5)
    # .fadeout(5)
)
video_inferior = (
    VideoFileClip(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\v_inferior.mp4') # (640, 360)
    .subclip(15,45)
)
    # AUDIOS
audio_intro = (
    AudioFileClip(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\a1.mp3')
    .subclip(8,18)
)
audio_credito = (
    AudioFileClip(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\a1.mp3')
    .subclip(38,48)
)
    # TEXTOS
texto_intro = (
    TextClip('Intro:\nSeu cool no meu pinto!', color = 'white', fontsize=50, font='Arial', size=(640, 720))
    .set_duration(10)
)
texto_credito = (
    TextClip('Creditos:\nClica no zino e \ntarimba o naique!', color = 'black', fontsize=50, font='Arial', size=(640, 720))
    .set_duration(10)
)


# PADRONIZAÇÃO DE FORMATOS
audio_v1 = video_1.audio
audio_v2 = video_2.audio
audio_videos = concatenate_audioclips([audio_v1, audio_v2])
audio_concatenado = concatenate_audioclips([audio_intro, audio_videos, audio_credito])
color_0 = ColorClip(size=texto_intro.size, color=(0, 255, 0), duration=3).set_start(0).set_fps(24)
color_1 = ColorClip(size=texto_intro.size, color=(0, 150, 150), duration=3).set_start(3).set_fps(24)
color_2 = ColorClip(size=texto_intro.size, color=(0, 0, 255), duration=3).set_start(6).set_fps(24)


# COMPOSIÇÕES DE FASES
compose_intro = CompositeVideoClip([color_2, color_1, color_0, texto_intro]).set_fps(24)
compose_credito = CompositeVideoClip([color_0, color_1, color_2, texto_credito]).set_fps(24)


# COMPOSIÇÕES FINAIS
compose1 = concatenate_videoclips([video_1,video_2])
compose2 = CompositeVideoClip([compose1,image])
compose3 = clips_array([[compose2],[video_inferior]])
compose4 = concatenate_videoclips([compose_intro,compose3])
compose5 = concatenate_videoclips([compose4,compose_credito])


# SAÍDA DE DADOS
compose5 = compose5.set_audio(audio_concatenado)
# Se não atribuir o audio ao final, ele dá erro de FPS no .preview() apenas, sei lá porque diabos
compose5.preview()
# compose5.write_videofile(r'C:\Users\paulo\Downloads\TEMP\DRUMEIBES\Always Somewhere\resultado.mp4', fps=24)