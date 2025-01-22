import yt_dlp
import os
import subprocess
import glob

class VideoDownloader:
    def __init__(self, url: str, format_choice: str = 'best'):
        self.url = url
        self.format_choice = format_choice
        self.ffmpeg_path = self.install_ffmpeg()  # Responsável por garantir que o FFmpeg esteja instalado
        self.ydl_opts = self.set_download_options()  # Configura as opções de download
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            return d['_percent_str'], d['_eta_str']
    
    # def is_ffmpeg_installed(self):
    #     try:
    #         subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    #         return True
    #     except FileNotFoundError:
    #         return False
    
    def install_ffmpeg(self):
        """Baixa e extrai o FFmpeg se não estiver instalado no diretório esperado."""
        ffmpeg_folder = "ffmpeg_bin"
        ffmpeg_exec = os.path.join(ffmpeg_folder, "ffmpeg")

        if not os.path.exists(ffmpeg_exec):
            os.makedirs(ffmpeg_folder, exist_ok=True)
            print("🔄 Baixando FFmpeg...")
            subprocess.run("wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz", shell=True)
            subprocess.run(f"tar -xf ffmpeg-release-amd64-static.tar.xz --strip-components 1 -C {ffmpeg_folder}", shell=True)
            print("✅ FFmpeg instalado!")
        
        return ffmpeg_exec  # Retorna o caminho para o executável do FFmpeg
    
    def set_download_options(self):
        """Configura as opções do yt-dlp para baixar o vídeo."""
        postprocessors = []

        # Se o formato escolhido não for MP4, adiciona o conversor
        if 'mp4' not in self.format_choice:
            postprocessors = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]

        return {
            'format': self.format_choice,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'ffmpeg_location': self.ffmpeg_path,  # Caminho para o FFmpeg
            'progress_hooks': [self.progress_hook],
            'postprocessors': postprocessors  # Adiciona o postprocessador apenas se necessário
        }
    
    def get_video_info(self):
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
                formats = info_dict.get('formats', [])
                
                resolutions_standard = ['144p', '240p', '360p', '480p', '720p', '720p60', '1080p', '1080p60']
                
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
        """Baixa o vídeo e retorna o caminho do arquivo baixado."""
        try:
            if not os.path.exists(download_path):
                os.makedirs(download_path)

            self.ydl_opts['outtmpl'] = os.path.join(download_path, '%(title)s.%(ext)s')

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                output_file = self.find_downloaded_file(download_path)
                
                if output_file:
                    return output_file  # Retorna o caminho do arquivo baixado
                else:
                    return "⚠️ Erro ao encontrar o arquivo baixado."

        except Exception as e:
            return f'Erro ao baixar o vídeo: {e}'
    
    def find_downloaded_file(self, download_path):
        """Procura o arquivo baixado na pasta e retorna o caminho."""
        files = glob.glob(os.path.join(download_path, "*.mp4"))
        return files[0] if files else None  # Retorna o primeiro arquivo encontrado ou None

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