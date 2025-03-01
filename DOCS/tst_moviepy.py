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