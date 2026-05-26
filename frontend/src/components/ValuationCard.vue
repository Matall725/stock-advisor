<template>
  <div class="valuation-card" v-if="valuation">
    <!-- Top accent glow bar based on operation color -->
    <div class="card-accent" :style="{ background: accentGradient }"></div>

    <!-- Header Section -->
    <div class="card-header">
      <div class="header-left">
        <span class="header-icon">📊</span>
        <h2 class="header-title">区间估值与操作分类</h2>
      </div>
      <!-- Operation Category Badge -->
      <div class="operation-badge" :style="{ color: operationColor, borderColor: operationColor, background: operationBg }">
        {{ valuation.operation_class }}
      </div>
    </div>

    <!-- Suggestions text -->
    <div class="suggestion-section">
      <p class="suggestion-text">{{ valuation.suggestion }}</p>
    </div>

    <!-- Interactive Price Ruler Slider -->
    <div class="ruler-container">
      <div class="ruler-labels">
        <div class="ruler-label-item buy-side">
          <span class="label-dot red-dot"></span>
          支撑位 (低吸区): <span class="label-val text-red">{{ valuation.support }} 元</span>
        </div>
        <div class="ruler-label-item current-side">
          <span class="label-dot pulse-dot" :style="{ background: operationColor }"></span>
          最新价: <span class="label-val text-glow" :style="{ color: operationColor }">{{ valuation.current_price }} 元</span>
        </div>
        <div class="ruler-label-item sell-side">
          <span class="label-dot green-dot"></span>
          压力位 (高抛区): <span class="label-val text-green">{{ valuation.resistance }} 元</span>
        </div>
      </div>

      <!-- The slider visual bar -->
      <div class="slider-track-wrap">
        <!-- Scale ticks background -->
        <div class="scale-ticks">
          <span v-for="i in 11" :key="i" class="tick"></span>
        </div>

        <div class="slider-track">
          <!-- Buy Zone Highlight -->
          <div class="zone buy-zone" :style="{ left: buyStartPct + '%', width: buyWidthPct + '%' }">
            <span class="zone-label">买入区</span>
          </div>
          <!-- Hold Zone Highlight -->
          <div class="zone hold-zone" :style="{ left: holdStartPct + '%', width: holdWidthPct + '%' }">
            <span class="zone-label">持有区</span>
          </div>
          <!-- Sell Zone Highlight -->
          <div class="zone sell-zone" :style="{ left: sellStartPct + '%', width: sellWidthPct + '%' }">
            <span class="zone-label">卖出区</span>
          </div>

          <!-- Current Price Needle Indicator -->
          <div 
            class="current-needle" 
            :style="{ left: currentPricePct + '%', borderColor: operationColor }"
          >
            <div class="needle-tooltip" :style="{ background: operationColor }">
              {{ valuation.current_price }} 元
            </div>
            <div class="needle-point" :style="{ background: operationColor, boxShadow: `0 0 10px ${operationColor}` }"></div>
          </div>
        </div>
      </div>

      <!-- Ruler Footnotes -->
      <div class="ruler-bounds">
        <span class="bound-val">{{ minVal }} 元</span>
        <span class="bound-text">支撑与压力区间分布图</span>
        <span class="bound-val">{{ maxVal }} 元</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  valuation: Object,
  totalScore: Number
})

// Calculate the range bounds for visualization
const minVal = computed(() => {
  if (!props.valuation) return 0
  const sup = props.valuation.support
  const buyL = props.valuation.buy_zone[0]
  const base = buyL > 0 ? buyL : sup
  return Math.max(0.01, round2(base * 0.9))
})

const maxVal = computed(() => {
  if (!props.valuation) return 0
  const res = props.valuation.resistance
  const sellU = props.valuation.sell_zone[1]
  const base = sellU > 0 ? sellU : res
  return round2(base * 1.1)
})

function round2(v) {
  return Math.round(v * 100) / 100
}

// Convert price to percentage on the ruler slider
function getPct(price) {
  const min = minVal.value
  const max = maxVal.value
  if (max === min) return 50
  const pct = ((price - min) / (max - min)) * 100
  return Math.max(0, Math.min(100, pct))
}

// Percentages for regions
const buyStartPct = computed(() => getPct(props.valuation.buy_zone[0]))
const buyWidthPct = computed(() => {
  const start = getPct(props.valuation.buy_zone[0])
  const end = getPct(props.valuation.buy_zone[1])
  return Math.max(2, end - start)
})

const holdStartPct = computed(() => getPct(props.valuation.buy_zone[1]))
const holdWidthPct = computed(() => {
  const start = getPct(props.valuation.buy_zone[1])
  const end = getPct(props.valuation.sell_zone[0])
  return Math.max(2, end - start)
})

const sellStartPct = computed(() => getPct(props.valuation.sell_zone[0]))
const sellWidthPct = computed(() => {
  const start = getPct(props.valuation.sell_zone[0])
  const end = getPct(props.valuation.sell_zone[1])
  return Math.max(2, end - start)
})

const currentPricePct = computed(() => getPct(props.valuation.current_price))

