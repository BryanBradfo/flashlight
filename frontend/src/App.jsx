import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';

// Import your showcase images
import cvWebp from './assets/cv.webp';
import githubWebp from './assets/github.webp';

import googleLogo from './assets/google.png';
import harvardLogo from './assets/harvard.png';
import lovableLogo from './assets/lovable.jpg';
import mitLogo from './assets/mit.png';
import openaiLogo from './assets/openai.png';
import sapLogo from './assets/sap.png';

// --- SVG Icons (no changes here) ---

const GithubIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-5 h-5 text-gray-400">
    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
  </svg>
);

const InstagramIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-gray-400" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <rect x="4" y="4" width="16" height="16" rx="4"></rect>
        <circle cx="12" cy="12" r="3"></circle>
        <line x1="16.5" y1="7.5" x2="16.5" y2="7.501"></line>
    </svg>
);

const HuggingFaceIcon = () => (<span className="text-lg">🤗</span>);

const WebsiteIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9 9 0 100-18 9 9 0 000 18z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.95 9A9.002 9.002 0 005.05 9M3.55 15a9.002 9.002 0 0017.9 0" />
    </svg>
);


const UploadIcon = () => (
  <svg className="w-10 h-10 mb-4 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2" />
  </svg>
);

const LargeSpinner = () => (
    <svg className="animate-spin h-16 w-16 text-cyan-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
);

const ProfileInput = ({ placeholder, value, onChange, icon }) => (
  <div className="relative">
    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
      {icon}
    </div>
    <input
      type="text"
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="block w-full bg-gray-700 border border-gray-600 rounded-md p-3 pl-10 focus:ring-2 focus:ring-cyan-accent focus:outline-none"
    />
  </div>
);

// --- NEW, LARGE FEATURE SHOWCASE COMPONENT ---
const FeatureShowcase = () => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 my-16">
    {/* Card 1: CV Analysis */}
    <div className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700 group transition-all duration-300 hover:border-cyan-accent hover:shadow-2xl hover:shadow-cyan-accent/10">
      <img src={cvWebp} alt="CV Document Analysis" className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-105" />
      <div className="p-8">
        <h3 className="text-3xl font-bold text-gray-100 mb-3">Deep CV Analysis</h3>
        <p className="text-gray-400 text-lg">Our AI goes beyond keywords, understanding the context of your projects and experiences directly from your PDF resume.</p>
      </div>
    </div>
    {/* Card 2: Public Profile Aggregation */}
    <div className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700 group transition-all duration-300 hover:border-cyan-accent hover:shadow-2xl hover:shadow-cyan-accent/10">
      <img src={githubWebp} alt="GitHub Profile Page" className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-105" />
      <div className="p-8">
        <h3 className="text-3xl font-bold text-gray-100 mb-3">Public Profile Aggregation</h3>
        <p className="text-gray-400 text-lg">Connect GitHub, Hugging Face, and personal websites to paint a complete picture of your capabilities.</p>
      </div>
    </div>
  </div>
);


const analysisSteps = [
  "Parsing your CV...",
  "Scraping public profiles...",
  "Generating summaries with AI...",
  "Compiling your final skill profile...",
];

const LoadingScreen = ({ step }) => {
  const progress = Math.round(((step + 1) / (analysisSteps.length + 1)) * 100);
  
  return (
    <motion.div
      key="loading-screen"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-gray-900/90 backdrop-blur-sm z-50 flex flex-col items-center justify-center text-center p-4"
    >
      <LargeSpinner />
      <AnimatePresence mode="wait">
        <motion.p
          key={step}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="text-2xl font-bold text-gray-200 mt-8"
        >
          {analysisSteps[step] || "Finalizing..."}
        </motion.p>
      </AnimatePresence>
      <div className="w-full max-w-md mt-4 bg-gray-700 rounded-full h-2.5">
        <motion.div
          className="bg-cyan-accent h-2.5 rounded-full"
          initial={{ width: '0%' }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
        />
      </div>
      <p className="text-cyan-accent font-mono text-lg mt-2">{progress}%</p>
    </motion.div>
  );
};

const SkillPill = ({ skill, confidence, evidence, index }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3, delay: index * 0.05 }}
    title={`Confidence: ${confidence}\nEvidence: ${evidence}`}
    className="flex items-center bg-gray-700 text-gray-200 text-sm font-medium px-3 py-1.5 rounded-full cursor-default transition-all duration-300 hover:bg-cyan-accent hover:text-gray-900"
  >
    {skill}
  </motion.div>
);

