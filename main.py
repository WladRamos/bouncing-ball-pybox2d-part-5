import pygame
import cv2
import numpy as np
import subprocess
import os
import time
from Game import Game
from utils import utils

# Configuração do Pygame
game = Game()
pygame.mixer.init()  # Inicia o mixer para capturar o áudio do Pygame

# Configuração do OpenCV para gravar vídeo
fps = 40
video_filename_avi = "output.avi"
video_filename_mp4 = "output.mp4"
fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = cv2.VideoWriter(video_filename_avi, fourcc, fps, (utils.width, utils.height))

recording = True

# Configuração do áudio usando FFmpeg
audio_filename = "output_audio.wav"

# Definir comando do FFmpeg para capturar áudio do sistema corretamente
if os.name == "nt":  # Windows
    ffmpeg_command = [
        "ffmpeg", "-y", "-f", "dshow", "-i", "audio=Mixagem estéreo (Realtek High Definition Audio)", 
        "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", audio_filename
    ]
elif os.name == "posix":  # Linux/macOS
    ffmpeg_command = [
        "ffmpeg", "-y", "-f", "pulse", "-i", "default", 
        "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", audio_filename
    ]

# Iniciar a gravação de áudio em um subprocesso separado (novo grupo de processo)
if os.name == "nt":  # Windows
    audio_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
else:
    audio_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

while True:
    utils.screen.fill((23, 23, 23), (0, 0, utils.width, utils.height))
    utils.calDeltaTime()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            recording = False  # Para a gravação de áudio

            # Finaliza a gravação de áudio corretamente
            print("⏹️ Finalizando gravação de áudio...")

            # Se o FFmpeg ainda estiver rodando, mate o processo
            if os.name == "nt":  # Windows
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(audio_process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                audio_process.terminate()
                time.sleep(1)  # Aguarda um pouco para garantir que ele finalize
                if audio_process.poll() is None:  # Se ainda estiver rodando, encerra à força
                    audio_process.kill()
                audio_process.wait()  # Aguarda a finalização completa
            
            print(f"✅ Áudio salvo como {audio_filename}")

            # Libera o vídeo
            out.release()
            pygame.quit()
            
            # Converte o vídeo para MP4 sem juntar com o áudio
            print("🔄 Convertendo vídeo para MP4...")
            os.system(f"ffmpeg -y -i {video_filename_avi} -vcodec libx264 -crf 23 {video_filename_mp4}")
            print(f"✅ Vídeo salvo como {video_filename_mp4}")

            print("\n🎬 Os arquivos foram gerados separadamente:")
            print(f"📂 Vídeo: {video_filename_mp4}")
            print(f"📂 Áudio: {audio_filename}")
            print("🎵 Agora você pode combinar o áudio e o vídeo manualmente em um editor de vídeo.")

            exit(0)

    game.update()
    game.draw()

    # Captura o frame da tela do Pygame
    frame = pygame.surfarray.array3d(utils.screen)
    frame = np.rot90(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if recording:
        out.write(frame)

    pygame.display.flip()

out.release()
pygame.quit()
