# Add your utilities or helper functions to this file.

import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    TooManyRequests,
    VideoUnavailable
)
from youtube_transcript_api.formatters import WebVTTFormatter
from pytube import YouTube
import csv
from os import path as osp
from googleapiclient.discovery import build
import re

        
"""
#def get_video_id_from_url(video_url):
   
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    

    import urllib.parse
    url = urllib.parse.urlparse(video_url)
    if url.hostname == 'youtu.be':
        return url.path[1:]
    if url.hostname in ('www.youtube.com', 'youtube.com'):
        if url.path == '/watch':
            p = urllib.parse.parse_qs(url.query)
            return p['v'][0]
        if url.path[:7] == '/embed/':
            return url.path.split('/')[2]
        if url.path[:3] == '/v/':
            return url.path.split('/')[2]

    return video_url
"""


def get_video_transcript(video_id):
    """Récupère le transcript d'une vidéo YouTube avec gestion des erreurs."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-GB', 'en', 'fr'])
        return transcript  # Retourne la liste des sous-titres
    except TranscriptsDisabled:
        return "Erreur: Les sous-titres sont désactivés pour cette vidéo."
    except NoTranscriptFound:
        return "Erreur: Aucun sous-titre trouvé dans les langues demandées."
    except TooManyRequests:
        return "Erreur: Trop de requêtes envoyées. Réessayez plus tard."
    except VideoUnavailable:
        return "Erreur: La vidéo n'est pas accessible."
    except Exception as e:
        return f"Erreur inconnue: {str(e)}"
    
# if this has transcript then download
def get_transcript_vtt(video_url, path='/tmp'):
    """Récupère le transcript d'une vidéo YouTube et l'enregistre dans un fichier."""
    yt = YouTube(video_url)
    video_id=yt.video_id
    if not video_id:
        return "Erreur: URL YouTube invalide."
    
    filepath = os.path.join(path,'captions.vtt')
    if os.path.exists(filepath):
        return filepath

    transcript = get_video_transcript(video_id)
    # Vérifier si une erreur a été retournée
    if isinstance(transcript, str) and transcript.startswith("Erreur"):
        return transcript  # Retourne le message d'erreur
    
    formatter = WebVTTFormatter()
    webvtt_formatted = formatter.format_transcript(transcript)
    
    with open(filepath, 'w', encoding='utf-8') as webvtt_file:
        webvtt_file.write(webvtt_formatted)
    webvtt_file.close()

    return filepath
    
def check_and_add_url(url, filename="src/data/shared_data/urls.csv"):
    """
    - Lire le fichier CSV pour vérifier si l'URL existe déjà sinon il le crée
    - il retourne le nom du dossier
    """
    
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)  # Convertir en liste pour pouvoir la parcourir plusieurs fois
        for row in rows:
            if row['url'] == url:
                return row['folder_name']

    # Si l'URL n'existe pas, générer un nouveau nom (video1, video2, etc.)
    if rows:  # Si le fichier n'est pas vide
        last_name = rows[-1]['folder_name']  # Récupérer le dernier nom utilisé
        last_number = int(last_name.replace('video', ''))  # Extraire le numéro
        new_number = last_number + 1
    else:
        new_number = 1  # Si le fichier est vide, commencer à 1

    new_name_folder = f"video{new_number}"

    # Ajouter la nouvelle URL et le nom au fichier CSV
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['url', 'folder_name'])
        writer.writerow({'url': url, 'folder_name': new_name_folder})

    return new_name_folder

def check_existing_url(url, filename="src/data/shared_data/urls.csv"):
    """
    - Lire le fichier CSV pour vérifier si l'URL existe déjà 
    - il retourne le nom du dossier ou rien
    """
    
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)  # Convertir en liste pour pouvoir la parcourir plusieurs fois
        for row in rows:
            if row['url'] == url:
                return row['folder_name']

    return ""

def get_youtube_comments(video_id, api_key, folder_name,max_results=200):
    """
    - permet la récupération des commentaires
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    output_file = folder_name+"/comments.txt"
    comments = []

    # Récupérer les commentaires de premier niveau
    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        maxResults=100  # Limite API
    )

    while request and len(comments) < max_results:
        response = request.execute()

        for item in response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(top_comment)

            # Vérifier s'il y a des réponses et les récupérer
            if "replies" in item:
                for reply in item["replies"]["comments"]:
                    reply_text = reply["snippet"]["textDisplay"]
                    comments.append(reply_text)

            if len(comments) >= max_results:
                break  # Stop si on atteint la limite

        request = youtube.commentThreads().list_next(request, response)  # Pagination
         # Écrire les commentaires dans le fichier spécifié
        with open(output_file, "w", encoding="utf-8") as file:
            for comment in comments:
                file.write(comment + "\n")

    #return f"{len(comments)} commentaires enregistrés dans {output_file}"
    return f"{len(comments)} commentaires enregistrés."



def is_valid_youtube_url(url):
    """
    Vérifie si une URL est un lien YouTube valide.
    
    Args:
        url (str): L'URL à vérifier.

    Returns:
        bool: True si c'est un lien YouTube valide, sinon False.
    """
    youtube_regex = re.compile(
        r'^(https?://)?(www\.)?'
        r'(youtube\.com/watch\?v=|youtu\.be/)'
        r'([a-zA-Z0-9_-]{11})'
    )
    
    return bool(youtube_regex.match(url))

def extract_text_from_webvtt(file_path):
    """
    Extrait et concatène le texte d'un fichier WEBVTT en un texte continu.
    Args:
        file_path (str): chemin vers le fichier des transcriptions.
    Returns:
        texte : les transcriptions concaténées dans un seul texte.
    
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Filtrer les lignes contenant du texte, en ignorant les lignes de timestamp
        text_lines = []
        for line in lines:
            line = line.strip()
            if "-->" not in line and not line.startswith("WEBVTT") and line != "":
                text_lines.append(line)

        # Concaténer toutes les lignes de texte en une seule chaîne
        final_text = " ".join(text_lines)

        return final_text

    except FileNotFoundError:
        return "Le fichier spécifié est introuvable."
    except Exception as e:
        return f"Une erreur est survenue : {str(e)}"

