<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { HERO_PHRASES, SUB_PHRASES, SUGGESTIONS, pick, shuffle } from '../lib/phrases'

const emit = defineEmits<{ (e: 'pick', text: string): void }>()

const heroIdx = ref(Math.floor(Math.random() * HERO_PHRASES.length))
const sub = ref(pick(SUB_PHRASES))
const tips = ref<string[]>([])

function refresh() {
  tips.value = shuffle(SUGGESTIONS).slice(0, 5)
}

let timer: number | undefined

refresh()

onMounted(() => {
  timer = window.setInterval(() => {
    heroIdx.value = (heroIdx.value + 1) % HERO_PHRASES.length
  }, 6000)
})

onUnmounted(() => window.clearInterval(timer))
</script>

<template>
  <div class="hero">
    <div class="hero-title">
      <Transition name="hero-swap" mode="out-in">
        <h1 :key="heroIdx">{{ HERO_PHRASES[heroIdx] }}</h1>
      </Transition>
    </div>
    <p class="hero-sub">{{ sub }}</p>
    <div class="tips">
      <button v-for="t in tips" :key="t" class="tip" @click="emit('pick', t)">
        {{ t }}
      </button>
      <button class="tip-refresh" @click="refresh">换一批</button>
    </div>
  </div>
</template>

<style scoped>
.hero {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 22px;
  padding: 8px 0 16px;
  text-align: center;
}
/* 内容少时垂直居中；内容超出时随页面自然滚动 */
.hero > :first-child {
  margin-top: auto;
}
.hero > :last-child {
  margin-bottom: auto;
}

.hero-title {
  min-height: 3.8rem;
  display: flex;
  align-items: center;
}
.hero h1 {
  margin: 0;
  font-size: clamp(1.6rem, 7.5vw, 3rem);
  font-weight: 700;
  letter-spacing: 0.01em;
  color: #f5f5f5;
  white-space: nowrap;
}

.hero-swap-enter-active,
.hero-swap-leave-active {
  transition: opacity 0.4s ease;
}
.hero-swap-enter-from,
.hero-swap-leave-to {
  opacity: 0;
}

.hero-sub {
  margin: 0;
  color: #8a8a8a;
  font-size: 1rem;
}

.tips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px 24px;
  max-width: 640px;
}
.tip {
  color: #8a8a8a;
  font-size: 0.98rem;
  padding: 2px 0;
  transition: color 0.2s;
}
.tip:hover {
  color: #f5f5f5;
  text-decoration: underline;
  text-underline-offset: 4px;
}
.tip-refresh {
  color: #555;
  font-size: 0.85rem;
  padding: 2px 0;
  transition: color 0.2s;
}
.tip-refresh:hover {
  color: #aaa;
}
</style>
