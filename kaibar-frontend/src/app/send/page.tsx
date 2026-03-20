"use client";

import { Send as SendIcon, ChevronRight } from "lucide-react";

export default function SendPage() {
  return (
    <main className="p-4 pt-12 pb-24 flex flex-col items-center justify-start min-h-[80vh]">
      
      <div className="w-full max-w-sm bg-[#1C1C1E] border border-white/5 rounded-2xl shadow-2xl relative overflow-hidden">
        
        {/* Header */}
        <div className="flex justify-between items-center p-5 border-b border-white/5">
          <div className="flex items-center gap-2 text-white">
            <div className="text-orange"><SendIcon size={16} /></div>
            <h2 className="text-sm font-bold tracking-wider">Send</h2>
          </div>
          <button className="text-white/40 hover:text-white transition-colors">
            ✕
          </button>
        </div>

        <div className="p-5">
            {/* Connected Wallet Pill */}
            <div className="bg-[#121212] border border-white/5 rounded-xl p-3 flex justify-between items-center mb-6 cursor-pointer hover:border-white/10 transition-colors">
                <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-md bg-orange/20 border border-orange/30 flex items-center justify-center">
                    <span className="text-[10px]">🦊</span>
                    </div>
                    <span className="text-sm font-medium">drekahshi</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-xs text-white/50">0.00 SDA</span>
                    <span className="text-[10px] text-white/30">▼</span>
                </div>
            </div>

            {/* Steps Tracker */}
            <div className="flex items-center justify-center gap-2 text-[10px] font-bold tracking-wider mb-6">
                <span className="text-orange flex items-center gap-1">
                    <span className="w-4 h-4 rounded-full bg-orange/20 flex items-center justify-center">1</span> 
                    Recipient
                </span>
                <span className="text-white/20">›</span>
                <span className="text-white/40 flex items-center gap-1">
                    <span className="w-4 h-4 rounded-full bg-white/5 flex items-center justify-center">2</span> 
                    Amount
                </span>
                <span className="text-white/20">›</span>
                <span className="text-white/40 flex items-center gap-1">
                    <span className="w-4 h-4 rounded-full bg-white/5 flex items-center justify-center">3</span> 
                    Confirm
                </span>
            </div>

            {/* Input */}
            <div className="bg-[#121212] border border-white/5 focus-within:border-orange/50 rounded-xl px-4 py-3 flex items-center gap-3 transition-colors mb-6 shadow-inner">
                <span className="text-white/40"><SearchIcon /></span>
                <input 
                    type="text" 
                    placeholder="@username, address (0x), or email" 
                    className="bg-transparent border-none outline-none w-full text-sm text-white placeholder-white/30"
                />
            </div>

            {/* Continue Button */}
            <button className="w-full bg-gradient-to-r from-orange to-[#FF4500] hover:shadow-[0_0_20px_rgba(249,115,22,0.4)] hover:-translate-y-0.5 text-white font-bold rounded-xl py-3.5 transition-all flex items-center justify-center gap-2">
                Continue <ChevronRight size={16} strokeWidth={3} />
            </button>

            {/* Saved Wallets Header */}
            <p className="text-[10px] font-bold text-white/40 tracking-widest uppercase mt-8 mb-3">Saved Wallets</p>
            
            <div className="bg-[#121212] border border-white/5 rounded-xl h-24 flex flex-col items-center justify-center gap-2 text-white/30">
                <WalletIconEmpty />
                <span className="text-xs font-medium">No saved wallets yet</span>
            </div>
        </div>

      </div>
    </main>
  );
}

const SearchIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
)

const WalletIconEmpty = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a8 8 0 0 1-9.27 7.8A2 2 0 0 1 11 22H6a4 4 0 0 1-4-4V4"/><path d="M22 11v2"/></svg>
)
