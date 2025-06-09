export interface User {
  id: string
  email: string
  full_name: string
  department?: string
  job_title?: string
  role: 'admin' | 'user' | 'viewer'
  is_active: boolean
  is_verified: boolean
}

export interface Meeting {
  id: string
  title: string
  description?: string
  scheduled_at?: string
  duration_seconds?: number
  participants: string[]
  organizer_id?: string
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled'
  processing_status: 'pending' | 'transcribing' | 'embedding' | 'analyzing' | 'completed' | 'failed'
  s3_audio_uri?: string
  s3_transcript_uri?: string
  processing_started_at?: string
  processing_completed_at?: string
  processing_cost_usd?: number
  created_at: string
  updated_at: string
}

export interface MeetingListResponse {
  items: Meeting[]
  total: number
  skip: number
  limit: number
}

export interface Segment {
  id: string
  meeting_id: string
  sequence_number: number
  start_time_seconds: number
  end_time_seconds: number
  text: string
  speaker?: string
  transcription_confidence?: number
  speaker_confidence?: number
}

export interface Insight {
  id: string
  meeting_id: string
  insight_type: string
  title: string
  content: string
  data: Record<string, any>
  priority?: string
  confidence_score?: number
  created_at: string
}

export interface SearchResult {
  segment_id: string
  meeting_id: string
  meeting_title: string
  meeting_date?: string
  text: string
  speaker?: string
  start_time: number
  end_time: number
  similarity_score: number
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total: number
}

export interface QuestionSource {
  segment_id: string
  meeting_id: string
  meeting_title: string
  text: string
  speaker?: string
  timestamp: number
  relevance_score: number
}

export interface QuestionResponse {
  question: string
  answer: string
  sources?: QuestionSource[]
  confidence_score: number
  tokens_used: number
}

export interface Template {
  id: string
  name: string
  description: string
}

export interface TemplateRunResponse {
  task_id: string
  status: string
  template_id: string
  meeting_id: string
}

export interface PresignedUploadResponse {
  upload_url: string
  s3_key: string
  expires_at: string
}

export interface AuthTokenResponse {
  access_token: string
  token_type: string
}