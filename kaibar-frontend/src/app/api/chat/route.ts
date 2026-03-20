import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const { message } = await req.json();

    if (!message) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    // Connect directly to local Ollama instance Qwen 0.5b
    const ollamaPayload = {
      model: "qwen:0.5b",
      prompt: `You are KAI, the premium AI advisor for the KAI DeFi ecosystem on Hedera. Keep answers extremely short, professional, and friendly.\n\nUser: ${message}\nKAI:`,
      stream: false,
    };

    const response = await fetch("http://localhost:11434/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(ollamaPayload),
    });

    if (!response.ok) {
      throw new Error(`Ollama responded with status: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      text: data.response || "No response generated.",
      agent: "KAI Premium (Next.js)",
      emoji: "✨"
    });

  } catch (error: any) {
    console.error("Ollama NextJS Connection Error:", error);
    return NextResponse.json(
      { error: "Failed to connect to local Ollama.", details: error.message },
      { status: 500 }
    );
  }
}
