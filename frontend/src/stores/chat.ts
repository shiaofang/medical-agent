import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessage } from '../api/chat'
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
      .slice(0, -2)
      .map(({ role, content }) => ({ role, content }))

    try {
      const res = await sendMessage({ message: text, history })
      placeholder.content = res.reply
      placeholder.loading = false
      currentModel.value = res.model
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      placeholder.content = `请求失败：${msg}`
      placeholder.loading = false
      placeholder.error = true
    } finally {
      isLoading.value = false
    }
  }

  function clearHistory() {
    messages.value = []
  }

  return { messages, currentModel, isLoading, send, clearHistory }
})
