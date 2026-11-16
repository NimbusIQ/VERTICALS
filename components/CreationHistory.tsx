/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import React from 'react';
import { ClockIcon, ArrowRightIcon, DocumentIcon, PhotoIcon } from '@heroicons/react/24/outline';

export interface Creation {
  id: string;
  name: string;
  html: string;
  originalImages?: string[]; // Array of Base64 data URLs
  timestamp: Date;
}

interface CreationHistoryProps {
  history: Creation[];
  onSelect: (creation: Creation) => void;
  onClearHistory: () => void;
}

export const CreationHistory: React.FC<CreationHistoryProps> = ({ history, onSelect, onClearHistory }) => {
  if (history.length === 0) return null;

  const handleClear = () => {
    if (window.confirm("Are you sure you want to clear your history? This action cannot be undone.")) {
      onClearHistory();
    }
  };

  return (
    <div className="w-full animate-in fade-in slide-in-from-bottom-8 duration-700">
      <div className="flex items-center space-x-3 mb-3 px-2">
        <ClockIcon className="w-4 h-4 text-zinc-500" />
        <h2 className="text-xs font-bold uppercase tracking-wider text-zinc-500">Archive</h2>
        <div className="h-px flex-1 bg-zinc-800"></div>
        <button 
            onClick={handleClear}
            className="text-[10px] font-bold uppercase tracking-wider text-zinc-600 hover:text-red-400 transition-colors"
        >
            Clear History
        </button>
      </div>
      
      {/* Horizontal Scroll Container for Compact Layout */}
      <div className="flex overflow-x-auto space-x-4 pb-2 px-2 scrollbar-hide">
        {history.map((item) => {
          const firstImage = item.originalImages?.[0];
          const isPdf = firstImage?.startsWith('data:application/pdf');
          const fileCount = item.originalImages?.length || 0;

          return (
            <button
              key={item.id}
              onClick={() => onSelect(item)}
              className="group flex-shrink-0 relative flex flex-col text-left w-44 h-28 bg-zinc-900/50 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-600 rounded-lg transition-all duration-200 overflow-hidden"
            >
              <div className="p-4 flex flex-col h-full">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex -space-x-2">
                    <div className="p-1.5 bg-zinc-800 rounded group-hover:bg-zinc-700 transition-colors border border-zinc-700/50">
                        {isPdf ? (
                            <DocumentIcon className="w-4 h-4 text-zinc-400" />
                        ) : firstImage ? (
                            <PhotoIcon className="w-4 h-4 text-zinc-400" />
                        ) : (
                            <DocumentIcon className="w-4 h-4 text-zinc-400" />
                        )}
                    </div>
                    {fileCount > 1 && (
                        <div className="px-1.5 py-0.5 bg-blue-600 rounded-full text-[8px] font-bold text-white border border-zinc-900 z-10 flex items-center">
                            +{fileCount - 1}
                        </div>
                    )}
                  </div>
                  <span className="text-[10px] font-mono text-zinc-600 group-hover:text-zinc-400">
                    {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                
                <div className="mt-auto">
                  <h3 className="text-sm font-medium text-zinc-300 group-hover:text-white truncate">
                    {item.name}
                  </h3>
                  <div className="flex items-center space-x-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-[10px] text-blue-400">Restore</span>
                    <ArrowRightIcon className="w-3 h-3 text-blue-400" />
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>
      <style>{`
        .scrollbar-hide::-webkit-scrollbar {
            display: none;
        }
        .scrollbar-hide {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
      `}</style>
    </div>
  );
};