// Operation accent styling colors based on score & classification
const operationColor = computed(() => {
  if (!props.valuation) return '#9e9e9e'
  const score = props.totalScore ?? 0
  const op = props.valuation.operation_class
  
  if (score >= 60 || op.includes('强烈推荐买入')) return '#ef5350' // Strong Buy -> Red
  if (score >= 20 || op.includes('吸纳') || op.includes('买入')) return '#ff8a65' // Buy -> Light Red/Orange
  if (score <= -60 || op.includes('减仓') || op.includes('卖出')) return '#2e7d32' // Strong Sell -> Dark Green
  if (score <= -20 || op.includes('减持') || op.includes('防范')) return '#4caf50' // Sell -> Green
  return '#a0aec0' // Hold/Neutral -> Gray
})

const operationBg = computed(() => {
  return `${operationColor.value}15`
})

const accentGradient = computed(() => {
  const c = operationColor.value
  return `linear-gradient(90deg, ${c}dd 0%, ${c}44 40%, transparent 100%)`
})
</script>

<script>
// Prevent double imports if any
export default {
  name: 'ValuationCard'
}
</script>

<style scoped>
.valuation-card {
  position: relative;
  background: rgba(17, 24, 39, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 24px 28px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  transition: all 0.3s ease;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
}

.valuation-card:hover {
  border-color: rgba(255, 255, 255, 0.14);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4);
}

/* Top colored accent line */
.card-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: 20px 20px 0 0;
}

/* Header styling */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #e8eaf0;
  margin: 0;
}

/* Badge */
.operation-badge {
  font-size: 13px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 8px;
  border: 1px solid currentColor;
  letter-spacing: 0.2px;
}

/* Suggestion text */
.suggestion-section {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 14px 18px;
  margin-bottom: 24px;
}

.suggestion-text {
  font-size: 14px;
  line-height: 1.6;
  color: #c9d1d9;
  margin: 0;
}

/* Ruler and Slider styling */
.ruler-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ruler-labels {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.ruler-label-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #a0aec0;
}

.ruler-label-item.current-side {
  justify-content: center;
}

.ruler-label-item.sell-side {
  justify-content: flex-end;
}

.label-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.red-dot {
  background: #ef5350;
  box-shadow: 0 0 6px #ef5350;
}

.green-dot {
  background: #4caf50;
  box-shadow: 0 0 6px #4caf50;
}

.pulse-dot {
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.4);
    opacity: 0.6;
  }
}

.label-val {
  font-weight: 700;
  font-family: 'Inter', monospace;
  margin-left: 2px;
}

.text-red { color: #ef5350; }
.text-green { color: #4caf50; }
.text-glow {
  text-shadow: 0 0 8px currentColor;
}

/* Track slider styling */
.slider-track-wrap {
  position: relative;
  height: 38px;
  margin-top: 10px;
}

.scale-ticks {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.tick {
  width: 1px;
  height: 5px;
  background: rgba(255, 255, 255, 0.15);
}

.slider-track {
  position: absolute;
  bottom: 8px;
  left: 0;
  right: 0;
  height: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 99px;
  border: 1px solid rgba(255, 255, 255, 0.03);
}

/* Zones colors */
.zone {
  position: absolute;
  top: -1px;
  bottom: -1px;
  border-radius: 99px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.buy-zone {
  background: rgba(239, 83, 80, 0.18);
  border: 1px solid rgba(239, 83, 80, 0.25);
  box-shadow: inset 0 0 6px rgba(239, 83, 80, 0.1);
}

.hold-zone {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.sell-zone {
  background: rgba(76, 175, 80, 0.18);
  border: 1px solid rgba(76, 175, 80, 0.25);
  box-shadow: inset 0 0 6px rgba(76, 175, 80, 0.1);
}

.zone-label {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.5px;
  opacity: 0.75;
  color: #fff;
  transform: translateY(-16px);
  position: absolute;
}

.buy-zone .zone-label { color: #ef5350; }
.hold-zone .zone-label { color: #a0aec0; }
.sell-zone .zone-label { color: #4caf50; }

/* Current Price Indicator Needle */
.current-needle {
  position: absolute;
  top: -14px;
  height: 40px;
  width: 2px;
  border-left: 2px dashed;
  transform: translateX(-50%);
  z-index: 5;
  transition: left 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.needle-point {
  position: absolute;
  bottom: 0px;
  left: -4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.needle-tooltip {
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 800;
  font-family: 'Inter', monospace;
  color: #fff;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Bounds */
.ruler-bounds {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #6b7c96;
}

.bound-val {
  font-family: 'Inter', monospace;
  font-weight: 600;
}

.bound-text {
  font-size: 10px;
  letter-spacing: 0.3px;
  opacity: 0.8;
}

/* Mobile responsive adjustments */
@media (max-width: 576px) {
  .ruler-labels {
    grid-template-columns: 1fr;
    gap: 4px;
  }
  .ruler-label-item.current-side,
  .ruler-label-item.sell-side {
    justify-content: flex-start;
  }
  .valuation-card {
    padding: 18px 20px;
  }
}
</style>
