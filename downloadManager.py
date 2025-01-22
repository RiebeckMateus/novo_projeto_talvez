import yt_dlp
import os
import subprocess

class VideoDownloader:
    def __init__(self, url: str, format_choice: str = 'best'):
        self.url = url
        self.format_choice = format_choice
        
        self.ydl_opts = {
            'quiet': True,
            'format': self.format_choice,
            'noplaylist': True,
            'progress_hooks': [self.progress_hook],
        }
        
        self.ffmpeg_path = self.install_ffmpeg()
        if self.ffmpeg_path:
            self.ydl_opts['ffmpeg_location'] = self.ffmpeg_path
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            return d['_percent_str'], d['_eta_str']
    
    def is_ffmpeg_installed(self):
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except FileNotFoundError:
            return False
    
    def install_ffmpeg(self):
        """Baixa e instala FFmpeg automaticamente caso não esteja disponível."""
        if self.is_ffmpeg_installed():
            print("FFmpeg já está instalado.")
            return "ffmpeg"  # Retorna o comando padrão se já estiver no sistema
        
        print("Baixando FFmpeg...")

        # Baixar FFmpeg (somente para Linux)
        subprocess.run("wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz", shell=True)
        subprocess.run("tar -xf ffmpeg-release-amd64-static.tar.xz", shell=True)
        
        # Detectar a pasta extraída do FFmpeg
        for folder in os.listdir():
            if folder.startswith("ffmpeg"):
                ffmpeg_path = os.path.join(os.getcwd(), folder, "ffmpeg")
                os.environ["FFMPEG_PATH"] = ffmpeg_path
                print(f"FFmpeg instalado em: {ffmpeg_path}")
                return ffmpeg_path
        
        print("Erro: FFmpeg não pôde ser instalado.")
        return None
    
    def get_video_info(self):
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
                formats = info_dict.get('formats', [])
                
                # resolutions_standard = ['144p', '240p', '360p', '480p', '720p', '720p60', '1080p', '1080p60']
                
                available_formats = []
                
                for fmt in formats:
                    format_id = fmt.get('format_id', 'N/A')
                    resolution = fmt.get('format_note', 'Desconhecido')
                    ext = fmt.get('ext', 'N/A')
                    acodec = fmt.get('acodec', 'none')
                    vcodec = fmt.get('vcodec', 'none')
                    
                    has_audio = acodec != 'none'
                    has_video = acodec != 'none'
                
                    available_formats.append({
                        'format_id': format_id,
                        'resolution': resolution,
                        'extension': ext,
                        'has_audio': has_audio,
                        'has_video': has_video,
                        'acodec': acodec,
                        'vcodec': vcodec
                    })
                
                video_info = {
                    'title': info_dict.get('title', 'Título não encontrado'),
                    'author': info_dict.get('uploader', 'Autor não encontrado'),
                    'duration': info_dict.get('duration_string', 'Duração não encontrada'),
                    'views': info_dict.get('view_count', 'Visualizações não encontradas'),
                    'formats': available_formats
                }
                return video_info
        except Exception as e:
            return f'Erro ao obter informações {e}'
    
    def download_video(self, download_path: str):
        """Baixa o vídeo e mescla áudio e vídeo com FFmpeg."""
        try:
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            
            # Configuração para baixar vídeo + áudio e mesclar
            self.ydl_opts.update({
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }]
            })
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url])
                return 'Download concluído com sucesso!'
            
        except Exception as e:
            return f'Erro ao baixar o vídeo: {e}'

if __name__ == '__main__':
    downloader = VideoDownloader('https://youtu.be/-s48CzbSrQ0')
    
    info = downloader.get_video_info()
    
    if isinstance(info, dict):
        
        print('Informações do vídeo')
        for key, value in info.items():
            print(f'{key}: {value}')
    
    else:
        print(info)
    
    # result = downloader.download_video(os.getcwd())
    # print(result)