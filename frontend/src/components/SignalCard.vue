<template>
  <div class="signal-card" v-if="signal">

    <!-- Top accent bar (color = signal color) -->
    <div class="card-accent" :style="{ background: accentGradient }"></div>

    <!-- Signal badge -->
    <div class="badge-wrap">
      <div class="signal-badge" :style="{ background: badgeBg, color: signal.color }">
        <span class="badge-dot" :style="{ background: signal.color }"></span>
        {{ signal.signal }}
      </div>
    </div>

    <!-- Stock info -->
    <div class="stock-info">
      <div class="stock-name">{{ signal.name || '未知股票' }}</div>
      <div class="stock-code-row">
        <span class="stock-code">{{ signal.code }}</span>
        <span class="updated-at">{{ updatedTime }}</span>
      </div>
    </div>

    <!-- Score ring -->
    <div class="score-section">
      <div class="score-ring-wrap">
        <svg class="score-ring" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="42" class="ring-bg"/>
          <circle
            cx="50" cy="50" r="42"
            class="ring-progress"
            :style="{
              stroke: signal.color,
              strokeDashoffset: ringOffset,
              filter: `drop-shadow(0 0 6px ${signal.color}80)`,
            }"
          />
        </svg>
        <div class="score-center">
          <span class="score-num" :style="{ color: signal.color }">
            {{ displayScore }}
          </span>
          <span class="score-label">综合评分</span>
        </div>
      </div>
      <div class="score-note">量化范围 -100 ~ +100</div>
    </div>

    <!-- Dimension breakdown -->
    <div class="breakdown">
      <div 
        v-for="dim in dims" 
        :key="dim.key" 
        class="dim-item"
        :class="{ 'is-expanded': expanded[dim.key] }"
        @click="toggleExpanded(dim.key)"
      >
        <div class="dim-main-row">
          <div class="dim-header">
            <span class="dim-icon" :style="{ background: dim.iconBg }">{{ dim.emoji }}</span>
            <span class="dim-label">{{ dim.label }}</span>
            <span class="dim-weight">{{ dim.weight }}</span>
          </div>
          <div class="dim-bar-row">
            <div class="dim-bar-track">
              <div
                class="dim-bar-fill"
                :style="{
                  width: barWidth(dim.score) + '%',
                  background: barColor(dim.score),
                  boxShadow: `0 0 8px ${barColor(dim.score)}60`,
                }"
              ></div>
            </div>
            <span class="dim-score" :style="{ color: barColor(dim.score) }">
              {{ dim.score > 0 ? '+' : '' }}{{ dim.score }}
            </span>
            <span class="chevron-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </span>
          </div>
        </div>

        <!-- Smooth height transition container -->
        <div class="dim-detail-container" @click.stop>
          <div class="dim-detail-content">
            <div class="dim-divider"></div>
            <div v-if="props.signal?.breakdown?.[dim.key]?.detail" class="dim-detail-inner">
              <!-- Technical / Capital / Sentiment sub-list -->
              <div v-if="dim.key !== 'information'" class="sub-list">
                <div 
                  v-for="(sub, subKey) in props.signal.breakdown[dim.key].detail" 
                  :key="subKey" 
                  class="sub-item"
                >
                  <div class="sub-info">
                    <span class="sub-label">{{ getSubLabel(subKey) }}</span>
                    <span class="sub-weight">权重 {{ sub.weight ?? 0 }}%</span>
                  </div>
                  <div class="sub-bar-row">
                    <div class="sub-bar-track">
                      <div
                        class="sub-bar-fill"
                        :style="{
                          width: getSubBarWidth(sub.score, subKey) + '%',
                          background: barColor(sub.score),
                          boxShadow: `0 0 6px ${barColor(sub.score)}40`,
                        }"
                      ></div>
                    </div>
                    <span class="sub-score" :style="{ color: barColor(sub.score) }">
                      {{ sub.score > 0 ? '+' : '' }}{{ sub.score }}
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- Information sub-list -->
              <div v-else class="info-list">
                <div class="info-stat-row">
                  <div class="info-stat-card">
                    <span class="info-stat-label">利多词频</span>
                    <span class="info-stat-val text-red">
                      {{ props.signal.breakdown.information.detail.bullish ?? 0 }} <small>次</small>
                    </span>
                  </div>
                  <div class="info-stat-card">
                    <span class="info-stat-label">利空词频</span>
                    <span class="info-stat-val text-green">
                      {{ props.signal.breakdown.information.detail.bearish ?? 0 }} <small>次</small>
                    </span>
                  </div>
                  <div class="info-stat-card">
                    <span class="info-stat-label">多空比值</span>
                    <span class="info-stat-val">
                      {{ props.signal.breakdown.information.detail.ratio ?? 0 }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ signal: Object })

