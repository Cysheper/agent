<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { ChatItem } from '../lib/types'
import { renderMarkdown } from '../lib/markdown'
import ToolCard from './ToolCard.vue'

const props = defineProps<{ item: ChatItem; isLast: boolean }>()
const emit = defineEmits<{ (e: 'grew'): void; (e: 'reveal-done'): void }>()

const shown = ref(0)
const done = ref(false)
const html = computed(() => renderMarkdown(props.item.content))

// Agent 消息逐字浮现：时长按长度自适应（500ms ~ 2.4s），完成后切换为 Markdown 渲染。
// 后端按"轮"吐消息（LLM stream=False + JSON 协议），靠这里制造流式观感
onMounted(() => {
  if (props.item.role !== 'agent') return
  const total = props.item.content.length
  if (total <= 0) {
    done.value = true
    return
  }
  const duration = Math.min(Math.max(total * 14, 500), 2400)
  const start = performance.now()

  const step = (now: number) => {
    const p = Math.min((now - start) / duration, 1)
    shown.value = Math.floor(total * (1 - Math.pow(1 - p, 3)))
    emit('grew')
    if (p < 1) {
      requestAnimationFrame(step)
    } else {
      done.value = true
      if (props.isLast) emit('reveal-done')
    }
  }
  requestAnimationFrame(step)
})
</script>

<template>
  <div class="msg" :class="item.role">
    <div v-if="item.role === 'user'" class="user-bubble">{{ item.content }}</div>
    <ToolCard v-else-if="item.role === 'tool'" :tool="item.tool!" />
    <div v-else-if="item.role === 'error'" class="err-text">{{ item.content }}</div>
    <div v-else class="agent-text">
      <span v-if="!done" class="plain">{{ item.content.slice(0, shown) }}</span>
      <div v-else class="md" v-html="html" />
      <span v-if="!done" class="cursor" aria-hidden="true" />
    </div>
  </div>
</template>
