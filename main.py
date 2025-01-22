import streamlit as st
import os
from downloadManager import VideoDownloader

class UI:
    def __init__(self):
        self.temp_folder = 'temp_video'
        os.makedirs(self.temp_folder, exist_ok=True)
    
    def url_input(self):
        video_url = st.text_input('📌 Digite a URL do vídeo do YouTube:')

        if video_url:
            st.write("🔍 Obtendo informações do vídeo...")

            downloader = VideoDownloader(video_url)
            info = downloader.get_video_info()

            if isinstance(info, dict):
                st.subheader('📄 Informações do vídeo')
                st.write(f'**📌 Título:** {info["title"]}')
                st.write(f'**👤 Autor:** {info["author"]}')
                st.write(f'**⏳ Duração:** {info["duration"]}')
                st.write(f'**👀 Visualizações:** {info["views"]:,}')

                formats = info['formats']
                
                valid_formats = [
                    f for f in formats if f['has_video'] and f['has_audio']
                ]

                if formats:
                    st.subheader('🎥 Formatos disponíveis (com vídeo + áudio)')
                    format_options = {
                        f"{f['format_id']} - {f['resolution']} ({f['extension']})": f["format_id"]
                        for f in formats
                    }
                    
                    for f in formats:
                        st.write(f"ID: {f['format_id']} | Resolução: {f['resolution']} | Extensão: {f['extension']} | 🎵 Áudio: {f['acodec']} | 🎥 Vídeo: {f['vcodec']}")
                    
                    format_choice = st.selectbox('🔽 Escolha o formato para download:', list(format_options.keys()))

                    if st.button('⬇️ Baixar Vídeo'):
                        st.write("🔄 Baixando vídeo...")

                        format_id = format_options[format_choice]
                        video_file = downloader.download_video(self.temp_folder)

                        if video_file:
                            # Exibe o botão de download após o vídeo ser baixado
                            with open(video_file, "rb") as f:
                                st.download_button(
                                    label="Clique aqui para baixar o vídeo",
                                    data=f,
                                    file_name=f"{info['title']}.mp4",
                                    mime="video/mp4"
                                )

                            # Remove o arquivo após o download
                            os.remove(video_file)
                            st.success("O arquivo foi baixado e apagado do servidor!")
                        else:
                            st.error("⚠️ Erro ao baixar o vídeo.")
                else:
                    st.warning('Nenhum formato disponível para este vídeo.')
            else:
                st.error(info)
    
    def run(self):
        st.title('Baixar vídeo do Youtube')
        self.url_input()

app = UI()
app.run()