const expanded = ref({
  technical: false,
  capital: false,
  sentiment: false,
  information: false,
})

function toggleExpanded(key) {
  expanded.value[key] = !expanded.value[key]
}

const SUB_ITEM_METRICS = {
  ma: { label: '均线排列', max: 30 },
  macd: { label: 'MACD 指标', max: 25 },
  kdj: { label: 'KDJ 指标', max: 20 },
  rsi: { label: 'RSI 指标', max: 25 },
  trend: { label: '资金趋势', max: 50 },
  ratio: { label: '大单占比', max: 50 },
  limit: { label: '市场涨跌停', max: 40 },
  turnover: { label: '换手偏离度', max: 30 },
  volume: { label: '量比偏离度', max: 30 },
}

function getSubLabel(subKey) {
  return SUB_ITEM_METRICS[subKey]?.label || subKey.toUpperCase()
}

function getSubBarWidth(score, subKey) {
  const metric = SUB_ITEM_METRICS[subKey]
  if (!metric) return Math.min(100, Math.abs(score))
  return Math.min(100, (Math.abs(score) / metric.max) * 100)
}

const LABELS = {
  technical:   { label: '技术面', emoji: '📈', weight: '40%', iconBg: 'rgba(79,142,247,0.15)' },
  capital:     { label: '资金面', emoji: '💰', weight: '25%', iconBg: 'rgba(246,201,14,0.15)' },
  information: { label: '资讯面', emoji: '📰', weight: '20%', iconBg: 'rgba(167,139,250,0.15)' },
  sentiment:   { label: '情绪面', emoji: '🌡️', weight: '15%', iconBg: 'rgba(52,211,153,0.15)' },
}

const dims = computed(() => {
  if (!props.signal?.breakdown) return []
  return Object.entries(props.signal.breakdown).map(([key, info]) => ({
    key,
    score: typeof info === 'object' ? info.score : info,
    ...LABELS[key],
  }))
})

// Ring progress: score -100..100 → 0..263 stroke-dasharray 263 (2π×42)
const CIRCUMFERENCE = 2 * Math.PI * 42  // ≈ 263.9
const ringOffset = computed(() => {
  const s = props.signal?.total_score ?? 0
  const pct = (s + 100) / 200  // 0–1
  return CIRCUMFERENCE * (1 - pct)
})

const displayScore = computed(() => {
  const s = props.signal?.total_score ?? 0
  return (s > 0 ? '+' : '') + s
})

const updatedTime = computed(() => {
  if (!props.signal?.updated_at) return ''
  const d = new Date(props.signal.updated_at)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

const accentGradient = computed(() => {
  const c = props.signal?.color || '#9e9e9e'
  return `linear-gradient(90deg, ${c}cc 0%, ${c}33 60%, transparent 100%)`
})

const badgeBg = computed(() => {
  const c = props.signal?.color || '#9e9e9e'
  return `${c}18`
})

function barWidth(score) {
  return Math.min(100, Math.abs(score))
}

function barColor(score) {
  if (score > 30) return '#ef5350'
  if (score > 0)  return '#ff8a65'
  if (score < -30) return '#4caf50'
  if (score < 0)  return '#81c784'
  return '#9e9e9e'
}
</script>

<style scoped>
.signal-card {
  position: relative;
  background: rgba(17,24,39,0.8);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 28px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}

.signal-card:hover {
  border-color: rgba(255,255,255,0.14);
  box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}

/* Top accent bar */
.card-accent {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  border-radius: 20px 20px 0 0;
}

/* Badge */
.badge-wrap { margin-bottom: 16px; }
.signal-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 700;
  border: 1px solid currentColor;
  opacity: 0.9;
}
.badge-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  animation: pulse-dot 1.5s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.7); }
}

