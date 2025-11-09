import os
import json
import re
import httpx
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import PyPDF2 as pdf
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from typing import Optional
import io
import base64

# --- CONFIGURATION (inchangée) ---
load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Erreur de configuration de l'API Google: {e}")

# --- PROMPTS (Remplacez "..." par vos prompts réels) ---
SUMMARY_PROMPT_TEMPLATE = """
As a senior tech recruiter, analyze the following raw text from a candidate's {platform_name} profile.
Summarize the key technical skills, programming languages, and project themes you observe in a single, concise paragraph of no more than 4 sentences.
Focus on unique skills that demonstrate practical application.

Raw Profile Data:
---
{profile_text}
---
"""

FINAL_JSON_PROMPT = """
You are an expert career coach and talent analyst. Your task is to analyze the provided CV text AND the expert summaries from the candidate's online profiles to create a final, comprehensive skill profile.
Your goal is to be exhaustive and identify ALL relevant skills.

Your analysis must be structured, insightful, and presented in a specific JSON format. Follow these instructions precisely:

1.  **Professional Summary:** Create a powerful 2-3 sentence summary of the candidate's core strengths based on ALL information.
2.  **Skill Categorization:** For each category (`technical_skills`, `soft_skills`, `tools_and_technologies`), identify and list ALL relevant skills you can find. Do not omit any.
3.  **Skill Object:** For each skill, create an object with `skill`, `confidence`, and `evidence`.
4.  **Evidence Conciseness:** For the `evidence` field, you MUST be concise. Use short keywords or sentence fragments (e.g., 'CV: Anomaly Detection Project', 'GitHub: NLP repo', 'Portfolio: Data Viz Section') instead of full sentences. This is critical.
5.  **Output Format:** The final output MUST be a valid and COMPLETE JSON object that follows the exact structure shown in the example below. Do not nest the skill lists inside another key. Start your response directly with ```json.

**Required JSON Structure Example:**
```json
{
  "professional_summary": "A concise summary...",
  "technical_skills": [
    {"skill": "Python", "confidence": "High", "evidence": "CV: Data pipeline project"}
  ],
  "soft_skills": [
    {"skill": "Communication", "confidence": "Medium", "evidence": "CV: Presented to stakeholders"}
  ],
  "tools_and_technologies": [
    {"skill": "Docker", "confidence": "High", "evidence": "GitHub: Containerized app"}
  ]
}
```
"""

# --- FONCTIONS UTILES ASYNCHRONES (inchangées) ---
async def get_github_data(username):
    if not username: return ""
    try:
        api_url = f"https://api.github.com/users/{username}/repos"
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, timeout=10)
        response.raise_for_status()
        repos = response.json()
        return " ".join(f"{r['name']}. {r['description']}. Lang: {r['language']}." for r in repos if r.get("description"))
    except httpx.RequestError: return ""

async def get_huggingface_data(username):
    if not username: return ""
    try:
        url = f"https://huggingface.co/{username}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        return " ".join(tag.get_text(strip=True) for tag in soup.find_all("h3", class_="mb-1"))
    except httpx.RequestError: return ""

async def get_portfolio_data(url):
    if not url: return ""
    try:
        if not url.startswith(("http://", "https://")): url = "https://" + url
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]): tag.decompose()
        return soup.body.get_text(separator=" ", strip=True)
    except httpx.RequestError: return ""

# --- FONCTIONS SYNCHRONES ---
def summarize_external_data(profile_text, platform_name):
    if not profile_text: return ""
    prompt = SUMMARY_PROMPT_TEMPLATE.format(platform_name=platform_name, profile_text=profile_text)
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    return f"\n\n--- AI-Generated Summary for {platform_name} ---\n{response.text}"

def generate_skill_json(combined_text):
    # MODIFIÉ: Augmentation des max_output_tokens à la limite maximale pour éviter la troncature
    generation_config = genai.GenerationConfig(max_output_tokens=8192, temperature=0.1)
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content([FINAL_JSON_PROMPT, combined_text], generation_config=generation_config)
    return response.text

def extract_text_from_pdf(file_bytes):
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = pdf.PdfReader(pdf_file)
        return "".join(page.extract_text() for page in pdf_reader.pages)
    except Exception: return None

