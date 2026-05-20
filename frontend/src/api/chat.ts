import axios from 'axios'
import type { ChatRequest, ChatResponse } from '../types/chat'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  timeout: 120_000,
})

export async function sendMessage(payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await http.post<ChatResponse>('/chat', payload)
  return data
}
