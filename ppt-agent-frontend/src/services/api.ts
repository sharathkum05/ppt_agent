import axios from 'axios';

// @ts-ignore - Vite env types
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export interface GeneratePresentationRequest {
  prompt: string;
}

export interface GeneratePresentationResponse {
  presentation_id: string;
  shareable_link: string;
  title: string;
  slide_count: number;
}

export const generatePresentation = async (
  prompt: string
): Promise<GeneratePresentationResponse> => {
  const response = await axios.post<GeneratePresentationResponse>(
    `${API_BASE_URL}/generate-presentation`,
    {
      prompt,
    }
  );
  return response.data;
};
