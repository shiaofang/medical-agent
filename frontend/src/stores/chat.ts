import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessageStream } from '../api/chat'
import type { ChatMessage } from '../types/chat'

export interface DisplayMessage extends ChatMessage {
  id: number
  loading?: boolean
  error?: boolean
}

let _id = 0
const nextId = () => ++_id

export const useChatStore = defineStore('chat', () => {
  const messages = ref<DisplayMessage[]>([])
  const currentModel = ref('')
  const isLoading = ref(false)

  async function send(text: string) {
    const userMsg: DisplayMessage = {
      id: nextId(),
      role: 'user',
      content: text,
    }
    messages.value.push(userMsg)

    const placeholder: DisplayMessage = {
      id: nextId(),
      role: 'assistant',
      content: '',
      loading: true,
    }
    messages.value.push(placeholder)
    isLoading.value = true

    const history = messages.value
      .filter((m) => !m.loading && !m.error)
      .slice(0, -1)
      .map(({ role, content }) => ({ role, content }))

    try {
      await sendMessageStream(
        { message: text, history },
        (chunk) => {
          const target = messages.value[messages.value.length - 1]
          if (target.loading) target.loading = false
          target.content += chunk
        },
        (model) => {
          currentModel.value = model
        },
        (err) => {
          const target = messages.value[messages.value.length - 1]
          target.content = `请求失败：${err}`
          target.loading = false
          target.error = true
        },
      )
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      const target = messages.value[messages.value.length - 1]
      target.content = `请求失败：${msg}`
      target.loading = false
      target.error = true
    } finally {
      isLoading.value = false
    }
  }

  function clearHistory() {
    messages.value = []
  }

  return { messages, currentModel, isLoading, send, clearHistory }
})
