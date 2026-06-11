import { GoogleGenAI } from '@google/genai';

// Initialize the SDK. It expects process.env.API_KEY to be available in the environment.
// For this frontend-only demo, we assume the environment provides it.
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY, vertexai: true });
const MODEL_NAME = 'gemini-2.5-flash';

export async function generateSummary(documentText: string): Promise<string> {
  try {
    const prompt = `
      Analyze the following financial document and provide a structured summary.
      Format the output in Markdown with the following sections:
      - **Executive Summary**
      - **Revenue & Financial Performance**
      - **Guidance & Outlook**
      - **Key Risks**
      - **Strategic Opportunities**

      Document Content:
      ${documentText}
    `;

    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: prompt,
    });
    return response.text || 'No summary generated.';
  } catch (error) {
    console.error("Error generating summary:", error);
    throw new Error("Failed to generate summary. Please check your API key and connection.");
  }
}

export async function compareDocuments(doc1Name: string, doc1Text: string, doc2Name: string, doc2Text: string): Promise<string> {
  try {
    const prompt = `
      Compare the following two financial documents. 
      Highlight the key differences and trends between them, focusing on:
      1. Revenue changes
      2. Shifts in strategic direction or guidance
      3. Changes in risk factors

      Format the output clearly in Markdown.

      Document 1 (${doc1Name}):
      ${doc1Text}

      Document 2 (${doc2Name}):
      ${doc2Text}
    `;

    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: prompt,
    });
    return response.text || 'No comparison generated.';
  } catch (error) {
    console.error("Error comparing documents:", error);
    throw new Error("Failed to compare documents.");
  }
}

export async function askQuestion(question: string, context: string): Promise<string> {
  try {
    const prompt = `
      You are FinSight, an expert financial research assistant.
      Answer the user's question based ONLY on the provided context from uploaded documents.
      If the answer cannot be found in the context, state clearly that you do not have enough information based on the provided documents.
      Be concise, professional, and cite specific numbers where available.

      Context:
      ${context}

      Question: ${question}
    `;

    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: prompt,
    });
    return response.text || 'No answer generated.';
  } catch (error) {
    console.error("Error answering question:", error);
    throw new Error("Failed to get an answer.");
  }
}
