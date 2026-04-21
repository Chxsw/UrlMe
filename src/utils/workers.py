from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp
import urllib.request
from core.downloader import UrlDownloader
from core.converter import LocalConverter

class InfoWorker(QThread):
    info_signal = pyqtSignal(dict, bytes, str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        ydl_opts = {
            'quiet': True, 
            'skip_download': True # No descarga el video, solo busca la metadata
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                thumb_url = info.get('thumbnail')
                image_data = b""
                if thumb_url:
                    req = urllib.request.Request(thumb_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response:
                        image_data = response.read()
                        
                self.info_signal.emit(info, image_data, "")
        except Exception as e:
            self.info_signal.emit({}, b"", f"Error al buscar el video: {str(e)}")


class DownloadWorker(QThread):
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, url, format_type):
        super().__init__()
        self.url = url
        self.format_type = format_type
        self.downloader = UrlDownloader()

    def run(self):
        if "Video" in self.format_type:
            success = self.downloader.download_video(self.url)
            mensaje = "¡Video descargado con éxito!" if success else "Error al descargar el video."
        else:
            success = self.downloader.download_audio(self.url)
            mensaje = "¡Audio descargado con éxito!" if success else "Error al descargar el audio."
        
        self.finished_signal.emit(success, mensaje)


class ConvertWorker(QThread):
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.converter = LocalConverter()

    def run(self):
        success = self.converter.mp4_to_mp3(self.file_path)
        mensaje = "¡Conversión completada!" if success else "Error en la conversión."
        self.finished_signal.emit(success, mensaje)