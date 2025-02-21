import logging



import gradio as gr
from pytube import YouTube
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
import sys
from pathlib import Path

# Ajouter le chemin racine du projet au PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from src.scripts.graph_builder import graph
from src.tools.utils import get_transcript_vtt, check_and_add_url, get_youtube_comments, is_valid_youtube_url, extract_text_from_webvtt, check_existing_url
from src.tools.utils_css import custom_css
from src.llm_integration.model_loader import set_llm, get_llm_name

env_path = BASE_DIR / "src" / "configs" / ".env"
LOG_FILE = BASE_DIR / "src" / "logs" / "app.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,  # DEBUG pour plus de détails
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("Application démarrée")

load_dotenv(dotenv_path=env_path)

youtube_api_key = os.environ.get("YOUTUBE_API_KEY")

def display_video(url):
    """Affiche la vidéo YouTube en occupant 100% de la largeur du conteneur"""
    if not url.strip():
        logging.warning("Tentative d'affichage avec une URL vide")
        return "<div style='width:100%; height:315px; background-color:#f0f0f0; display:flex; align-items:center; justify-content:center; color:#888;'>Aucune vidéo</div>"
    
    try:
        yt = YouTube(url)
        video_id = yt.video_id
        logging.info(f"Affichage de la vidéo avec ID : {video_id}")
        return f"""
            <div style="width:100%; height:315px; background-color:#f0f0f0; display:flex; align-items:center; justify-content:center;">
                <iframe style="width:100%; height:100%;" 
                        src="https://www.youtube.com/embed/{video_id}" 
                        frameborder="0" allowfullscreen>
                </iframe>
            </div>
        """
    except Exception as e:
        logging.error(f"Erreur lors de l'affichage de la vidéo : {e}")
        return f"<p style='color:red;'>Erreur : {str(e)}</p>"
    
    
def get_video_summary(url):
    """Génère un résumé de la vidéo YouTube"""
    logging.info(f"Tentative de résumé pour l'URL : {url}")
    folder_name = check_existing_url(url)
    model_name = get_llm_name()

    if folder_name:
        path_folder = f"src/data/shared_data/videos/{folder_name}"
        resume_transcription_file = os.path.join(path_folder, f"resume_transcription_{model_name}.txt")
        resume_comments_file = os.path.join(path_folder, f"resume_comments_{model_name}.txt")

        if os.path.exists(resume_transcription_file) and os.path.exists(resume_comments_file):
            logging.info(f"Résumé déjà disponible pour {url}")
            with open(resume_transcription_file, "r", encoding="utf-8") as file:
                resume_transcription = file.read()
            with open(resume_comments_file, "r", encoding="utf-8") as file:
                resume_comments = file.read()
            return resume_transcription, resume_comments
        else:
            logging.info(f"Traitement du résumé en cours pour {url}")
            transcription_file = os.path.join(path_folder, "captions.vtt")
            comments_file = os.path.join(path_folder, "comments.txt")
            Text_video = extract_text_from_webvtt(transcription_file)
            Text_comments = extract_text_from_webvtt(comments_file)

            try:
                result = graph.invoke({"Text_video": Text_video, "Comments": Text_comments})
                with open(resume_transcription_file, "w", encoding="utf-8") as txt_file:
                    txt_file.write(result["Resume_text_video"])
                with open(resume_comments_file, "w", encoding="utf-8") as txt_file:
                    txt_file.write(result["Resume_comments"])
                logging.info("Résumé généré avec succès")
                return result["Resume_text_video"], result["Resume_comments"]
            except Exception as e:
                logging.error(f"Erreur lors du résumé de la vidéo : {e}")
                return "Erreur lors du résumé de la vidéo", ""
    else:
        logging.warning(f"Processing non effectué pour {url}")
        return "Lancez d'abord le processing de la vidéo !!!", ""

    
def processing_video(url):
    """ Charge la transcription et les commentaires"""
    if is_valid_youtube_url(url):
        logging.info(f"Début du processing pour {url}")
        folder_name = check_and_add_url(url)
        folder_path = f"src/data/shared_data/videos/{folder_name}"

        if os.path.exists(folder_path):
            logging.info(f"Vidéo {url} déjà traitée")
            return "Vidéo déjà traitée !!!"
        else:
            os.makedirs(folder_path)
            try:
                r = get_transcript_vtt(video_url=url, path=folder_path)
                if isinstance(r, str) and r.startswith("Erreur"):
                    logging.error(f"Erreur lors de la transcription : {r}")
                    return r
                yt = YouTube(url)
                VIDEO_ID = yt.video_id
                result = get_youtube_comments(VIDEO_ID, youtube_api_key, folder_path)
                logging.info(f"Processing terminé avec succès pour {url}")
                return f"✅ Transcription de la vidéo effectuée et {result}"
            except Exception as e:
                logging.error(f"Erreur lors du processing de la vidéo : {e}")
                return f"Erreur : {str(e)}"
    else:
        logging.warning(f"URL invalide : {url}")
        return "URL invalide !"
    
def fonction_selection_modeles(valeur):
    set_llm(valeur)  # Mise à jour du modèle
    return f"Vous avez sélectionné : {valeur}"

if not youtube_api_key:
    raise ValueError("La clé API YouTube est manquante. Vérifiez votre fichier .env.")

# Interface Gradio
with gr.Blocks(css=custom_css) as app:

    gr.Markdown("## 🎥 Résumez votre Vidéo YouTube")
    with gr.Row() :
        with gr.Column(scale=1) :
            models_selection = gr.Dropdown(
                                choices=["llama3.1:8b", "gpt-4o-mini"], 
                                label="Sélectionnez un modèle", 
                                value="llama3.1:8b"
                            )
                # Afficher le résultat de la sélection
            sortie_model = gr.Markdown("Modèle sélectionné : llama3.1:8b")
            # Interagir avec la sélection
            models_selection.change(fonction_selection_modeles, models_selection, sortie_model)
            url_input = gr.Textbox(label="Entrez l'URL YouTube", placeholder="https://www.youtube.com/watch?v=...")
            processing_video_btn = gr.Button("Processing", elem_classes="custom-button")  # Appliquer la classe CSS
            processing_output = gr.Textbox(label="Traitement", interactive=False)

            
        with gr.Column(scale=2):
            video_display = gr.HTML(value=display_video(""), label="Vidéo YouTube")  # Affiche un cadre vide au début
            #video_display = gr.HTML("<iframe class='video-frame' width='100%' height='265' src='' frameborder='0' allowfullscreen></iframe>")
            summarize_video_btn = gr.Button("Résumer la video et les commentaires", elem_classes="custom-button")  # Appliquer la classe CSS      
             
            
    with gr.Tabs():
        with gr.TabItem("Résumé de la Vidéo"):
            summary_video_output = gr.Textbox(label="Résumé de la vidéo", interactive=False, lines=15)
        with gr.TabItem("Résumé des Commentaires"):
            summary_comments_output = gr.Textbox(label="Résumé des commentaires", interactive=False, lines=15)
    
    # Déclenche l'affichage de la vidéo dès qu'on appuie sur Entrée
    url_input.change(display_video, inputs=[url_input], outputs=[video_display])

    # Déclenche le résumé après un clic sur le bouton
    summarize_video_btn.click(get_video_summary, inputs=[url_input], outputs=[summary_video_output,summary_comments_output])
    
    
    processing_video_btn.click(processing_video, inputs=[url_input], outputs=[processing_output])

app.launch()
