# 📺 YouTube Video & Comment Summarizer

Ce projet permet de **résumer automatiquement** les vidéos YouTube et leurs commentaires en utilisant un **LLM local** ou un **LLM propriétaire**.

![Demo](video.gif)

## 🚀 Installation & Exécution

### 1️⃣ Cloner le dépôt 

git clone https://github.com/Samadfilali/Youtube_Resume.git

cd Youtube_Resume

### 2️⃣ Créer un environnement virtuel

python -m venv venv

Sous Windows :
venv\Scripts\activate

Sous macOS/Linux :
source venv/bin/activate

### 3️⃣ Installer les dépendances
pip install -r requirements.txt

### 4️⃣ Configurer les clés API
Dans le fichier src/configs/.env, ajoutez vos clés API :

YOUTUBE_API_KEY=VOTRE_CLE_YOUTUBE   # Obligatoire

OPENAI_API_KEY=VOTRE_CLE_OPENAI     # Facultatif (si utilisation d'un LLM propriétaire)

### 📌 Comment obtenir une clé YouTube API ?
1. Rendez-vous sur la Google Cloud Console
2. Créez un projet ou utilisez un projet existant.
3. Activez l'API YouTube Data v3.
4. Générez une clé API et copiez-la dans le .env

### 5️⃣ Exécuter le script
python src/scripts/main.py

### ⚙️ Options d'exécution
- LLM en local : Si aucun OPENAI_API_KEY n'est fourni, un modèle local peut être utilisé avec ollama
- LLM propriétaire : Si OPENAI_API_KEY est défini, vous pouvez utiliser l'API OpenAI.
- Différences : Les temps de réponse et la qualité des résumés varient selon l'option choisie. Un modèle 7B local a donné des résultats satisfaisants.

## 📬 Contact & Contributions

N'hésitez pas à proposer des améliorations ou à ouvrir des issues ! 🚀
