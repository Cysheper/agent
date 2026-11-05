<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
import { INPUT_PLACEHOLDERS, pick } from '../lib/phrases'

defineProps<{ disabled?: boolean }>()
const emit = defineEmits<{ (e: 'send', text: string): void }>()

const text = ref('')
const placeholder = ref(pick(INPUT_PLACEHOLDERS))
const ta = ref<HTMLTextAreaElement | null>(null)

function resize() {
  const el = ta.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 168) + 'px'
}

function submit() {
  const t = text.value.trim()
  if (!t) return
  emit('send', t)
  text.value = ''
  nextTick(resize)
}

function onEnter(e: KeyboardEvent) {
  // 中文输入法选词回车不发送
  if (e.isComposing || e.shiftKey || e.ctrlKey || e.metaKey || e.altKey) return
  e.preventDefault()
  submit()
}

function setText(t: string) {
  text.value = t
  nextTick(() => {
    ta.value?.focus()
    resize()
  })
}

defineExpose({ setText })

watch(text, resize)
onMounted(resize)
</script>

<template>
  <div class="input-shell">
    <textarea
      ref="ta"
      v-model="text"
      rows="1"
      :placeholder="placeholder"
      maxlength="2000"
      @keydown.enter="onEnter"
    />
    <button
      class="send-btn"
      :disabled="disabled || !text.trim()"
      title="发送"
      @click="submit"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 21l19-9-19-9v7l13.5 2L2.5 14z" /></svg>
    </button>
  </div>
</template>

<style scoped>
.input-shell {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 12px 12px 12px 18px;
  border-radius: 14px;
  border: 1px solid var(--line-strong);
  background: #0a0a0a;
  transition: border-color 0.25s;
}
.input-shell:focus-within {
  border-color: #555;
}

textarea {
  flex: 1;
  padding: 7px 0;
  font-size: 1.05rem;
  line-height: 1.6;
  max-height: 168px;
  overflow-y: auto;
  caret-color: #fff;
}
textarea::placeholder {
  color: #5f5f5f;
}

.send-btn {
  flex: none;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: #f2f2f2;
  transition: transform 0.15s var(--ease-out), background 0.2s;
}
.send-btn svg {
  width: 18px;
  height: 18px;
  fill: #000;
  margin: -1px 0 0 -2px;
}
.send-btn:hover:not(:disabled) {
  background: #fff;
  transform: translateY(-1px);
}
.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}
.send-btn:disabled {
  background: #1a1a1a;
  cursor: not-allowed;
}
.send-btn:disabled svg {
  fill: #4a4a4a;
}
</style>
