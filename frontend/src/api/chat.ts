import type { ChatRequest } from '../types/chat'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function sendMessageStream(
  payload: ChatRequest,
  onChunk: (chunk: string) => void,
  onDone: (model: string) => void,
  onError: (err: string) => void,
): Promise<void> {
  const res = await fetch(`${BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok || !res.body) {
    onError(`HTTP ${res.status}`)
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const raw = line.slice(6).trim()
      try {
        const parsed = JSON.parse(raw)
        if (parsed.chunk) onChunk(parsed.chunk)
        else if (parsed.error) onError(parsed.error)
        else if (parsed.done) onDone(parsed.model ?? '')
      } catch {
        // 忽略非 JSON 行
      }
    }
  }
}
