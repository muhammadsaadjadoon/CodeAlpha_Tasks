export type Theme = 'system' | 'light' | 'dark';
export type User = {
  id: number;
  email: string;
  full_name: string;
  theme: Theme;
  has_avatar: boolean;
  avatar_updated_at: string | null;
};
export type EmotionScore = { label: string; probability: number };
export type AnalysisResult = {
  id: number;
  primary_emotion: string;
  confidence: number;
  distribution: EmotionScore[];
  valence: number;
  arousal: number;
  duration_seconds: number;
  sample_rate: number;
  model_version: string;
  source_type: 'recording' | 'upload' | string;
  source_name: string;
  created_at: string;
  privacy: string;
};
export type AnalysisHistoryPage = { items: AnalysisResult[]; total: number };
export type ModelStatus = {
  ready: boolean;
  state: 'ready' | 'available' | 'loading' | 'unavailable' | 'error';
  model_version: string;
  source: string;
  device: string;
  message: string;
};
