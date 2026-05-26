<template>
  <div class="radar-card">
    <div class="radar-header">
      <h3 class="radar-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="title-icon">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>
        四维评分雷达
      </h3>
      <span class="radar-sub">归一化 · 悬浮查看真实分值</span>
    </div>
    <div ref="chartRef" class="radar-chart"></div>
    <div class="legend-row">
      <div v-for="item in legendItems" :key="item.label" class="legend-item">
        <span class="legend-dot" :style="{ background: item.color }"></span>
        <span class="legend-label">{{ item.label }}</span>
        <span class="legend-score" :style="{ color: item.color }">{{ item.displayScore }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ breakdown: Object })
const chartRef = ref(null)
let chart = null

const keys   = ['technical', 'capital', 'sentiment', 'information']
const labels = ['技术面', '资金面', '情绪面', '资讯面']

function rawScores() {
  if (!props.breakdown) return [0, 0, 0, 0]
  return keys.map(k => {
    const v = props.breakdown[k]
    return typeof v === 'object' ? (v.score ?? 0) : (v || 0)
  })
}

function scoreColor(s) {
  if (s > 30)  return '#ef5350'
  if (s > 0)   return '#ff8a65'
  if (s < -30) return '#4caf50'
  if (s < 0)   return '#81c784'
  return '#9e9e9e'
}

const legendItems = computed(() => {
  const raw = rawScores()
  return labels.map((label, i) => ({
    label,
    score: raw[i],
    color: scoreColor(raw[i]),
    displayScore: (raw[i] > 0 ? '+' : '') + raw[i],
  }))
})

function render() {
  if (!chartRef.value || !props.breakdown) return
  if (!chart) chart = echarts.init(chartRef.value)

  const raw        = rawScores()
  const normalized = raw.map(v => Math.max(0, (v + 100) / 2))

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      show: true,
      trigger: 'item',
      backgroundColor: 'rgba(13,18,33,0.95)',
      borderColor: 'rgba(79,142,247,0.3)',
      borderWidth: 1,
      borderRadius: 10,
      padding: [10, 14],
      textStyle: { color: '#c9d1d9', fontSize: 13 },
      extraCssText: 'backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.5);',
      formatter: (params) => {
        const val = params.value
        let html = `<div style="font-weight:700;color:#4f8ef7;margin-bottom:8px;font-size:12px;letter-spacing:0.5px;">
          📊 维度评分（真实分值）
        </div>`
        labels.forEach((label, idx) => {
          const norm = val[idx]
          const rawScore = Math.round((norm * 2) - 100)
          const color = scoreColor(rawScore)
          const bar = Math.abs(rawScore)
          html += `
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
              <span style="color:#8892a4;width:42px;font-size:12px;">${label}</span>
              <div style="flex:1;height:4px;background:rgba(255,255,255,0.08);border-radius:99px;overflow:hidden;">
                <div style="width:${bar}%;height:100%;background:${color};border-radius:99px;"></div>
              </div>
              <span style="font-weight:700;color:${color};font-size:12px;width:28px;text-align:right;">
                ${rawScore > 0 ? '+' : ''}${rawScore}
              </span>
            </div>`
        })
        return html
      }
    },
    radar: {
      center: ['50%', '50%'],
      radius: '68%',
      indicator: labels.map(l => ({ name: l, max: 100 })),
      shape: 'polygon',
      axisName: {
        color: '#c9d1d9',
        fontSize: 13,
        fontFamily: 'Inter, sans-serif',
        fontWeight: 600,
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(79,142,247,0.03)', 'rgba(79,142,247,0.01)'],
        },
      },
      splitLine: {
        lineStyle: { color: 'rgba(255,255,255,0.06)', width: 1 },
      },
      axisLine: {
        lineStyle: { color: 'rgba(255,255,255,0.06)', width: 1 },
      },
    },
    series: [{
      type: 'radar',
      data: [{
        value: normalized,
        name: '评分',
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          color: '#4f8ef7',
          borderColor: '#0d1221',
          borderWidth: 2,
        },
      }],
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(79,142,247,0.35)' },
          { offset: 1, color: 'rgba(79,142,247,0.05)' },
        ]),
      },
      lineStyle: {
        color: '#4f8ef7',
        width: 2,
        shadowColor: 'rgba(79,142,247,0.4)',
        shadowBlur: 8,
      },
    }],
  })
}

onMounted(render)
watch(() => props.breakdown, render, { deep: true })
onUnmounted(() => { chart?.dispose(); chart = null })
</script>

<style scoped>
.radar-card {
  background: rgba(17,24,39,0.8);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(20px);
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
.radar-card:hover {
  border-color: rgba(255,255,255,0.14);
  box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}

.radar-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}
.radar-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 15px;
  font-weight: 600;
  color: #c9d1d9;
}
.title-icon { width: 16px; height: 16px; color: #4f8ef7; }
.radar-sub {
  font-size: 11px;
  color: #4b5568;
  white-space: nowrap;
}

.radar-chart {
  flex: 1;
  width: 100%;
  height: 280px;
}

.legend-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 4px;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.05);
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
}
.legend-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.legend-label {
  color: var(--text-secondary);
  flex: 1;
}
.legend-score {
  font-weight: 700;
  font-family: 'Inter', monospace;
  font-size: 13px;
}
</style>