<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import ChatInput from './components/ChatInput.vue'
import ChatMessage from './components/ChatMessage.vue'
import LandingHero from './components/LandingHero.vue'
import TypingIndicator from './components/TypingIndicator.vue'
import { useChat } from './composables/useChat'

const { items, streaming, send, clear } = useChat()

const inputRef = ref<InstanceType<typeof ChatInput> | null>(null)
const revealing = ref(false)

const started = computed(() => items.value.length > 0)
const showTyping = computed(() => streaming.value && !revealing.value)

// 最后一条是 Agent 消息且还在逐字浮现时，隐藏打字指示器
watch(
  () => items.value[items.value.length - 1],
  (last) => {
    revealing.value = last?.role === 'agent'
  },
)

// 页面滚动容器（整页滚动，window 级）
function scroller(): Element {
  return document.scrollingElement ?? document.documentElement
}

// 新消息到达时自动滚到底部（用户上翻阅读时不打扰）
watch(
  () => items.value.length,
  async () => {
    await nextTick()
    const el = scroller()
    const last = items.value[items.value.length - 1]
    const near = el.scrollHeight - el.scrollTop - el.clientHeight < 200
    if (last?.role === 'user' || near) {
      window.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
    }
  },
)

// 逐字浮现时贴底跟随
function stickBottom() {
  const el = scroller()
  const near = el.scrollHeight - el.scrollTop - el.clientHeight < 160
  if (near) window.scrollTo(0, el.scrollHeight)
}

function onPick(text: string) {
  inputRef.value?.setText(text)
}
</script>

<template>
  <div class="app">
    <header class="topbar">
      <div class="brand">
        <span class="brand-name">云游</span>
      </div>
      <Transition name="fade">
        <button v-if="started" class="ghost-btn" @click="clear">重新出发</button>
      </Transition>
    </header>

    <main class="stage">
      <Transition name="view" mode="out-in">
        <LandingHero v-if="!started" key="hero" @pick="onPick" />
        <div v-else key="chat" class="chat">
          <ChatMessage
            v-for="(m, i) in items"
            :key="m.id"
            :item="m"
            :is-last="i === items.length - 1"
            @grew="stickBottom"
            @reveal-done="revealing = false"
          />
          <TypingIndicator v-if="showTyping" />
        </div>
      </Transition>
    </main>

    <footer class="dock">
      <ChatInput ref="inputRef" :disabled="streaming" @send="send" />
      <p class="dock-note">AI 生成内容仅供参考 · 对话只留在当前页面</p>
    </footer>
  </div>
</template>
