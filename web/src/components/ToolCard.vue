<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ToolPayload } from '../lib/types'

const props = defineProps<{ tool: ToolPayload }>()

const open = ref(false)
const resultExpanded = ref(false)

const LABELS: Record<string, string> = {
  web_search: '联网搜索',
  web_fetch: '抓取网页',
  weather: '查询天气',
  shell: '执行命令',
  memory_get: '读取记忆',
  memory_add: '记录备忘',
  get_balance: '查询余额',
}

const label = computed(() => LABELS[props.tool.toolName] ?? props.tool.toolName)

const argsFull = computed(() => {
  const a = props.tool.args
  if (a !== null && typeof a === 'object') {
    try {
      return JSON.stringify(a)
    } catch {
      /* 回退到原始字符串 */
    }
  }
  return String(props.tool.argsRaw ?? '')
})
const argsPreview = computed(() => {
  const s = argsFull.value
  return s.length > 56 ? s.slice(0, 56) + '…' : s
})
const argsPretty = computed(() => pretty(props.tool.args))

const resultFull = computed(() => pretty(props.tool.result))
const resultShown = computed(() =>
  resultExpanded.value ? resultFull.value : resultFull.value.slice(0, 600),
)
const resultTruncated = computed(() => resultFull.value.length > 600)

function pretty(v: unknown): string {
  if (v === null || v === undefined) return 'None'
  if (typeof v === 'string') return v
  try {
    return JSON.stringify(v, null, 2)
  } catch {
    return String(v)
  }
}
</script>

<template>
  <div class="tool-card" :class="{ open }">
    <button
      class="tool-head"
      :aria-expanded="open"
      :title="argsFull"
      @click="open = !open"
    >
      <span class="chevron" :class="{ open }" aria-hidden="true">▸</span>
      <span class="tool-meta">
        <span class="tool-name">{{ label }}</span>
        <span class="tool-args">{{ argsPreview }}</span>
      </span>
      <span class="tool-status">完成</span>
    </button>

    <div class="tool-body">
      <div class="tool-body-inner">
        <div class="tool-section">
          <h4>参数</h4>
          <pre><code>{{ argsPretty }}</code></pre>
        </div>
        <div class="tool-section">
          <h4>结果</h4>
          <pre><code>{{ resultShown }}</code></pre>
          <button v-if="resultTruncated" class="more" @click="resultExpanded = !resultExpanded">
            {{ resultExpanded ? '收起' : '展开全部' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tool-card {
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #0a0a0a;
  overflow: hidden;
  transition: border-color 0.25s;
}
.tool-card:hover {
  border-color: var(--line-strong);
}
.tool-card.open {
  border-color: #444;
}

.tool-head {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  text-align: left;
}
.chevron {
  flex: none;
  color: #777;
  font-size: 0.75rem;
  transition: transform 0.25s var(--ease-out), color 0.2s;
}
.chevron.open {
  transform: rotate(90deg);
  color: #ccc;
}
.tool-meta {
  min-width: 0;
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.tool-name {
  flex: none;
  color: #ddd;
  font-size: 0.95rem;
}
.tool-args {
  color: #777;
  font-size: 0.85rem;
  font-family: ui-monospace, 'SF Mono', Consolas, monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tool-status {
  flex: none;
  color: #666;
  font-size: 0.8rem;
}

.tool-body {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s var(--ease-out);
}
.tool-card.open .tool-body {
  grid-template-rows: 1fr;
}
.tool-body-inner {
  min-height: 0;
  overflow: hidden;
}
.tool-section {
  padding: 12px 14px;
  border-top: 1px solid #1f1f1f;
}
.tool-section h4 {
  margin: 0 0 8px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: #666;
}
.tool-section pre {
  margin: 0;
  padding: 12px 14px;
  background: var(--panel);
  border: 1px solid #1f1f1f;
  border-radius: 8px;
  overflow: auto;
  max-height: 320px;
  color: #b3b3b3;
  font-size: 0.88rem;
  line-height: 1.65;
  font-family: ui-monospace, 'SF Mono', Consolas, monospace;
  white-space: pre-wrap;
  word-break: break-word;
}
.more {
  margin-top: 8px;
  color: #999;
  font-size: 0.82rem;
}
.more:hover {
  color: #ccc;
  text-decoration: underline;
}
</style>
