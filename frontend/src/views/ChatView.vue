<template>
  <div class="chat-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="logo">
        <el-icon size="28" color="#0ea5e9"><FirstAidKit /></el-icon>
        <span>医疗问答助手</span>
      </div>

      <div class="sidebar-desc">
        基于大语言模型的专业医疗健康问答服务，回答仅供参考，请遵医嘱。
      </div>

      <div class="sidebar-model" v-if="store.currentModel">
        <el-tag type="info" size="small" round>
          <el-icon><Cpu /></el-icon>
          {{ store.currentModel }}
        </el-tag>
      </div>

      <div class="sidebar-tips">
        <p class="tips-title">您可以问我：</p>
        <ul>
          <li v-for="tip in EXAMPLE_TIPS" :key="tip" @click="fillInput(tip)">
            {{ tip }}
          </li>
        </ul>
      </div>

      <div class="sidebar-footer">
        <el-button
          type="danger"
          plain
          size="small"
          :icon="Delete"
          @click="handleClear"
          :disabled="store.messages.length === 0"
        >
          清除对话
        </el-button>
      </div>
    </aside>

    <!-- Main chat area -->
    <main class="chat-main">
      <!-- Header -->
      <header class="chat-header">
        <div class="header-title">
          <el-icon size="18" color="#0ea5e9"><FirstAidKit /></el-icon>
          医疗问答助手
        </div>
        <div class="header-status">
          <span class="status-dot" />
          在线
        </div>
      </header>

      <!-- Messages -->
      <div ref="messageListRef" class="message-list">
        <transition-group name="msg" tag="div">
          <template v-if="store.messages.length === 0">
            <div class="empty-state" key="empty">
              <el-icon size="64" color="#cbd5e1"><ChatDotRound /></el-icon>
              <p>您好！我是您的医疗健康助手</p>
              <p class="sub">请描述您的症状或健康问题，我将尽力为您解答</p>
            </div>
          </template>

          <ChatBubble
            v-for="msg in store.messages"
            :key="msg.id"
            :msg="msg"
          />
        </transition-group>
      </div>

      <!-- Input area -->
      <footer class="input-area">
        <div class="disclaimer">
          <el-icon size="12"><Warning /></el-icon>
          回答仅供健康参考，不构成医疗建议，紧急情况请拨打 120
        </div>
        <div class="input-row">
          <el-input
            v-model="inputText"
            :autosize="{ minRows: 1, maxRows: 5 }"
            type="textarea"
            placeholder="请描述您的症状或健康问题…"
            resize="none"
            class="chat-input"
            @keydown.enter.exact.prevent="handleSend"
            @keydown.enter.shift.exact="() => {}"
          />
          <el-button
            type="primary"
            :loading="store.isLoading"
            :disabled="!inputText.trim()"
            class="send-btn"
            @click="handleSend"
          >
            <el-icon v-if="!store.isLoading"><Promotion /></el-icon>
          </el-button>
        </div>
        <div class="input-hint">Enter 发送 · Shift+Enter 换行</div>
      </footer>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import ChatBubble from '../components/ChatBubble.vue'
import {
  FirstAidKit,
  Delete,
  Promotion,
  Warning,
  ChatDotRound,
  Cpu,
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const store = useChatStore()
const inputText = ref('')
const messageListRef = ref<HTMLElement | null>(null)

const EXAMPLE_TIPS = [
  '感冒发烧怎么处理？',
  '高血压患者饮食注意事项',
  '长期失眠有哪些危害？',
  '如何预防颈椎病？',
  '糖尿病患者能吃水果吗？',
]

function fillInput(text: string) {
  inputText.value = text
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || store.isLoading) return
  inputText.value = ''
  await store.send(text)
}

async function handleClear() {
  await ElMessageBox.confirm('确定要清除所有对话记录吗？', '清除对话', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
  store.clearHistory()
}

function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

watch(() => store.messages.length, scrollToBottom)
watch(
  () => store.messages[store.messages.length - 1]?.content,
  scrollToBottom,
)
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  background: #f1f5f9;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ── Sidebar ── */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  gap: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #f8fafc;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-desc {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.6;
}

.sidebar-model {
  display: flex;
}

.sidebar-model .el-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sidebar-tips {
  flex: 1;
}

.tips-title {
  font-size: 12px;
  color: #64748b;
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sidebar-tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sidebar-tips li {
  font-size: 13px;
  color: #94a3b8;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  line-height: 1.4;
}

.sidebar-tips li:hover {
  background: rgba(14, 165, 233, 0.15);
  color: #38bdf8;
}

.sidebar-footer {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* ── Main ── */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.header-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #10b981;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* ── Messages ── */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

.message-list::-webkit-scrollbar {
  width: 5px;
}

.message-list::-webkit-scrollbar-track {
  background: transparent;
}

.message-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
  color: #94a3b8;
  text-align: center;
  padding-top: 80px;
}

.empty-state p {
  font-size: 18px;
  font-weight: 500;
  color: #64748b;
  margin: 0;
}

.empty-state .sub {
  font-size: 14px;
  color: #94a3b8;
}

/* ── Transition ── */
.msg-enter-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.msg-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

/* ── Input area ── */
.input-area {
  background: #fff;
  border-top: 1px solid #e2e8f0;
  padding: 12px 24px 16px;
  flex-shrink: 0;
}

.disclaimer {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 10px;
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
}

.chat-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 14px;
  border-color: #e2e8f0;
  box-shadow: none;
  resize: none;
  transition: border-color 0.2s;
}

.chat-input :deep(.el-textarea__inner:focus) {
  border-color: #0ea5e9;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  padding: 0;
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  border: none;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: scale(1.04);
}

.send-btn :deep(.el-icon) {
  font-size: 18px;
}

.input-hint {
  text-align: right;
  font-size: 11px;
  color: #cbd5e1;
  margin-top: 6px;
}
</style>
