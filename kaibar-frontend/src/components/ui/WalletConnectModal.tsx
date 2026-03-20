"use client";
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { useKaibarStore } from "@/store/useKaibarStore";
import { useConnect } from "wagmi";

export default function WalletConnectModal({ onClose }: { onClose: () => void }) {
  const { connected, walletType, accountId, connectWallet, disconnectWallet } = useKaibarStore();
  const [connecting, setConnecting] = useState<string | null>(null);
  const [step, setStep] = useState<"select" | "connecting" | "done">("select");
  const { connectAsync, connectors } = useConnect();

  const handleConnect = async (type: "hashpack" | "metamask") => {
    setConnecting(type);
    setStep("connecting");
    
    if (type === "metamask") {
      try {
        const injected = connectors.find((c) => c.id === 'metaMask' || c.id === 'injected');
        if (injected) {
          const res = await connectAsync({ connector: injected });
          connectWallet(type, res.accounts[0]);
        } else {
          await new Promise((r) => setTimeout(r, 1800));
          connectWallet(type);
        }
      } catch (err) {
        console.error(err);
        setStep("select");
        return;
      }
    } else {
      await new Promise((r) => setTimeout(r, 1800));
      connectWallet(type);
    }
    
    setStep("done");
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-end justify-center"
         style={{ background: "rgba(0,0,0,0.7)", backdropFilter: "blur(8px)" }}
         onClick={onClose}>
      <div className="w-full max-w-[600px] rounded-t-3xl p-6 pb-10"
           style={{ background: "linear-gradient(180deg, #1B4332 0%, #0D2B1F 100%)", border: "1px solid rgba(255,215,0,0.25)" }}
           onClick={(e) => e.stopPropagation()}>

        {/* Handle */}
        <div className="w-10 h-1 rounded-full bg-white/20 mx-auto mb-5" />

        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-black text-white">Connect Wallet</h2>
          <button onClick={onClose} className="text-white/40 hover:text-white transition-colors p-1">
            <X size={20} />
          </button>
        </div>

        {step === "select" && (
          <div className="flex flex-col gap-3">
            {/* HashPack */}
            <button onClick={() => handleConnect("hashpack")}
              className="flex items-center gap-4 p-4 rounded-2xl transition-all"
              style={{ background: "rgba(255,215,0,0.08)", border: "1px solid rgba(255,215,0,0.3)" }}>
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                   style={{ background: "linear-gradient(135deg,#4ECDC4,#45B7D1)" }}>🧊</div>
              <div className="text-left">
                <p className="font-bold text-white">HashPack</p>
                <p className="text-xs text-white/50">Hedera native · Account ID</p>
              </div>
              <span className="ml-auto text-white/30">›</span>
            </button>

            {/* MetaMask */}
            <button onClick={() => handleConnect("metamask")}
              className="flex items-center gap-4 p-4 rounded-2xl transition-all"
              style={{ background: "rgba(249,115,22,0.08)", border: "1px solid rgba(249,115,22,0.3)" }}>
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                   style={{ background: "linear-gradient(135deg,#F97316,#EA580C)" }}>🦊</div>
              <div className="text-left">
                <p className="font-bold text-white">MetaMask</p>
                <p className="text-xs text-white/50">EVM compatible · 0x address</p>
              </div>
              <span className="ml-auto text-white/30">›</span>
            </button>

            {/* WalletConnect */}
            <button className="flex items-center gap-4 p-4 rounded-2xl transition-all opacity-60 cursor-not-allowed"
              style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.1)" }}>
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl bg-[#3B99FC]/20">🔗</div>
              <div className="text-left">
                <p className="font-bold text-white/70">WalletConnect</p>
                <p className="text-xs text-white/40">Coming soon</p>
              </div>
              <span className="ml-auto text-xs text-white/30 bg-white/10 px-2 py-0.5 rounded-full">Soon</span>
            </button>

            <p className="text-center text-[10px] text-white/30 mt-2">
              By connecting, you agree to KAIBAR Terms of Service
            </p>
          </div>
        )}

        {step === "connecting" && (
          <div className="flex flex-col items-center gap-4 py-8">
            <div className="w-16 h-16 rounded-full animate-spin"
                 style={{ border: "3px solid rgba(255,215,0,0.2)", borderTopColor: "#FFD700" }} />
            <p className="text-white font-semibold">Connecting to {connecting === "hashpack" ? "HashPack" : "MetaMask"}...</p>
            <p className="text-xs text-white/40">Approve request in your wallet</p>
          </div>
        )}

        {step === "done" && (
          <div className="flex flex-col items-center gap-4 py-6">
            <div className="w-16 h-16 rounded-full flex items-center justify-center text-3xl"
                 style={{ background: "linear-gradient(135deg,#FFD700,#F97316)" }}>✓</div>
            <div className="text-center">
              <p className="font-bold text-white text-lg">Connected!</p>
              <p className="text-xs text-white/50 mt-1 font-mono">{accountId}</p>
            </div>
            <button onClick={onClose}
              className="btn-gold w-full py-3 rounded-xl font-bold text-sm mt-2">
              Enter KAIBAR →
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
