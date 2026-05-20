export type Role = 'user' | 'assistant'

export interface ChatMessage {
  role: Role
  content: string
}

export interface ChatRequest {
  message: string
  history: ChatMessage[]
}

export interface ChatResponse {
  reply: string
  model: string
}
