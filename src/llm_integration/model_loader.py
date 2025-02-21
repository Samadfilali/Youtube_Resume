from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
import sys
from pathlib import Path

# Ajouter le chemin racine du projet au PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent.parent # Ajustez en fonction de votre structure
sys.path.insert(0, str(BASE_DIR))  # Insérer au début du PYTHONPATH
# Charger les variables d'environnement depuis configs/.env
env_path = BASE_DIR / "src" / "configs" / ".env"

load_dotenv(dotenv_path=env_path)
# Récupérer les clés API depuis les variables d'environnement
openai_api_key = os.environ.get("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = openai_api_key

# Variable globale pour stocker l'instance LLM
llm = ChatOllama(model="llama3.1:8b", temperature=0.0)  # Modèle par défaut
global_model_name = "llama3.1:8b"

def set_llm(model_name: str):
    """Met à jour la variable globale llm"""
    global llm, global_model_name
    if model_name == "llama3.1:8b":
        llm = ChatOllama(model="llama3.1:8b", temperature=0.0)
    else:
        llm = ChatOpenAI(model="gpt-4o-mini")
    global_model_name = model_name
    
def get_llm():
    """Retourne l'instance actuelle de llm"""
    return llm

def get_llm_name() :
    """Retourne le nom du modèle actuel"""
    return global_model_name