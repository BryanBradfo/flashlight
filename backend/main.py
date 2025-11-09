import os
import json
import re
import asyncio
from typing import Optional

import google.generativeai as genai
import PyPDF2 as pdf
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# --- CONFIGURATION INITIALE ---
load_dotenv()

app = FastAPI(
    title="Flashlight API",
    description="API to analyze resumes and profiles to uncover hidden skills.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("The GOOGLE_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Critical error during Google API configuration: {e}")

# --- PROMPTS (inchangés) ---
SUMMARY_PROMPT_TEMPLATE = """
As a senior tech recruiter, analyze the following raw text from a candidate's {platform_name} profile.
Summarize the key technical skills, programming languages, and project themes you observe.
Be concise (maximum 3-4 sentences) and focus on unique skills that demonstrate practical application.

Raw Profile Data:
---
{profile_text}
---
"""

FINAL_JSON_PROMPT = """
You are an expert talent analyst and career coach. Your mission is to analyze the provided CV text AND the summaries from the candidate's online profiles to create a final, comprehensive skill profile.

Your analysis must be insightful, structured, and presented in a specific JSON format. Follow these instructions PRECISELY:

1.  **Professional Summary:** Write a powerful 2-3 sentence summary of the candidate's core strengths, based on ALL available information.
2.  **Filtering and Prioritization Rules (VERY IMPORTANT):**
    *   **Focus on Marketable Skills:** Prioritize skills frequently mentioned in job descriptions (e.g., Python, React, AWS, Docker, Project Management, SQL).
    *   **Ignore "Noise":** Exclude extremely niche, academic, or single-mention tools/libraries from very specific projects (e.g., 'scikit-maad', 'VGGish', 'PANNs'), UNLESS they are the core focus of a major project. The goal is to highlight core talents, not list every imported library.
    *   **Group where necessary:** If multiple small libraries serve the same purpose, prefer the higher-level skill (e.g., instead of listing 3 visualization libraries, list "Data Visualization" with high confidence).
3.  **Skill Object Structure:** For each skill, create an object with `skill`, `confidence` ('High', 'Medium', 'Low'), and `evidence`.
4.  **Concise Evidence:** For the `evidence` field, be very brief. Use keywords or sentence fragments (e.g., 'CV: Data pipeline project', 'GitHub: NLP repo', 'Portfolio: Data Viz section').
5.  **Output Format:** The final output MUST be a valid and COMPLETE JSON object that follows the structure in the example below. Provide no explanation or text before or after the JSON block. Start your response directly with ```json.

**Required JSON Structure Example:**
```json
{
  "professional_summary": "A concise summary of the candidate's strengths...",
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

# --- FONCTIONS HELPERS ASYNCHRONES ---

async def get_external_data(url: str, client: httpx.AsyncClient) -> str:
    """Récupère le contenu brut d'une URL de manière asynchrone, en suivant les redirections."""
    if not url:
        return ""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        # User-Agent est crucial pour des sites comme Instagram
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = await client.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except httpx.RequestError as e:
        print(f"Warning: Could not fetch data from {url}. Error: {e}")
        return ""

# NOUVEAU : Fonction spécifique pour extraire la bio Instagram
async def get_instagram_bio(username: str, client: httpx.AsyncClient) -> str:
    """Extrait la biographie d'un profil Instagram à partir des métadonnées de la page."""
    if not username:
        return ""
    try:
        url = f"https://www.instagram.com/{username}/"
        html_content = await get_external_data(url, client)
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, "lxml")
        # La bio est souvent dans la meta tag 'description'
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            # Nettoyer le contenu pour ne garder que la bio
            content = meta_tag["content"]
            # Le contenu est souvent "X Followers, Y Following, Z Posts - [LA BIO ICI] from [Nom] (@username)"
            # On cherche à extraire la partie bio
            parts = content.split(' - ')
            if len(parts) > 1:
                return parts.split('from').strip()
        return ""
    except Exception as e:
        print(f"Warning: Could not extract Instagram bio for {username}. Error: {e}")
        return ""

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    import io
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = pdf.PdfReader(pdf_file)
        return "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    except Exception as e:
        print(f"Error reading PDF: {e}")
        raise HTTPException(status_code=400, detail=f"Error reading PDF file: {e}")

async def call_gemini_api(prompt: str, content: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = await model.generate_content_async([prompt, content])
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise HTTPException(status_code=503, detail=f"Error communicating with the Gemini API: {e}")

def clean_and_parse_json(raw_text: str) -> dict:
    match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if match:
        json_string = match.group(1)
    else:
        json_string = raw_text

    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error. Raw AI Response:\n{raw_text}")
        raise HTTPException(
            status_code=500,
            detail=f"The AI response was not valid JSON. Error: {e}"
        )

# --- ENDPOINT PRINCIPAL DE L'API (MODIFIÉ) ---

@app.post("/analyze/")
async def analyze(
    cv_file: UploadFile = File(...),
    github_user: Optional[str] = Form(None),
    huggingface_user: Optional[str] = Form(None),
    portfolio_url: Optional[str] = Form(None),
    instagram_user: Optional[str] = Form(None), # NOUVEAU CHAMP
):
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Google API key is not configured on the server.")

    cv_content_bytes = await cv_file.read()
    cv_text = extract_text_from_pdf_bytes(cv_content_bytes)
    if not cv_text:
        raise HTTPException(status_code=400, detail="Could not extract text from the CV.")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = []
        if github_user:
            tasks.append(get_external_data(f"https://api.github.com/users/{github_user}/repos", client))
        if huggingface_user:
            tasks.append(get_external_data(f"https://huggingface.co/{huggingface_user}", client))
        if portfolio_url:
            tasks.append(get_external_data(portfolio_url, client))
        # NOUVEAU : Ajouter la tâche pour Instagram
        if instagram_user:
            tasks.append(get_instagram_bio(instagram_user, client))

        results = await asyncio.gather(*tasks, return_exceptions=True)

    external_data_map = {}
    if github_user:
        external_data_map["GitHub"] = results.pop(0) if results else ""
    if huggingface_user:
        external_data_map["Hugging Face"] = results.pop(0) if results else ""
    if portfolio_url:
        external_data_map["Personal Website"] = results.pop(0) if results else ""
    # NOUVEAU : Mapper le résultat d'Instagram
    if instagram_user:
        external_data_map["Instagram"] = results.pop(0) if results else ""

    summary_tasks = []
    for platform, data in external_data_map.items():
        if data and not isinstance(data, Exception):
            # Le nettoyage spécifique au portfolio est déjà géré dans la fonction get_external_data
            if platform == "Personal Website":
                soup = BeautifulSoup(data, "lxml")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                data = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
            
            prompt = SUMMARY_PROMPT_TEMPLATE.format(platform_name=platform, profile_text=data)
            summary_tasks.append(call_gemini_api(prompt, ""))

    summary_results = await asyncio.gather(*summary_tasks, return_exceptions=True)
    summaries = [s for s in summary_results if isinstance(s, str)]

    combined_text = cv_text + "\n\n--- External Profile Summaries ---\n" + "\n".join(summaries)
    
    final_response_text = await call_gemini_api(FINAL_JSON_PROMPT, combined_text)
    
    final_json = clean_and_parse_json(final_response_text)

    return final_json