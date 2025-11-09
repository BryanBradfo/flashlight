# 🔦 Flashlight - Uncover Your Hidden Skills

![Flashlight App Screenshot](frontend/src/assets/flashlight_img.png)

*Built for the Global AI Hackathon – SAP "SkillSense" Challenge*

Flashlight is an AI-powered application designed to revolutionize how we discover and validate skills. It moves beyond traditional resumes by aggregating data from multiple sources to build dynamic, evidence-based skill profiles, helping individuals answer the critical question: "What am I truly good at?
---

## 🚀 The Problem

The future of work is shifting from credentials to skills, yet individuals possess a wealth of capabilities that remain undocumented or underutilized. Skills acquired through projects, open-source contributions, and informal learning often go unnoticed. This leads to missed opportunities for individuals and friction in talent matching for employers.

## ✨ Our Solution

Flashlight tackles this by creating an intelligent system that ingests data from a user's CV, GitHub, personal portfolio, and other public profiles. It uses Large Language Models to extract both explicit and implicit skills, generating a structured, dynamic skill profile complete with confidence scores and evidence trails.

### Key Features
*   **Multi-Source Data Aggregation:** Ingests data from PDFs (CVs) and public URLs (GitHub, portfolios, etc.).
*   **AI-Powered Skill Extraction:** Uses Google's Gemini Pro to perform deep semantic analysis and identify technical skills, soft skills, and tools.
*   **Dynamic Skill Profiles:** Generates a structured JSON output with skills, confidence levels, and direct evidence.
*   **Asynchronous Processing:** Leverages a high-performance backend to fetch and analyze data from multiple sources concurrently for a fast user experience.
*   **Clean & Modern UI:** A simple, intuitive interface built with React for easy CV uploading and profile analysis.

## 🛠️ Tech Stack & Architecture

Flashlight is built with a modern, decoupled architecture. The React frontend communicates with a high-performance Python backend that orchestrates data collection and AI analysis.

| Component         | Technology                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| **Frontend**      | [React](https://reactjs.org/), [Vite](https://vitejs.dev/), [Axios](https://axios-http.com/), [Tailwind CSS](https://tailwindcss.com/)     |
| **Backend**       | [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/) |
| **AI Model**      | [Google Gemini 2.5 Flash](https://ai.google.dev/)                                                                 |
| **Data Processing** | [PyPDF2](https://pypi.org/project/PyPDF2/) (for CVs), [HTTPX](https://www.python-httpx.org/) & [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) (for web scraping) |

**Architecture Flow:**
`User UI (React)` ➔ `CV/URLs` ➔ `API (FastAPI)` ➔ `[PyPDF2, HTTPX]` ➔ `Gemini (Summarize)` ➔ `Gemini (Synthesize)` ➔ `JSON Response` ➔ `User UI (React)`

---

## ⚙️ Setup and Installation

To run this project locally, you will need Python 3.8+ and Node.js v18+ installed.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Flashlight.git
cd Flashlight
```

### 2. Backend Setup

The backend handles the core logic of file processing, web scraping, and AI analysis.

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Create a .env file for your API key
# Create a file named .env in the /backend directory and add your key:
echo "GOOGLE_API_KEY='YOUR_GOOGLE_API_KEY_HERE'" > .env

# Run the backend server
uvicorn main:app --reload
```
The backend server will now be running at `http://127.0.0.1:8000`.

### 3. Frontend Setup

The frontend is a React application that provides the user interface.

```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
The frontend will now be available at `http://localhost:5173`. Open this URL in your browser to use the application.

## Usage

1.  **Upload Your CV:** Drag and drop your resume in PDF format onto the upload area.
2.  **Add Your Profiles:** Fill in the optional fields with your GitHub username, portfolio URL, and any other relevant links.
3.  **Analyze:** Click the "Analyze" button to start the process.
4.  **View Your Profile:** Within seconds, your comprehensive skill profile will be displayed, showing your technical skills, soft skills, and tools, along with the evidence for each.

## 🔮 Future Work

This project was built in under 24 hours for a hackathon, but it has immense potential. Future enhancements could include:
*   **Skill-Gap Analysis:** Compare a user's generated profile against a job description to identify missing skills.
*   **Personalized Learning Recommendations:** Suggest courses or projects based on identified skill gaps.
*   **Expanded Data Sources:** Integrate with more platforms like Stack Overflow, Medium, or academic publication sites.
*   **Interactive Dashboard:** Allow users to filter, edit, and export their skill profiles.