// --- NOUVEAU COMPOSANT POUR LES SPONSORS ---
const Sponsors = () => {
  const sponsorLogos = [
    { name: 'MIT', logo: mitLogo },
    { name: 'Harvard', logo: harvardLogo },
    { name: 'SAP', logo: sapLogo },
    { name: 'OpenAI', logo: openaiLogo },
    { name: 'Google', logo: googleLogo },
    { name: 'Lovable', logo: lovableLogo },
  ];

  return (
    <div className="text-center mt-24 pb-12">
      <h3 className="text-sm font-semibold text-gray-500 tracking-wider uppercase">
        TRUSTED BY LEADING INSTITUTIONS & COMPANIES
      </h3>
      <div className="mt-8 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-x-8 gap-y-12 items-center">
        {sponsorLogos.map((sponsor) => (
          <img
            key={sponsor.name}
            src={sponsor.logo}
            alt={sponsor.name}
            className="max-h-12 w-auto mx-auto transition-transform duration-300 hover:scale-110"
          />
        ))}
      </div>
    </div>
  );
};

// --- Main App Component ---
function App() {
  const [pdfFile, setPdfFile] = useState(null);
  const [githubUser, setGithubUser] = useState('');
  const [hfUser, setHfUser] = useState('');
  const [portfolioUrl, setPortfolioUrl] = useState('');
  const [instagramUser, setInstagramUser] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState(null);
  const [skillData, setSkillData] = useState(null);

  useEffect(() => {
    let interval;
    if (isLoading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep(prevStep => {
          if (prevStep >= analysisSteps.length - 1) {
            clearInterval(interval);
            return prevStep;
          }
          return prevStep + 1;
        });
      }, 1800);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const onDrop = useCallback(acceptedFiles => {
    const file = acceptedFiles[0]; 
    if (file && file.type === 'application/pdf') {
      setPdfFile(file);
      setError(null);
      setSkillData(null);
    } else {
      setError('Please upload a valid PDF file.');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!pdfFile) {
      setError('A CV in PDF format is required to start the analysis.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setSkillData(null);

    const formData = new FormData();
    formData.append('cv_file', pdfFile);
    if (githubUser) formData.append('github_user', githubUser);
    if (hfUser) formData.append('huggingface_user', hfUser);
    if (portfolioUrl) formData.append('portfolio_url', portfolioUrl);
    if (instagramUser) formData.append('instagram_user', instagramUser);

    try {
      const response = await axios.post('/api/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setSkillData(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'An unknown error occurred.';
      setError(`Analysis failed: ${errorMessage}`);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearForm = () => {
    setPdfFile(null);
    setGithubUser('');
    setHfUser('');
    setPortfolioUrl('');
    setInstagramUser('');
    setSkillData(null);
    setError(null);
  }

  return (
    <div className="bg-gray-900 min-h-screen text-gray-100 font-sans p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <AnimatePresence>
          {isLoading && <LoadingScreen step={loadingStep} />}
        </AnimatePresence>
        
        <header className="text-center my-12">
          <h1 className="text-5xl md:text-7xl font-bold mb-3">
            🔦 Flashlight
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto">
            Upload your CV, connect your profiles, and let our AI discover the skills you didn't even know you had.
          </p>
        </header>

        <AnimatePresence mode="wait">
          {!skillData ? (
            <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              
              {/* This is the new, large showcase */}
              <FeatureShowcase />

              <form onSubmit={handleSubmit} className="bg-gray-800 p-6 md:p-8 rounded-xl shadow-2xl border border-gray-700 mt-16">
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold text-cyan-accent">Start Your Analysis</h2>
                  <p className="text-gray-400">Provide your CV and any public profiles below.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {/* Left side: CV Upload */}
                  <div className="flex flex-col">
                    <h3 className="text-xl font-semibold mb-4">Step 1: Upload Your CV <span className="text-red-500">*</span></h3>
                    <div {...getRootProps()} className={`flex-grow flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-lg cursor-pointer transition-colors duration-300 ${isDragActive ? 'border-cyan-accent bg-gray-700' : 'border-gray-600 hover:border-cyan-hover bg-gray-800'}`}>
                      <input {...getInputProps()} />
                      <UploadIcon />
                      {pdfFile ? (
                        <p className="text-green-400 font-semibold">{pdfFile.name}</p>
                      ) : (
                        <p className="text-gray-400 text-center">{isDragActive ? "Drop the PDF here..." : "Drag 'n' drop your CV here, or click to select"}</p>
                      )}
                      <span className="text-xs text-gray-500 mt-2">PDF format required</span>
                    </div>
                  </div>

                  {/* Right side: Profiles */}
                  <div>
                    <h3 className="text-xl font-semibold mb-4">Step 2: Add Public Profiles <span className="text-gray-500">(Optional)</span></h3>
                    <div className="space-y-4">
                      <ProfileInput 
                        icon={<GithubIcon />}
                        value={githubUser} 
                        onChange={e => setGithubUser(e.target.value)} 
                        placeholder="GitHub Username" 
                      />
                      <ProfileInput 
                        icon={<InstagramIcon />}
                        value={instagramUser} 
                        onChange={e => setInstagramUser(e.target.value)} 
                        placeholder="Instagram Username" 
                      />
                      <ProfileInput 
                        icon={<HuggingFaceIcon />}
                        value={hfUser} 
                        onChange={e => setHfUser(e.target.value)} 
                        placeholder="Hugging Face Username" 
                      />
                      <ProfileInput 
                        icon={<WebsiteIcon />}
                        value={portfolioUrl} 
                        onChange={e => setPortfolioUrl(e.target.value)} 
                        placeholder="Personal Website URL" 
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-8 pt-6 border-t border-gray-700">
                  <button type="submit" disabled={!pdfFile || isLoading} className="w-full bg-cyan-accent text-gray-900 font-bold py-4 px-6 rounded-lg text-xl transition-all duration-300 hover:bg-cyan-hover disabled:bg-gray-600 disabled:cursor-not-allowed transform hover:scale-105">
                    Analyze My Skills
                  </button>
                </div>
              </form>
            </motion.div>
          ) : (
            <motion.div key="results" initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mt-12">
              <h2 className="text-4xl font-bold text-center mb-8">Your AI-Generated Skill Profile</h2>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 mb-8">
                <h3 className="text-xl font-semibold mb-3 text-cyan-accent">🚀 Professional Summary</h3>
                <blockquote className="text-gray-300 text-lg border-l-4 border-cyan-accent pl-4 italic">
                  {skillData.professional_summary}
                </blockquote>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                    <h3 className="text-xl font-semibold mb-4 text-cyan-accent">💻 Technical Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {skillData.technical_skills?.map((s, i) => <SkillPill key={i} {...s} index={i} />)}
                    </div>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                    <h3 className="text-xl font-semibold mb-4 text-cyan-accent">🛠️ Tools & Technologies</h3>
                    <div className="flex flex-wrap gap-2">
                      {skillData.tools_and_technologies?.map((s, i) => <SkillPill key={i} {...s} index={i} />)}
                    </div>
                  </div>
                  <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                    <h3 className="text-xl font-semibold mb-4 text-cyan-accent">🤝 Soft Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {skillData.soft_skills?.map((s, i) => <SkillPill key={i} {...s} index={i} />)}
                    </div>
                  </div>
              </div>
              <div className="text-center mt-12">
                <button onClick={clearForm} className="bg-gray-700 text-gray-200 font-bold py-2 px-6 rounded-lg transition-colors duration-300 hover:bg-gray-600">
                  Analyze Another Profile
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        {error && (
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mt-6 bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded-lg text-center" role="alert">
            {error}
          </motion.div>
        )}

        <Sponsors />
      </div>
    </div>
  );
}

export default App;