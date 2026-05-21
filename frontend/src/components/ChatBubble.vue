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
import { marked } from 'marked'
import { FirstAidKit, User } from '@element-plus/icons-vue'
import type { DisplayMessage } from '../stores/chat'

const props = defineProps<{ msg: DisplayMessage }>()

marked.setOptions({ breaks: true })

const avatarStyle = computed(() =>
  props.msg.role === 'assistant'
    ? { background: 'linear-gradient(135deg, #0ea5e9, #6366f1)' }
    : { background: 'linear-gradient(135deg, #10b981, #059669)' },
)

/**
 * 把模型挤在一行里的 Markdown 还原成多行结构。
 * 模型经常输出 "##标题-项目1-项目2"，需要补出换行/空格 marked 才能识别。
 */
function normalizeMarkdown(text: string): string {
  let s = text

  s = s.replace(/(#{1,6})(?=[^\s#])/g, '$1 ')

  s = s.replace(/([^\n])(#{1,6} )/g, '$1\n\n$2')

  s = s.replace(/(?<!\n) ?-(?=[\u4e00-\u9fa5A-Za-z（(*])/g, '\n- ')

  s = s.replace(/(?<!\n)(?<!\d)(\d+)\.(?=[\u4e00-\u9fa5A-Za-z*（(])/g, '\n$1. ')

  s = s.replace(/(^|\n)([-*+]|\d+\.)(?=\S)/g, '$1$2 ')

  s = s.replace(/\n{3,}/g, '\n\n')
  s = s.replace(/^\s+/, '')

  return s
}

const renderedContent = computed(() => {
  if (!props.msg.content) return ''
  if (props.msg.role === 'user') {
    return props.msg.content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br/>')
  }
  const normalized = normalizeMarkdown(props.msg.content)
  return marked.parse(normalized) as string
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

.bubble-text :deep(p) {
  margin: 0 0 8px;
}
.bubble-text :deep(p:last-child) {
  margin-bottom: 0;
}
.bubble-text :deep(h1),
.bubble-text :deep(h2),
.bubble-text :deep(h3) {
  font-size: 15px;
  font-weight: 700;
  margin: 12px 0 6px;
  color: #0f172a;
}
.bubble-text :deep(ul),
.bubble-text :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}
.bubble-text :deep(li) {
  margin-bottom: 4px;
  line-height: 1.6;
}
.bubble-text :deep(strong) {
  font-weight: 600;
  color: #0f172a;
}
.bubble-text :deep(code) {
  background: rgba(0, 0, 0, 0.08);
  padding: 1px 5px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
}
.bubble-text :deep(pre) {
  background: #f1f5f9;
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
}
.bubble-text :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 13px;
}
.bubble-text :deep(blockquote) {
  border-left: 3px solid #0ea5e9;
  padding-left: 12px;
  margin: 8px 0;
  color: #64748b;
}
.bubble-text :deep(table) {
  border-collapse: collapse;
  margin: 10px 0;
  width: 100%;
  font-size: 13px;
  background: #fff;
}
.bubble-text :deep(th),
.bubble-text :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 6px 10px;
  text-align: left;
  vertical-align: top;
}
.bubble-text :deep(th) {
  background: #f1f5f9;
  font-weight: 600;
  color: #0f172a;
}
.bubble-text :deep(tr:nth-child(even) td) {
  background: #f8fafc;
}
.bubble-text :deep(hr) {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 12px 0;
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
