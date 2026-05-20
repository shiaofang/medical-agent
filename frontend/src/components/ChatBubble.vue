<template>
  <div class="bubble-row" :class="msg.role">
    <div class="avatar">
      <el-avatar :size="38" :style="avatarStyle">
        <el-icon v-if="msg.role === 'assistant'"><FirstAidKit /></el-icon>
        <el-icon v-else><User /></el-icon>
      </el-avatar>
    </div>

    <div class="bubble-wrap">
      <div
        class="bubble"
        :class="{
          'bubble--user': msg.role === 'user',
          'bubble--assistant': msg.role === 'assistant',
          'bubble--error': msg.error,
        }"
      >
        <template v-if="msg.loading">
          <span class="typing-dot" />
          <span class="typing-dot" />
          <span class="typing-dot" />
        </template>
        <template v-else>
          <span class="bubble-text" v-html="renderedContent" />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { FirstAidKit, User } from '@element-plus/icons-vue'
import type { DisplayMessage } from '../stores/chat'

const props = defineProps<{ msg: DisplayMessage }>()

const avatarStyle = computed(() =>
  props.msg.role === 'assistant'
    ? { background: 'linear-gradient(135deg, #0ea5e9, #6366f1)' }
    : { background: 'linear-gradient(135deg, #10b981, #059669)' },
)

const renderedContent = computed(() => {
  if (!props.msg.content) return ''
  return props.msg.content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br/>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
})
</script>

<style scoped>
.bubble-row {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
  align-items: flex-end;
}

.bubble-row.user {
  flex-direction: row-reverse;
}

.avatar {
  flex-shrink: 0;
}

.bubble-wrap {
  max-width: 68%;
  display: flex;
  flex-direction: column;
}

.bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
}

.bubble--user {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.bubble--assistant {
  background: #fff;
  color: #1e293b;
  border-bottom-left-radius: 4px;
  border: 1px solid #e2e8f0;
}

.bubble--error {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #dc2626;
}

.bubble-text :deep(code) {
  background: rgba(0, 0, 0, 0.08);
  padding: 1px 5px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
}

.bubble--user .bubble-text :deep(code) {
  background: rgba(255, 255, 255, 0.25);
}

/* Typing indicator */
.typing-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
  margin: 0 2px;
  animation: bounce 1.2s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: 0s; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.5; }
  40% { transform: translateY(-6px); opacity: 1; }
}
</style>
