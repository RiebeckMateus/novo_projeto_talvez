import yt_dlp
import os

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
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            return d['_percent_str'], d['_eta_str']
    
    def get_video_info(self):
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
                formats = info_dict.get('formats', [])
                
                resolutions_standard = ['144p', '240p', '360p', '480p', '720p', '720p60', '1080p', '1080p60']
                
                mp4_formats = {}
                resolution_formats = {}

                for fmt in formats:
                    if fmt.get('ext') == 'mp4':
                        if fmt.get('format_note'):
                            mp4_formats[fmt['format_note']] = fmt['format_id']
                        else:
                            mp4_formats["Qualidade desconhecida"] = fmt['format_id']
                    
                    if fmt.get('format_note') in resolutions_standard:
                        resolution_formats[fmt['format_note']] = fmt['format_id']
                
                sorted_formats = {}
                for res in resolutions_standard:
                    if res in mp4_formats:
                        sorted_formats[res] = mp4_formats[res]
                    elif res in resolution_formats:
                        sorted_formats[res] = resolution_formats[res]
                
                video_info = {
                    'title': info_dict.get('title', 'Título não encontrado'),
                    'author': info_dict.get('uploader', 'Autor não encontrado'),
                    'duration': info_dict.get('duration_string', 'Duração não encontrada'),
                    'views': info_dict.get('view_count', 'Visualizações não encontradas'),
                    'formats': sorted_formats
                }
                return video_info
        except Exception as e:
            return f'Erro ao obter informações {e}'
    
    def download_video(self, download_path: str):
        try:
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            
            self.ydl_opts['outtmpl'] = os.path.join(download_path, '%(title)s.%(ext)s')
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url])
                return 'sucesso'
            
        except Exception as e:
            return f'Erro ao baixar o vídeo'

if __name__ == '__main__':
    downloader = VideoDownloader('https://youtu.be/e_Xp57NgHXU')
    
    info = downloader.get_video_info()
    
    if isinstance(info, dict):
        
        print('Informações do vídeo')
        for key, value in info.items():
            print(f'{key}: {value}')
    
    else:
        print(info)
    
    result = downloader.download_video(os.getcwd())
    print(result)