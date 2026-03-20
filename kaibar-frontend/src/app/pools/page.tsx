"use client";

import { Activity, Repeat, Plus } from "lucide-react";

export default function PoolsPage() {
  const pools = [
    { pair1: "FREET", pair2: "VPA", fullName1: "Freelancium", fullName2: "VPAword", rate1: 1, rate2: 0.29, trades: "87.15K", tvl1: "805.48K", tvl2: "2.81M", fee: "1%" },
    { pair1: "SDA", pair2: "MBF", fullName1: "Sidra Digital Assets", fullName2: "EBMOF", rate1: 1, rate2: 0.16, trades: "71.69K", tvl1: "247.37K", tvl2: "1.52M", fee: "1%" },
    { pair1: "ECSDA", pair2: "SDA", fullName1: "ECOSIDRA", fullName2: "Sidra Digital Assets", rate1: 1, rate2: 9.51, trades: "52.85K", tvl1: "1.22M", tvl2: "128.71K", fee: "1%" },
    { pair1: "ARMS", pair2: "SDA", fullName1: "Sidra Aram Travel", fullName2: "Sidra Digital As...", rate1: 1, rate2: 5.9, trades: "42.71K", tvl1: "1.09M", tvl2: "184.43K", fee: "0.05%" },
  ];

  return (
    <main className="p-4 pt-6 pb-24 flex flex-col gap-4">
      
      {/* Search Header */}
      <div className="flex justify-between items-center gap-4 mb-2">
        <div className="flex-1 bg-[#1C1C1E] border border-white/5 rounded-full px-4 py-2 flex items-center gap-2">
           <span className="text-white/40">🔍</span>
           <input type="text" placeholder="Search pools..." className="bg-transparent border-none outline-none text-sm w-full text-white" />
        </div>
        <div className="flex items-center gap-1 bg-[#FF4500] text-white px-3 py-2 rounded-full text-xs font-bold border border-[#FF4500]/50 shadow-[0_0_15px_rgba(255,69,0,0.3)]">
           <Activity size={14} /> Most Active
        </div>
      </div>

      {/* ── FEATURED SAUCERSWAP DEX INTEGRATION ── */}
      <div style={{
        marginTop: "10px",
        marginBottom: "16px",
        padding: "20px",
        borderRadius: "24px",
        background: "linear-gradient(145deg, rgba(20, 24, 30, 0.9), rgba(10, 15, 20, 0.95))",
        border: "1px solid rgba(236, 72, 153, 0.25)",
        position: "relative",
        overflow: "hidden",
        boxShadow: "0 12px 32px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.05)"
      }}>
        {/* SaucerSwap Glow Effects */}
        <div style={{ position:"absolute", top:-50, right:-50, width:150, height:150, background:"rgba(236, 72, 153, 0.15)", filter:"blur(50px)", borderRadius:"50%" }} />
        <div style={{ position:"absolute", bottom:-50, left:-50, width:120, height:120, background:"rgba(59, 130, 246, 0.15)", filter:"blur(50px)", borderRadius:"50%" }} />

        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:20, position:"relative", zIndex:2 }}>
          <div>
            <div style={{ display:"inline-flex", alignItems:"center", gap:6, background:"rgba(236, 72, 153, 0.15)", border:"1px solid rgba(236, 72, 153, 0.3)", padding:"4px 10px", borderRadius:999, marginBottom:10 }}>
              <span style={{ width:6, height:6, background:"#EC4899", borderRadius:"50%", animation:"pulse-gold 1.5s infinite" }} />
              <span style={{ fontSize:10, fontWeight:800, color:"#EC4899", letterSpacing:0.5 }}>OFFICIAL SAUCERSWAP ROUTING</span>
            </div>
            <h2 style={{ fontSize:20, fontWeight:900, color:"#fff", margin:"0 0 4px" }}>Provide KAI/HBAR Liquidity</h2>
            <p style={{ fontSize:12, color:"rgba(255,255,255,0.5)", margin:0, lineHeight:1.4 }}>
              Add liquidity instantly to the Hedera ecosystem. The <strong style={{color:"#EC4899"}}>KAIBASaucerSwap</strong> smart contract routes directly to the SaucerSwap V2 Testnet Router.
            </p>
          </div>
          <div style={{ width:54, height:54, background:"linear-gradient(135deg, #EC4899, #8B5CF6)", borderRadius:16, display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0, boxShadow:"0 4px 20px rgba(236,72,153,0.3)" }}>
            <span style={{ fontSize:26 }}>🛸</span>
          </div>
        </div>

        <div style={{ display:"flex", gap:16, position:"relative", zIndex:2 }}>
          <div style={{ flex:1, position:"relative" }}>
            <label style={{ fontSize:10, fontWeight:800, color:"rgba(255,255,255,0.4)", marginBottom:4, display:"block", paddingLeft:4 }}>INPUT HBAR</label>
            <div style={{ position:"relative" }}>
              <input type="number" placeholder="0.0" style={{ width:"100%", background:"rgba(255,255,255,0.05)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:14, padding:"12px 16px", color:"#fff", fontSize:16, fontWeight:700, outline:"none", transition:"border-color 0.2s" }} />
              <span style={{ position:"absolute", right:16, top:13, fontSize:12, fontWeight:800, color:"#10B981" }}>HBAR</span>
            </div>
          </div>
          
          <div style={{ display:"flex", alignItems:"center", marginTop:16 }}>
             <span style={{ fontSize:20, color:"rgba(255,255,255,0.2)" }}>+</span>
          </div>

          <div style={{ flex:1, position:"relative" }}>
            <label style={{ fontSize:10, fontWeight:800, color:"rgba(255,255,255,0.4)", marginBottom:4, display:"block", paddingLeft:4 }}>INPUT KAI</label>
            <div style={{ position:"relative" }}>
              <input type="number" placeholder="0.0" style={{ width:"100%", background:"rgba(255,255,255,0.05)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:14, padding:"12px 16px", color:"#fff", fontSize:16, fontWeight:700, outline:"none", transition:"border-color 0.2s" }} />
              <span style={{ position:"absolute", right:16, top:13, fontSize:12, fontWeight:800, color:"#F97316" }}>KAI</span>
            </div>
          </div>
        </div>

        <div style={{ marginTop:16, position:"relative", zIndex:2 }}>
          <button style={{ width:"100%", background:"linear-gradient(135deg, #EC4899, #8B5CF6)", border:"none", borderRadius:14, padding:"14px", color:"#fff", fontWeight:900, fontSize:14, cursor:"pointer", boxShadow:"0 6px 20px rgba(236,72,153,0.3)", display:"flex", alignItems:"center", justifyContent:"center", gap:8, transition:"transform 0.1s" }} onMouseOver={e => e.currentTarget.style.transform="scale(1.01)"} onMouseOut={e => e.currentTarget.style.transform="scale(1)"}>
            <Plus size={16} strokeWidth={3} /> Add SaucerSwap Liquidity
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {pools.map((pool, idx) => (
          <div key={idx} className="bg-[#1C1C1E] border border-white/5 hover:border-white/10 rounded-2xl p-5 flex flex-col transition-colors group">
            
            {/* Top row */}
            <div className="flex justify-between items-start mb-4">
               <div className="flex items-center gap-3">
                  <div className="flex -space-x-2">
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/50 flex flex-col items-center justify-center relative z-10">
                        <span className="text-[10px] font-black">{pool.pair1[0]}</span>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-green-500/20 border border-green-500/50 flex flex-col items-center justify-center relative z-0">
                         <span className="text-[10px] font-black">{pool.pair2[0]}</span>
                    </div>
                  </div>
                  <div className="flex flex-col">
                     <span className="text-sm font-bold tracking-tight">{pool.pair1}/{pool.pair2}</span>
                     <span className="text-[10px] text-white/50">{pool.fullName1} / {pool.fullName2}</span>
                  </div>
               </div>
               <div className="bg-white/5 px-2 py-0.5 rounded text-[10px] font-medium text-white/70">
                 {pool.fee}
               </div>
            </div>

            {/* Rates */}
            <div className="mb-4">
               <div className="text-[13px] font-medium mb-1 border-b border-white/5 pb-2">
                  1 {pool.pair1} = <span className="font-bold text-white">{pool.rate2} {pool.pair2}</span>
               </div>
               <div className="flex items-center gap-3 mt-2">
                 <div className="flex items-center gap-1 text-[10px] font-bold text-[#FF4500] bg-[#FF4500]/10 px-2 py-0.5 rounded border border-[#FF4500]/20">
                    🔥 Hot
                 </div>
                 <span className="text-[10px] text-white/50">{pool.trades} trades</span>
               </div>
            </div>

            {/* TVL */}
            <div className="flex items-center gap-2 mb-5">
               <span className="text-[10px] text-white/40">🔒</span>
               <span className="text-[10px] text-white/50">{pool.tvl1} {pool.pair1} + {pool.tvl2} {pool.pair2}</span>
            </div>

            {/* Actions */}
            <div className="flex gap-2 mt-auto">
               <button className="flex-1 bg-[#FF4500] hover:bg-[#FF4500]/90 text-white font-bold py-2 rounded-xl text-xs flex items-center justify-center gap-1 transition-colors relative overflow-hidden group-hover:shadow-[0_0_10px_rgba(255,69,0,0.3)]">
                  <Repeat size={12} strokeWidth={3} /> Swap
               </button>
               <button className="flex-1 bg-white/5 hover:bg-white/10 border border-white/5 text-white/80 font-medium py-2 rounded-xl text-xs flex items-center justify-center gap-1 transition-colors">
                  <Plus size={12} strokeWidth={3} /> Quick Add
               </button>
            </div>

          </div>
        ))}
      </div>
      
    </main>
  );
}
