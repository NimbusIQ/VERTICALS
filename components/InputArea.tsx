/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import React, { useCallback, useState, useEffect } from 'react';
import { ArrowUpTrayIcon, SparklesIcon, CpuChipIcon } from '@heroicons/react/24/outline';

interface InputAreaProps {
  onGenerate: (prompt: string, files: File[]) => void;
  isGenerating: boolean;
  disabled?: boolean;
}

const CyclingText = () => {
    const words = [
        "a CRM architecture",
        "messy CSV data",
        "infrastructure diagrams",
        "a roofing contract",
        "a custom integration",
        "a set of complex PDFs",
        "high-res blueprints",
        "a lead generation dashboard"
    ];
    const [index, setIndex] = useState(0);
    const [fade, setFade] = useState(true);

    useEffect(() => {
        const interval = setInterval(() => {
            setFade(false); // fade out
            setTimeout(() => {
                setIndex(prev => (prev + 1) % words.length);
                setFade(true); // fade in
            }, 500); // Wait for fade out
        }, 3000); // Slower cycle to read longer text
        return () => clearInterval(interval);
    }, [words.length]);

    return (
        <span className={`inline-block whitespace-nowrap transition-all duration-500 transform ${fade ? 'opacity-100 translate-y-0 blur-0' : 'opacity-0 translate-y-2 blur-sm'} text-white font-medium pb-1 border-b-2 border-blue-500/50`}>
            {words[index]}
        </span>
    );
};

