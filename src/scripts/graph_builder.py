from typing_extensions import TypedDict
from operator import add
from typing import Annotated
import sys
from pathlib import Path

# Ajouter le chemin racine du projet au PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from src.llm_integration.model_loader import get_llm
import src.configs as sc

class StateOverAll(TypedDict):
    Text_video: Annotated[str, add]
    Resume_text_video : Annotated[str, add]
    Comments : Annotated[str, add]
    Resume_comments : Annotated[str, add]
    Final_report : Annotated[str, add]
    
    
from langchain_core.messages import SystemMessage, HumanMessage
def summarize_text(state):
    print("---Node 1---")
    # First, we get any existing summary
    Text_video = state.get("Text_video", "")

    # Create our summarization prompt 
    if Text_video:
        # Structure des messages
        prompt_system= """
                Vous êtes un expert en synthèse de contenu. Votre tâche est de résumer ce texte. Concentrez-vous uniquement sur les idées principales, 
                les points récurrents, et les grandes lignes exprimées dans le texte. Produisez un résumé clair, 
                concis et bien structuré qui reflète les thématiques principales et les éléments essentiels du texte, 
                tout en évitant de répéter des informations ou de prendre en compte des détails personnels.
                """

        # Conversation
        messages = [
            SystemMessage(content=prompt_system),
            HumanMessage(content=f"Text :\n{Text_video}\n\nRésumé :")
        ]

        # Générer une réponse
        llm= get_llm()
        response = llm.invoke(messages)
        return {"Resume_text_video": str(response.content)} # en cas de API Groq
        #return {"Resume_text_video": str(response)}  # en cas de Ollama

    else :
        return {"Resume_text_video": ""}
    

def summarize_comments(state):
    print("---Node 2---")
    # First, we get any existing summary
    comments = state.get("Comments", "")

    # Create our summarization prompt 
    if comments:
        # Structure des messages
        prompt_system= """
                Vous êtes un expert en synthèse de contenu. Votre tâche est de résumer les commentaires fournis sans 
                prendre en compte les auteurs ou les identités associées. Concentrez-vous uniquement sur les idées principales, 
                les points récurrents, et les grandes lignes exprimées dans les commentaires. Produisez un résumé clair, 
                concis et bien structuré qui reflète les thématiques principales et les éléments essentiels du texte, 
                tout en évitant de répéter des informations ou de prendre en compte des détails personnels.
                """

        # Conversation
        messages = [
            SystemMessage(content=prompt_system),
            HumanMessage(content=f"Commentaires :\n{comments}\n\nRésumé :")
        ]

        # Générer une réponse
        llm=get_llm()
        response = llm.invoke(messages)
        return {"Resume_comments": str(response.content)} # en cas de API Groq
        #return {"Resume_comments": str(response)} # en cas de Ollama
    else :
        return {"Resume_comments": ""}

def generate_final_report(state):
    print("---Node 3---")
    return {"Final_report": state['Text_video'] + state['Comments']}


from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

# Build graph
builder = StateGraph(StateOverAll)
builder.add_node("summarize_text", summarize_text)
builder.add_node("summarize_comments", summarize_comments)
builder.add_node("generate_final_report", generate_final_report)

# Logic
builder.add_edge(START, "summarize_text")
builder.add_edge(START, "summarize_comments")
builder.add_edge("summarize_text", "generate_final_report")
builder.add_edge("summarize_comments", "generate_final_report")
builder.add_edge("generate_final_report", END)

# Add
graph = builder.compile()

# View
#display(Image(graph.get_graph().draw_mermaid_png()))

