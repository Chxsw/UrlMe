import subprocess
import os

class LocalConverter:
    def mp4_to_mp3(self, input_file_path):
        """Toma un archivo local mp4 y genera un mp3 en la misma ruta mediante FFmpeg."""
        if not os.path.exists(input_file_path):
            print("El archivo de origen no existe.")
            return False

        base_name = os.path.splitext(input_file_path)[0]
        output_file_path = f"{base_name}.mp3"

        command = [
            'ffmpeg',
            '-i', input_file_path,
            '-q:a', '0',
            '-map', 'a',
            output_file_path
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Conversión exitosa: {output_file_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error en FFmpeg durante la conversión: {e}")
            return False
        except FileNotFoundError:
            print("Error: FFmpeg no está instalado o no está en el PATH del sistema.")
            return False