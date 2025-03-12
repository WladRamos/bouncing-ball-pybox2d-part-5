import pygame
import cv2
import numpy as np
import subprocess
import os

from Game import Game
from utils import utils

# Configuração do Pygame
game = Game()

# Configuração do OpenCV para gravar vídeo
fps = 60  # Ajuste para a taxa de quadros desejada
video_filename_avi = "output.avi"
video_filename_mp4 = "output.mp4"
fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Codec de vídeo
out = cv2.VideoWriter(video_filename_avi, fourcc, fps, (utils.width, utils.height))

recording = True  # Alterne para False se não quiser gravar

while True:
    utils.screen.fill((23, 23, 23), (0, 0, utils.width, utils.height))
    utils.calDeltaTime()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            out.release()  # Libera o vídeo antes de sair
            pygame.quit()
            
            # Converte para MP4 após fechar o jogo
            print("🔄 Convertendo vídeo para MP4...")
            try:
                result = subprocess.run(
                    ["ffmpeg", "-i", video_filename_avi, "-vcodec", "libx264", "-crf", "23", video_filename_mp4],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                print(result.stdout)  # Exibe a saída do FFmpeg no terminal
                os.remove(video_filename_avi)  # Remove o AVI após a conversão
                print(f"✅ Vídeo salvo como {video_filename_mp4}")

            except subprocess.CalledProcessError as e:
                print(f"⚠️ Erro ao converter o vídeo: {e.stderr}")
                print("Certifique-se de que o FFmpeg está instalado e disponível no PATH.")

            exit(0)

    game.update()
    game.draw()

    # Captura o frame da tela do Pygame
    frame = pygame.surfarray.array3d(utils.screen)
    frame = np.rot90(frame)  # Corrige a rotação da imagem
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Converte para formato BGR do OpenCV

    # Grava o frame no vídeo
    if recording:
        out.write(frame)

    pygame.display.flip()

# Libera os recursos do OpenCV quando terminar
out.release()
pygame.quit()
