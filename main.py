import streamlit as st
import os
from downloadManager import VideoDownloader

class UI:
    def __init__(self):
        pass
    
    def url_input(self):
        video_url = st.text_input('URL do vídeo')
        
        if video_url:
            downloader = VideoDownloader(video_url, 'best')
            info = downloader.get_video_info()
            
            if isinstance(info, dict):
                st.subheader('Informações do vídeo')
                st.write(f'**Título:** {info["title"]}')
                st.write(f'**Autor:** {info["author"]}')
                st.write(f'**Duração:** {info["duration"]}')
                st.write(f'**Visualizações:** {info["views"]}')
                
                formats = info['formats']
                
                if formats:
                    format_choice = st.selectbox('Escolha o formato para download:', options=list(formats.keys()))
                    
                    temp_folder = 'temp_video'
                    os.makedirs(temp_folder, exist_ok=True)
                    
                    if st.button('Baixar Vídeo'):
                        format_id = formats[format_choice]
                        downloader = VideoDownloader(video_url, format_id)
                        result = downloader.download_video(temp_folder)

                        if result == 'sucesso':
                            video_file = os.path.join(temp_folder, f"{info['title']}.mp4")
                            
                            with open(video_file, "rb") as f:
                                st.download_button(
                                    label="Clique aqui para baixar o vídeo",
                                    data=f,
                                    file_name=f"{info['title']}.mp4",
                                    mime="video/mp4"
                                )

                            os.remove(video_file)
                            st.success("O arquivo foi baixado e apagado do servidor!")
                        else:
                            st.error(f"Erro ao baixar o vídeo: {result}")
                else:
                    st.warning('Nenhum formato disponível para este vídeo.')
            else:
                st.error(info)
    
    def run(self):
        st.title('Baixar vídeo do Youtube')
        self.url_input()

app = UI()
app.run()
