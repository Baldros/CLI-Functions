import yt_dlp
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional, List, Dict
import os
import sys
import argparse
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do .env na raiz (C:\Users\amori\Documents\CLI-Functions\.env)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

def get_youtube_service():
    if not YOUTUBE_API_KEY:
        print("Erro: YOUTUBE_API_KEY não encontrada no arquivo .env")
        sys.exit(1)
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def buscar_videos(query: str, max_results: int = 5):
    youtube = get_youtube_service()
    try:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results,
            order="relevance"
        )
        response = request.execute()
        
        if not response.get('items'):
            print(f"Nenhum vídeo encontrado para '{query}'")
            return
        
        for item in response['items']:
            video_id = item['id'].get('videoId')
            if not video_id: continue 
            
            titulo = item['snippet']['title']
            canal = item['snippet']['channelTitle']
            descricao = item['snippet']['description']
            descricao_truncada = (descricao[:100] + '...') if len(descricao) > 100 else descricao
            
            print(f"📹 {titulo}")
            print(f"   Canal: {canal}")
            print(f"   ID: {video_id}")
            print(f"   URL: https://youtube.com/watch?v={video_id}")
            print(f"   Descrição: {descricao_truncada}\n")
            
    except Exception as e:
        print(f"Erro ao buscar vídeos: {str(e)}")

def obter_detalhes(video_id: str):
    youtube = get_youtube_service()
    try:
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        )
        response = request.execute()
        
        if not response['items']:
            print("Vídeo não encontrado.")
            return
        
        video = response['items'][0]
        snippet = video['snippet']
        stats = video['statistics']
        
        print(f"📹 {snippet['title']}\n")
        print(f"👤 Canal: {snippet['channelTitle']}")
        print(f"📅 Publicado em: {snippet['publishedAt']}\n")
        print(f"📊 Estatísticas:")
        print(f"   • Views: {stats.get('viewCount', 'N/A')}")
        print(f"   • Likes: {stats.get('likeCount', 'N/A')}")
        print(f"   • Comentários: {stats.get('commentCount', 'N/A')}\n")
        print(f"📝 Descrição:\n{snippet['description']}\n")
        print(f"🔗 URL: https://youtube.com/watch?v={video_id}")
        
    except Exception as e:
        print(f"Erro ao obter detalhes: {str(e)}")

def obter_transcricao(video_id: str, idioma: str = "pt"):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_transcript([idioma])
        except:
            transcript = transcript_list.find_transcript(['en']).translate(idioma)
        
        texto_completo = [entry['text'] for entry in transcript.fetch()]
        transcricao = " ".join(texto_completo)
        
        print(f"📝 Transcrição ({idioma}):\n")
        print(transcricao)
        
    except Exception as e:
        print(f"Erro ao obter transcrição: {str(e)}")

def listar_comentarios(video_id: str, max_results: int = 10):
    youtube = get_youtube_service()
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            order="relevance"
        )
        response = request.execute()
        
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            autor = comment['authorDisplayName']
            texto = comment['textDisplay']
            likes = comment['likeCount']
            
            print(f"💬 {autor} ({likes} likes):")
            print(f"   {texto[:300]}...\n")
            
    except Exception as e:
        print(f"Erro ao listar comentários: {str(e)}")

def baixar_video(video_url: str, output_path: str = "./downloads", format_str: str = "best", is_audio: bool = False):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        # Ajusta o formato se for apenas áudio
        if is_audio:
            format_str = "bestaudio/best"
            
        ydl_opts = {
            'format': format_str,
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'quiet': False,
        }
        
        # Se for áudio, adiciona post-processors para converter (opcional, requer ffmpeg)
        if is_audio:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Iniciando download de {video_url} (Formato: {format_str})...")
            info = ydl.extract_info(video_url, download=True)
            titulo = info['title']
            print(f"✅ Download concluído com sucesso: {titulo}")
            
    except Exception as e:
        print(f"Erro ao baixar vídeo: {str(e)}")

def obter_info_canal(channel_id: str):
    youtube = get_youtube_service()
    try:
        request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        response = request.execute()
        
        if not response['items']:
            print("Canal não encontrado.")
            return
        
        canal = response['items'][0]
        snippet = canal['snippet']
        stats = canal['statistics']
        
        print(f"📺 {snippet['title']}\n")
        print(f"📊 Estatísticas:")
        print(f"   • Inscritos: {stats.get('subscriberCount', 'N/A')}")
        print(f"   • Vídeos: {stats.get('videoCount', 'N/A')}")
        print(f"   • Views totais: {stats.get('viewCount', 'N/A')}\n")
        print(f"📝 Descrição:\n{snippet['description']}")
        
    except Exception as e:
        print(f"Erro ao obter info do canal: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="YouTube CLI - Interface para interação com YouTube via terminal.")
    subparsers = parser.add_subparsers(dest="command", help="Comando a ser executado")

    # Subcomando 'search'
    search_parser = subparsers.add_parser("search", help="Busca vídeos por palavra-chave")
    search_parser.add_argument("query", help="Termo de busca")
    search_parser.add_argument("--max", type=int, default=5, help="Máximo de resultados (padrão 5)")

    # Subcomando 'details'
    details_parser = subparsers.add_parser("details", help="Obtém detalhes de um vídeo pelo ID")
    details_parser.add_argument("id", help="ID do vídeo")

    # Subcomando 'transcript'
    transcript_parser = subparsers.add_parser("transcript", help="Obtém transcrição de um vídeo")
    transcript_parser.add_argument("id", help="ID do vídeo")
    transcript_parser.add_argument("--lang", default="pt", help="Código do idioma (padrão 'pt')")

    # Subcomando 'comments'
    comments_parser = subparsers.add_parser("comments", help="Lista comentários relevantes")
    comments_parser.add_argument("id", help="ID do vídeo")
    comments_parser.add_argument("--max", type=int, default=10, help="Máximo de comentários")

    # Subcomando 'download'
    download_parser = subparsers.add_parser("download", help="Baixa um vídeo do YouTube")
    download_parser.add_argument("url", help="URL do vídeo")
    download_parser.add_argument("--out", default="./downloads", help="Pasta de destino")
    download_parser.add_argument("--audio", action="store_true", help="Baixa apenas o áudio (mp3)")
    download_parser.add_argument("--format", default="best", help="Especifica o formato do yt-dlp (ex: 'bestvideo[height<=720]+bestaudio/best')")

    # Subcomando 'channel'
    channel_parser = subparsers.add_parser("channel", help="Obtém informações de um canal")
    channel_parser.add_argument("id", help="ID do canal")

    args = parser.parse_args()

    if args.command == "search":
        buscar_videos(args.query, args.max)
    elif args.command == "details":
        obter_detalhes(args.id)
    elif args.command == "transcript":
        obter_transcricao(args.id, args.lang)
    elif args.command == "comments":
        listar_comentarios(args.id, args.max)
    elif args.command == "download":
        baixar_video(args.url, args.out, args.format, args.audio)
    elif args.command == "channel":
        obter_info_canal(args.id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
