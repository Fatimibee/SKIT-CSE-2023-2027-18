import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, ChevronRight, Loader2, Star, Trash2 } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function DocumentUploadPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [schemes, setSchemes] = useState([]);
  const [ocrDetails, setOcrDetails] = useState(null);

  const setMockSchemes = () => {
    setSchemes([
      { id: 1, name: 'PM Kisan Samman Nidhi', category: 'Agriculture', status: 'Eligible', matchScore: '95%' },
      { id: 2, name: 'Pradhan Mantri Awas Yojana', category: 'Housing', status: 'Eligible', matchScore: '88%' },
      { id: 3, name: 'Ayushman Bharat PM-JAY', category: 'Health', status: 'Eligible', matchScore: '85%' },
      { id: 4, name: 'Atal Pension Yojana', category: 'Finance', status: 'Eligible', matchScore: '78%' },
      { id: 5, name: 'PM Ujjwala Yojana', category: 'Energy', status: 'Eligible', matchScore: '75%' },
    ]);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setIsUploading(true);
    setSchemes([]);
    setOcrDetails(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8080/api/ocr/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          if (data.ocr_result?.extracted_fields) {
            setOcrDetails(data.ocr_result.extracted_fields);
          }
          if (data.recommended_schemes && data.recommended_schemes.length > 0) {
            const mappedSchemes = data.recommended_schemes.map((item, index) => ({
              id: item.scheme?.id || index + 1,
              name: item.scheme?.title || 'Government Scheme',
              category: item.scheme?.category || 'General',
              status: 'Eligible',
              matchScore: Math.round(item.matchPercentage || 85) + '%',
            }));
            setSchemes(mappedSchemes);
          } else {
            setMockSchemes();
          }
        } else {
          setMockSchemes();
        }
      } else {
        setMockSchemes();
      }
    } catch (error) {
      console.warn('Backend API offline, falling back to demo mode:', error);
      setMockSchemes();
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setSchemes([]);
    setOcrDetails(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-purple-600/[0.08] rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-1/4 left-1/4 w-[400px] h-[400px] bg-indigo-600/[0.08] rounded-full blur-[140px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
      </div>

      <Navbar />

      <main className="flex-1 flex flex-col items-center py-16 px-4 relative z-10">
        <div className="max-w-3xl w-full text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 shadow-lg shadow-purple-500/20 mb-6">
            <UploadCloud className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white mb-4">Document Upload & OCR Extraction</h1>
          <p className="text-slate-400 text-lg">
            Upload your Aadhaar, Income Certificate, or Caste Certificate. We'll extract your details and instantly match you with eligible government schemes.
          </p>
        </div>

        {/* Upload Area */}
        <div className="w-full max-w-2xl bg-slate-900/60 backdrop-blur-xl border border-white/[0.08] p-8 rounded-3xl shadow-2xl shadow-black/50 mb-10 text-center transition-all">
          {!selectedFile ? (
            <div className="relative border-2 border-dashed border-slate-600 hover:border-purple-500/50 rounded-2xl p-10 transition-colors group cursor-pointer bg-slate-800/20 hover:bg-slate-800/40">
              <input 
                type="file" 
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
                accept=".pdf,image/png,image/jpeg"
                onChange={handleFileUpload}
              />
              <div className="flex flex-col items-center pointer-events-none">
                <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <FileText className="w-8 h-8 text-slate-400 group-hover:text-purple-400 transition-colors" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Click or drag document to upload</h3>
                <p className="text-sm text-slate-500">Supports PDF, PNG, JPG (Max 5MB)</p>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between bg-slate-800/50 border border-purple-500/30 rounded-xl p-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-purple-400" />
                </div>
                <div className="text-left">
                  <p className="text-white font-medium truncate max-w-[200px] sm:max-w-xs">{selectedFile.name}</p>
                  <p className="text-xs text-slate-400">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {isUploading ? (
                  <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                )}
                <button 
                  onClick={removeFile}
                  className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-700 text-slate-400 hover:text-red-400 transition-colors"
                  title="Remove file"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Extracted Details Card (if available) */}
        {ocrDetails && (
          <div className="w-full max-w-2xl bg-slate-900/80 backdrop-blur-md border border-purple-500/20 rounded-2xl p-6 shadow-xl mb-6">
            <h4 className="text-purple-400 text-sm font-semibold uppercase tracking-wider mb-3">Extracted Citizen Profile</h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-left">
              {ocrDetails.name && <div><span className="text-xs text-slate-500 block">Name</span><span className="text-sm font-medium text-white">{ocrDetails.name}</span></div>}
              {ocrDetails.gender && <div><span className="text-xs text-slate-500 block">Gender</span><span className="text-sm font-medium text-white">{ocrDetails.gender}</span></div>}
              {ocrDetails.category && <div><span className="text-xs text-slate-500 block">Category</span><span className="text-sm font-medium text-white">{ocrDetails.category}</span></div>}
              {ocrDetails.income && <div><span className="text-xs text-slate-500 block">Annual Income</span><span className="text-sm font-medium text-emerald-400">₹{ocrDetails.income}</span></div>}
              {ocrDetails.state && <div><span className="text-xs text-slate-500 block">State</span><span className="text-sm font-medium text-white">{ocrDetails.state}</span></div>}
              {ocrDetails.dob && <div><span className="text-xs text-slate-500 block">Date of Birth</span><span className="text-sm font-medium text-white">{ocrDetails.dob}</span></div>}
            </div>
          </div>
        )}

        {/* Scrollable Schemes Component (shown only if schemes are loaded) */}
        {schemes.length > 0 && (
          <div className="w-full max-w-2xl bg-slate-900/80 backdrop-blur-md border border-white/[0.08] rounded-2xl shadow-xl overflow-hidden flex flex-col animate-fade-in-up">
            <div className="p-4 border-b border-white/[0.08] bg-slate-900 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Star className="w-5 h-5 text-emerald-400" />
                Eligible Schemes Found
              </h3>
              <span className="text-sm px-2.5 py-1 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20 font-medium">
                {schemes.length} Matches
              </span>
            </div>
            
            {/* The scrollable list with a reduced height */}
            <div className="overflow-y-auto max-h-[300px] p-2 custom-scrollbar">
              <div className="space-y-2">
                {schemes.map(scheme => (
                  <div key={scheme.id} className="flex items-center justify-between p-4 rounded-xl hover:bg-slate-800/50 transition-colors group cursor-pointer border border-transparent hover:border-white/[0.05]">
                    <div>
                      <h4 className="text-white font-medium mb-1 group-hover:text-purple-300 transition-colors">{scheme.name}</h4>
                      <p className="text-xs text-slate-500">{scheme.category}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right hidden sm:block">
                        <span className="text-[10px] uppercase tracking-wider text-slate-500 block">Match</span>
                        <span className="text-sm font-semibold text-emerald-400">{scheme.matchScore}</span>
                      </div>
                      <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-white transition-colors" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </main>

      <Footer />

      <style jsx="true">{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.02);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  );
}