/* Stock info */
.stock-info { margin-bottom: 20px; }
.stock-name {
  font-size: 26px;
  font-weight: 800;
  color: #e8eaf0;
  line-height: 1.3;
}
.stock-code-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}
.stock-code {
  font-size: 13px;
  color: var(--text-secondary);
  font-family: 'Inter', monospace;
  font-weight: 600;
  background: rgba(255,255,255,0.06);
  padding: 2px 8px;
  border-radius: 5px;
}
.updated-at {
  font-size: 12px;
  color: var(--text-muted);
}

/* Score ring */
.score-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}
.score-ring-wrap {
  position: relative;
  width: 110px;
  height: 110px;
}
.score-ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}
.ring-bg {
  fill: none;
  stroke: rgba(255,255,255,0.06);
  stroke-width: 7;
}
.ring-progress {
  fill: none;
  stroke-width: 7;
  stroke-linecap: round;
  stroke-dasharray: 263.9;
  transition: stroke-dashoffset 1s cubic-bezier(0.16, 1, 0.3, 1);
}
.score-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.score-num {
  font-size: 26px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.5px;
}
.score-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
  font-weight: 500;
}
.score-note {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 8px;
}

/* Breakdown */
.breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.dim-item {
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.dim-item:hover, .dim-item.is-expanded {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.08);
}
.dim-main-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.dim-header {
  display: flex;
  align-items: center;
  gap: 7px;
}
.dim-icon {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}
.dim-label {
  font-size: 14px;
  color: #e8eaf0;
  flex: 1;
  font-weight: 600;
}
.dim-weight {
  font-size: 11px;
  color: var(--text-muted);
}
.dim-bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dim-bar-track {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 99px;
  overflow: hidden;
}
.dim-bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.dim-score {
  font-size: 14px;
  font-weight: 700;
  font-family: 'Inter', monospace;
  min-width: 32px;
  text-align: right;
}

/* Chevron */
.chevron-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  transition: transform 0.3s ease, color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.dim-item:hover .chevron-icon {
  color: var(--text-secondary);
}
.dim-item.is-expanded .chevron-icon {
  transform: rotate(180deg);
  color: var(--text-primary);
}
.dim-item:not(.is-expanded):hover .chevron-icon {
  transform: rotate(180deg);
}

/* Accordion transition */
.dim-detail-container {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}
.dim-item:hover .dim-detail-container,
.dim-item.is-expanded .dim-detail-container {
  grid-template-rows: 1fr;
}
.dim-detail-content {
  min-height: 0;
}

.dim-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
  margin: 12px 0 8px;
}

/* Child lists styling */
.sub-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 4px 4px 6px 30px;
}
.sub-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.sub-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sub-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}
.sub-weight {
  font-size: 10px;
  color: var(--text-muted);
}
.sub-bar-track {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.04);
  border-radius: 99px;
  overflow: hidden;
}
.sub-bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.sub-score {
  font-size: 12px;
  font-weight: 700;
  font-family: 'Inter', monospace;
  min-width: 28px;
  text-align: right;
}

/* Information stats card grid */
.info-list {
  padding: 4px 4px 6px 30px;
}
.info-stat-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 4px;
}
.info-stat-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 8px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.info-stat-label {
  font-size: 10px;
  color: var(--text-muted);
}
.info-stat-val {
  font-size: 13px;
  font-weight: 700;
  font-family: 'Inter', sans-serif;
  color: var(--text-primary);
}
.info-stat-val small {
  font-size: 9px;
  font-weight: 400;
  color: var(--text-muted);
}
.text-red {
  color: var(--red-light) !important;
}
.text-green {
  color: var(--green-light) !important;
}
</style>