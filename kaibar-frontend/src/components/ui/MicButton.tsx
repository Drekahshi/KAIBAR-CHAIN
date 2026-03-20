"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";

interface MicButtonProps {
  onTranscript?: (text: string) => void;
  onFinalTranscript?: (text: string) => void;
  size?: "sm" | "md" | "lg";
}

export default function MicButton({ onTranscript, onFinalTranscript, size = "md" }: MicButtonProps) {
  const [listening, setListening] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [supported, setSupported] = useState(true);
  const recognitionRef = useRef<any>(null);
  const finalRef = useRef<string>("");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) { setSupported(false); return; }

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;     // auto-stops after a pause
    recognitionRef.current.interimResults = true;
    recognitionRef.current.lang = "en-US";
    recognitionRef.current.maxAlternatives = 1;

    recognitionRef.current.onresult = (e: any) => {
      let interim = "";
      let final = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        if (e.results[i].isFinal) {
          final += t;
        } else {
          interim += t;
        }
      }
      // Show interim text live in input field
      if (interim) onTranscript?.(interim);
      if (final) {
        finalRef.current = final;
        onTranscript?.(final);
      }
    };

    recognitionRef.current.onspeechend = () => {
      setProcessing(true);
    };

    recognitionRef.current.onend = () => {
      setListening(false);
      setProcessing(false);
      // Auto-send the final captured transcript
      if (finalRef.current.trim()) {
        onFinalTranscript?.(finalRef.current.trim());
        finalRef.current = "";
      }
    };

    recognitionRef.current.onerror = (e: any) => {
      console.error("STT Error:", e.error);
      setListening(false);
      setProcessing(false);
    };
  }, [onTranscript, onFinalTranscript]);

  const toggle = useCallback(() => {
    if (!recognitionRef.current) return;
    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      finalRef.current = "";
      recognitionRef.current.start();
      setListening(true);
    }
  }, [listening]);

  const sz = size === "sm" ? 28 : size === "lg" ? 52 : 42;
  const iconSz = size === "sm" ? 14 : size === "lg" ? 22 : 18;

  return (
    <button
      onClick={toggle}
      disabled={!supported}
      title={!supported ? "Speech recognition not supported in this browser" : listening ? "Stop recording" : "🎙️ Tap to speak"}
      style={{
        width: sz, height: sz,
        borderRadius: "50%",
        display: "flex", alignItems: "center", justifyContent: "center",
        flexShrink: 0,
        background: listening
          ? "linear-gradient(135deg,#E63946,#C1121F)"
          : processing
          ? "linear-gradient(135deg,#F97316,#FFD700)"
          : "linear-gradient(135deg,#FFD700,#F97316)",
        boxShadow: listening
          ? "0 0 0 5px rgba(230,57,70,0.25), 0 0 20px rgba(230,57,70,0.4)"
          : "0 0 12px rgba(255,215,0,0.35)",
        animation: listening ? "pulse-gold 1.2s ease-in-out infinite" : "none",
        transition: "all 0.2s ease",
        cursor: supported ? "pointer" : "not-allowed",
        opacity: supported ? 1 : 0.4,
        border: "none",
        outline: "none",
      }}>
      {processing
        ? <Loader2 size={iconSz} color="#1B4332" style={{ animation: "spin 1s linear infinite" }} />
        : listening
        ? <MicOff size={iconSz} color="#fff" strokeWidth={2.5} />
        : <Mic size={iconSz} color="#1B4332" strokeWidth={2.5} />}
    </button>
  );
}