def create_word_cloud_base64(skill_data):
    tech_skills = skill_data.get("technical_skills", [])
    tools = skill_data.get("tools_and_technologies", [])
    all_skills = tech_skills + tools
    confidence_weights = {"High": 3, "Medium": 2, "Low": 1}
    frequencies = {s["skill"]: confidence_weights.get(s["confidence"], 1) for s in all_skills if "skill" in s}
    if not frequencies: return None
    wc = WordCloud(width=600, height=200, background_color=None, colormap="viridis", mode="RGBA").generate_from_frequencies(frequencies)
    img_buffer = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(img_buffer, format='png', transparent=True)
    plt.close()
    img_buffer.seek(0)
    return base64.b64encode(img_buffer.getvalue()).decode('utf-8')

# --- LE POINT D'ENTRÉE DE L'API ---
@app.post("/analyze/")
async def analyze_skills(
    cv_file: UploadFile = File(...),
    github_user: Optional[str] = Form(None),
    hf_user: Optional[str] = Form(None),
    portfolio_url: Optional[str] = Form(None),
):
    # ... (les étapes 1 et 2 sont inchangées)
    print("\n--- ✅ REQUÊTE REÇUE ---")
    if not cv_file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    print("--- 1. Extraction du texte du PDF... ---")
    cv_bytes = await cv_file.read()
    cv_text = await run_in_threadpool(extract_text_from_pdf, cv_bytes)
    if not cv_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
    print("--- ...Texte du PDF extrait. ---")
    print("--- 2a. Récupération des données GitHub... ---")
    github_raw_data = await get_github_data(github_user)
    print("--- ...Données GitHub récupérées. Appel à l'IA pour le résumé... ---")
    github_summary = await run_in_threadpool(summarize_external_data, github_raw_data, "GitHub")
    print("--- ...Résumé GitHub terminé. ---")
    print("--- 2b. Récupération des données Hugging Face... ---")
    hf_raw_data = await get_huggingface_data(hf_user)
    print("--- ...Données Hugging Face récupérées. Appel à l'IA pour le résumé... ---")
    hf_summary = await run_in_threadpool(summarize_external_data, hf_raw_data, "Hugging Face")
    print("--- ...Résumé Hugging Face terminé. ---")
    print("--- 2c. Récupération des données Portfolio... ---")
    portfolio_raw_data = await get_portfolio_data(portfolio_url)
    print("--- ...Données Portfolio récupérées. Appel à l'IA pour le résumé... ---")
    portfolio_summary = await run_in_threadpool(summarize_external_data, portfolio_raw_data, "Personal Website")
    print("--- ...Résumé Portfolio terminé. ---")
    print("--- 3. Appel final à l'IA pour la génération du JSON... (Cette étape peut être longue) ---")
    combined_text = cv_text + github_summary + hf_summary + portfolio_summary
    response_text = await run_in_threadpool(generate_skill_json, combined_text)
    print("--- ...Génération JSON terminée. ---")

    # MODIFIÉ: Le bloc try...except est maintenant plus robuste
    try:
        print("--- 4. Traitement de la réponse JSON... ---")
        
        # Étape 1: Utiliser une expression régulière pour extraire UNIQUEMENT le contenu JSON
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not match:
            # Si aucun JSON n'est trouvé, lever une erreur
            raise ValueError("No JSON object found in the AI response.")
            
        json_string = match.group(0)
        
        # Étape 2: Parser le JSON extrait
        skill_data = json.loads(json_string)
        print("--- ...JSON traité. ---")
        
        print("--- 5. Génération du nuage de mots... ---")
        wordcloud_b64 = await run_in_threadpool(create_word_cloud_base64, skill_data)
        skill_data['wordcloud_image'] = wordcloud_b64
        print("--- ...Nuage de mots généré. ---")

        print("--- ✅ RÉPONSE ENVOYÉE ---")
        return skill_data
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"--- ❌ ERREUR lors du traitement de la réponse : {e} ---")
        print(f"--- Réponse brute de l'IA : {response_text} ---")
        raise HTTPException(status_code=500, detail=f"Error processing AI response: {e}\nRaw response: {response_text}")

# --- Pour lancer le serveur (inchangé) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)