export const InputArea: React.FC<InputAreaProps> = ({ onGenerate, isGenerating, disabled = false }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  const handleFiles = (newFiles: FileList | File[]) => {
    const validTypes = ['image/', 'application/pdf', 'text/plain', 'text/csv', 'application/json', 'text/markdown'];
    const validFiles = Array.from(newFiles).filter(file => 
      validTypes.some(type => file.type.startsWith(type)) || 
      file.name.endsWith('.txt') || file.name.endsWith('.csv') || file.name.endsWith('.md') || file.name.endsWith('.json')
    );
    
    if (validFiles.length > 0) {
      setFiles(prev => [...prev, ...validFiles]);
    } else if (newFiles.length > 0) {
      alert("Please upload images, PDFs, or data files (CSV, TXT, JSON).");
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
        handleFiles(e.target.files);
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (isGenerating || disabled) return;
    if (prompt.trim() || files.length > 0) {
        onGenerate(prompt, files);
    } else {
        alert("Please provide a prompt or a file.");
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleDrop = useCallback((e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled || isGenerating) return;
    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  }, [disabled, isGenerating]);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    if (!disabled && !isGenerating) {
        setIsDragging(true);
    }
  }, [disabled, isGenerating]);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  return (
    <div className="w-full max-w-4xl mx-auto perspective-1000">
      <div 
        className={`relative group transition-all duration-300 ${isDragging ? 'scale-[1.01]' : ''}`}
      >
        <label
          className={`
            relative flex flex-col items-center justify-center
            h-56 sm:h-64 md:h-[22rem]
            bg-zinc-900/30 
            backdrop-blur-sm
            rounded-xl border border-dashed
            cursor-pointer overflow-hidden
            transition-all duration-300
            ${isDragging 
              ? 'border-blue-500 bg-zinc-900/50 shadow-[inset_0_0_20px_rgba(59,130,246,0.1)]' 
              : 'border-zinc-700 hover:border-zinc-500 hover:bg-zinc-900/40'
            }
            ${isGenerating ? 'pointer-events-none' : ''}
          `}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
            {/* Technical Grid Background */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none" 
                 style={{backgroundImage: 'linear-gradient(#ffffff 1px, transparent 1px), linear-gradient(90deg, #ffffff 1px, transparent 1px)', backgroundSize: '32px 32px'}}>
            </div>
            
            {/* Corner Brackets for technical feel */}
            <div className={`absolute top-4 left-4 w-4 h-4 border-l-2 border-t-2 transition-colors duration-300 ${isDragging ? 'border-blue-500' : 'border-zinc-600'}`}></div>
            <div className={`absolute top-4 right-4 w-4 h-4 border-r-2 border-t-2 transition-colors duration-300 ${isDragging ? 'border-blue-500' : 'border-zinc-600'}`}></div>
            <div className={`absolute bottom-4 left-4 w-4 h-4 border-l-2 border-b-2 transition-colors duration-300 ${isDragging ? 'border-blue-500' : 'border-zinc-600'}`}></div>
            <div className={`absolute bottom-4 right-4 w-4 h-4 border-r-2 border-b-2 transition-colors duration-300 ${isDragging ? 'border-blue-500' : 'border-zinc-600'}`}></div>

            <div className="relative z-10 flex flex-col items-center text-center space-y-4 md:space-y-6 p-6 md:p-8 w-full">
                <div className={`relative w-16 h-16 md:w-20 md:h-20 rounded-2xl flex items-center justify-center transition-transform duration-500 ${isDragging ? 'scale-110' : 'group-hover:-translate-y-1'}`}>
                    <div className={`absolute inset-0 rounded-2xl bg-zinc-800 border border-zinc-700 shadow-xl flex items-center justify-center ${isGenerating ? 'animate-pulse' : ''}`}>
                        {isGenerating ? (
                            <CpuChipIcon className="w-8 h-8 md:w-10 md:h-10 text-blue-400 animate-spin-slow" />
                        ) : (
                            <ArrowUpTrayIcon className={`w-8 h-8 md:w-10 md:h-10 text-zinc-300 transition-all duration-300 ${isDragging ? '-translate-y-1 text-blue-400' : ''}`} />
                        )}
                    </div>
                </div>

                <div className="space-y-1 md:space-y-2 w-full max-w-2xl">
                    <h3 className="flex items-center justify-center text-xl sm:text-2xl md:text-3xl text-zinc-100 leading-none font-bold tracking-tighter gap-3">
                        <span>Deploy</span>
                        <div className="h-10 flex items-center justify-center">
                           <CyclingText />
                        </div>
                        <span>instantly</span>
                    </h3>
                </div>

                {/* File List / Preview */}
                {files.length > 0 && (
                    <div className="flex flex-wrap justify-center gap-2 max-w-xl w-full">
                        {files.map((file, idx) => (
                            <div key={idx} className="group/file relative flex items-center gap-2 px-3 py-1.5 bg-zinc-800/80 rounded-lg border border-zinc-700 text-xs text-zinc-300">
                                <span className="max-w-[120px] truncate">{file.name}</span>
                                <button 
                                    onClick={(e) => { e.preventDefault(); e.stopPropagation(); removeFile(idx); }}
                                    className="opacity-0 group-hover/file:opacity-100 transition-opacity p-0.5 hover:bg-zinc-700 rounded text-zinc-500 hover:text-white"
                                >
                                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Prompt TextArea */}
                <div 
                    onClick={(e) => e.stopPropagation()} 
                    className="w-full max-w-xl relative group/input"
                >
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe your idea or what the files represent..."
                        className="w-full bg-zinc-950/50 border border-zinc-800 focus:border-blue-500/50 rounded-xl px-4 py-3 text-sm md:text-base text-zinc-100 placeholder:text-zinc-600 focus:outline-none transition-all duration-300 min-h-[80px] md:min-h-[100px] resize-none pr-12 shadow-2xl"
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit();
                            }
                        }}
                    />
                    <button
                        onClick={handleSubmit}
                        disabled={isGenerating || (!prompt.trim() && files.length === 0)}
                        className={`absolute bottom-3 right-3 p-2 rounded-lg transition-all duration-300 ${isGenerating ? 'bg-zinc-800 text-zinc-600' : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20'}`}
                    >
                        <SparklesIcon className={`w-5 h-5 ${isGenerating ? 'animate-pulse' : ''}`} />
                    </button>
                </div>

                <p className="text-zinc-600 text-[10px] md:text-xs font-light tracking-wide">
                    Drag & Drop or <span className="text-zinc-400 font-medium">Click</span> to add multiple files (Images, PDFs)
                </p>
            </div>

            <input
                type="file"
                accept="image/*,application/pdf,text/*,application/json"
                className="hidden"
                multiple
                onChange={handleFileChange}
                disabled={isGenerating || disabled}
            />
        </label>
      </div>
    </div>
  );
};
