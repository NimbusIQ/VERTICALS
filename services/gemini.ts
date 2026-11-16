/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";

// Using gemini-3.1-pro-preview for complex coding and large context tasks.
const GEMINI_MODEL = 'gemini-3.1-pro-preview';

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const SYSTEM_INSTRUCTION = `You are NimbusIQ Agent, a specialized AI Automation and Software Engineering Engineer.
Your goal is to take user uploaded files—which might be polished UI designs, unstructured data, complex documents, or photos of diagrams—and instantly write and deploy a fully functional, interactive, single-page HTML/JS/CSS application based on the user's intent.

CORE DIRECTIVES:
1. **Analyze & Execute**: Look at the input data.
    - **Sketches/Wireframes**: Compile them into a modern, clean UI tailored to Enterprise standards.
    - **Data/Documents**: Synthesize into interactive dashboards, functional tools, or CRM/ERP views.
    - **Real-World Concepts**: If the user uploads messy data or generalized photos, build clear interactive utilities or gamify it.
    - Treat edge cases intelligently. Do not fail.

2. **NO EXTERNAL IMAGES**:
    - **CRITICAL**: Do NOT use <img src="..."> with external URLs (like imgur, placeholder.com, or generic internet URLs). They will fail.
    - **INSTEAD**: Use **CSS shapes**, **inline SVGs**, **Emojis**, or **CSS gradients** to visually represent elements.

3. **Make it Interactive**: The output MUST NOT be static. It needs buttons, interactivity, data visualization, or fluid dynamics.
4. **Self-Contained**: The output must be a single HTML file with embedded CSS (<style>) and JavaScript (<script>). No external dependencies unless absolutely necessary (Tailwind via CDN, simple libraries like Chart.js allowed).
5. **Robust & Creative**: Build high-quality "NimbusIQ level" interactive apps even from messy inputs.

RESPONSE FORMAT:
Return ONLY the raw HTML code. Do not wrap it in markdown code blocks (\`\`\`html ... \`\`\`). Start immediately with <!DOCTYPE html>.`;

export interface GeminiFile {
  data: string;
  mimeType: string;
}

export async function bringToLife(prompt: string, files: GeminiFile[] = []): Promise<string> {
  const parts: any[] = [];
  
  // Combine user prompt with a strong directive
  let finalPrompt = "Analyze the provided input(s). ";
  
  if (files.length > 0) {
    if (files.some(f => f.mimeType === 'application/pdf')) {
      finalPrompt += "Review the documents carefully. ";
    } else {
      finalPrompt += "Detect what functionality is implied from the image(s). ";
    }
    finalPrompt += "Extract key data, UI elements, and logic. If it represents real-world objects, gamify the experience. ";
  }
  
  finalPrompt += prompt || "Build a fully interactive web app based on the input.";
  finalPrompt += "\n\nIMPORTANT: Do NOT use external image URLs. Recreate visuals using CSS, SVGs, or Emojis.";

  parts.push({ text: finalPrompt });

  for (const file of files) {
    parts.push({
      inlineData: {
        data: file.data,
        mimeType: file.mimeType,
      },
    });
  }

  try {
    const response: GenerateContentResponse = await ai.models.generateContent({
      model: GEMINI_MODEL,
      contents: {
        parts: parts
      },
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        temperature: 0.5, // Higher temperature for more creativity with mundane inputs
      },
    });

    let text = response.text || "<!-- Failed to generate content -->";

    // Cleanup if the model still included markdown fences despite instructions
    text = text.replace(/^```html\s*/, '').replace(/^```\s*/, '').replace(/```$/, '');

    return text;
  } catch (error) {
    console.error("Gemini Generation Error:", error);
    throw error;
  }
}