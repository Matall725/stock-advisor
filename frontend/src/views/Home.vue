<template>
  <div class="page">

    <!-- ── Decorative ambient orbs ── -->
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <!-- ── Top navigation bar ── -->
    <nav class="topbar">
      <div class="topbar-inner">
        <div class="brand">
          <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
            <polyline points="16 7 22 7 22 13"></polyline>
          </svg>
          <span class="brand-name">股票顾问</span>
          <span class="brand-tag">AI 四维分析</span>
        </div>
        <div class="nav-pills">
          <span class="pill">技术面 40%</span>
          <span class="pill">资金面 25%</span>
          <span class="pill">资讯面 20%</span>
          <span class="pill">情绪面 15%</span>
        </div>
      </div>
    </nav>

    <!-- ── Main content ── -->
    <main class="main">

      <!-- Hero section -->
      <section class="hero">
        <h1 class="hero-title">
          <span class="gradient-text">智能股票</span>操作信号
        </h1>
        <p class="hero-sub">基于四维度量化模型，提供 A 股买卖操作提示</p>
        <StockSearch @search="onSearch" :loading="loading" />
      </section>

      <!-- Error alert -->
      <transition name="fade">
        <div v-if="error" class="error-alert">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="alert-icon">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>{{ error }}</span>
        </div>
      </transition>

      <!-- Loading skeleton -->
      <transition name="fade">
        <div v-if="loading" class="loading-container">
          <div class="loading-status">
            <svg class="spinner" viewBox="0 0 50 50">
              <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
            </svg>
            <span class="loading-title">正在获取并分析股票数据...</span>
            <span class="loading-tip">提示：如果主数据接口网络抖动，系统将尝试备用接口，这可能需要 30 ~ 40 秒，请耐心等待。</span>
          </div>
          <div class="skeleton-wrap">
            <div class="skeleton-card"></div>
            <div class="skeleton-radar"></div>
          </div>
        </div>
      </transition>

      <!-- Result section -->
      <transition name="slide-up">
        <div v-if="signal && !loading" class="result-section">

          <!-- Analysis row -->
          <div class="analysis-row">
            <SignalCard :signal="signal" />
            <ScoreRadar :breakdown="signal.breakdown" />
          </div>

          <!-- Valuation section -->
          <div v-if="signal.valuation" class="valuation-section">
            <ValuationCard :valuation="signal.valuation" :totalScore="signal.total_score" />
          </div>

          <!-- K-line section -->
          <div v-if="kline.length" class="kline-section">
            <div class="section-header">
              <h2 class="section-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="section-icon">
                  <rect x="3" y="3" width="18" height="18" rx="2"></rect>
                  <line x1="3" y1="9" x2="21" y2="9"></line>
                  <line x1="9" y1="21" x2="9" y2="9"></line>
                </svg>
                K 线走势
              </h2>
              <span class="section-meta">近 120 个交易日 · 前复权</span>
            </div>
            <KlineChart :kline="kline" />
          </div>

        </div>
      </transition>

      <!-- Empty state -->
      <transition name="fade">
        <div v-if="!signal && !loading && !error" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="32" cy="32" r="28" stroke-dasharray="4 4" opacity="0.3"/>
              <polyline points="14 42 24 28 34 36 50 18" stroke-width="2" opacity="0.6"/>
              <circle cx="32" cy="32" r="6" fill="rgba(79,142,247,0.15)" stroke="#4f8ef7"/>
            </svg>
          </div>
          <p class="empty-title">输入股票代码、名称或拼音缩写开始分析</p>
          <p class="empty-sub">例如：600519、贵州茅台 或 GZMT</p>
          <div class="example-chips">
            <button class="chip" @click="onSearch('600519')">600519 (代码)</button>
            <button class="chip" @click="onSearch('贵州茅台')">贵州茅台 (名称)</button>
            <button class="chip" @click="onSearch('GZMT')">GZMT (拼音缩写)</button>
            <button class="chip" @click="onSearch('招商银行')">招商银行</button>
          </div>
        </div>
      </transition>

    </main>

    <!-- ── Footer ── -->
    <footer class="footer">
      <p>股票顾问 · 四维度量化分析 · 仅供参考，不构成投资建议</p>
    </footer>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import StockSearch from '../components/StockSearch.vue'
import SignalCard  from '../components/SignalCard.vue'
import ScoreRadar  from '../components/ScoreRadar.vue'
import KlineChart  from '../components/KlineChart.vue'
import ValuationCard from '../components/ValuationCard.vue'
import { getSignal, getKline } from '../api/index.js'

const loading = ref(false)
const error   = ref('')
const signal  = ref(null)
const kline   = ref([])

async function onSearch(code) {
  loading.value = true
  error.value   = ''
  signal.value  = null
  kline.value   = []
  try {
    const [s, k] = await Promise.all([
      getSignal(code),
      getKline(code, 120),
    ])
    signal.value = s
    kline.value  = k.kline || []
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || '查询失败，请检查股票代码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Page shell ── */
.page {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
}

/* ── Ambient orbs ── */
.orb {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  z-index: 0;
}
.orb-1 {
  width: 600px; height: 600px;
  top: -200px; left: -200px;
  background: radial-gradient(circle, rgba(79,142,247,0.12) 0%, transparent 70%);
  animation: orb-drift 20s ease-in-out infinite alternate;
}
.orb-2 {
  width: 500px; height: 500px;
  bottom: 0; right: -150px;
  background: radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%);
  animation: orb-drift 25s ease-in-out infinite alternate-reverse;
}
.orb-3 {
  width: 350px; height: 350px;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(16,185,129,0.05) 0%, transparent 70%);
  animation: orb-drift 30s ease-in-out infinite alternate;
}
@keyframes orb-drift {
  0%   { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, 20px) scale(1.05); }
}

/* ── Topbar ── */
.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(6,9,18,0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.topbar-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
}
.brand-icon {
  width: 22px; height: 22px;
  color: #4f8ef7;
  flex-shrink: 0;
}
.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: #e8eaf0;
  letter-spacing: -0.3px;
}
.brand-tag {
  font-size: 10px;
  font-weight: 600;
  color: #4f8ef7;
  background: rgba(79,142,247,0.12);
  border: 1px solid rgba(79,142,247,0.25);
  border-radius: 4px;
  padding: 2px 6px;
  letter-spacing: 0.3px;
}
.nav-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.pill {
  font-size: 11px;
  color: #8892a4;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 20px;
  padding: 3px 10px;
  white-space: nowrap;
}

/* ── Main ── */
.main {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px 80px;
}

/* ── Hero ── */
.hero {
  text-align: center;
  padding: 72px 0 40px;
}
.hero-title {
  font-size: clamp(32px, 5vw, 52px);
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -1.5px;
  color: #e8eaf0;
  margin-bottom: 12px;
}
.gradient-text {
  background: linear-gradient(135deg, #4f8ef7 0%, #a78bfa 50%, #34d399 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-size: 16px;
  color: #8892a4;
  margin-bottom: 36px;
  font-weight: 400;
}

/* ── Error alert ── */
.error-alert {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 560px;
  margin: 0 auto 24px;
  padding: 12px 16px;
  background: rgba(239,83,80,0.08);
  border: 1px solid rgba(239,83,80,0.25);
  border-radius: 10px;
  color: #ef5350;
  font-size: 14px;
}
.alert-icon { width: 18px; height: 18px; flex-shrink: 0; }

/* ── Loading Container & Skeleton ── */
.loading-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}
.loading-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 16px 0;
  gap: 8px;
}
.loading-title {
  font-size: 16px;
  font-weight: 600;
  color: #e8eaf0;
}
.loading-tip {
  font-size: 13px;
  color: var(--text-secondary);
  max-width: 600px;
  line-height: 1.5;
}
.spinner {
  animation: rotate 2s linear infinite;
  z-index: 2;
  width: 32px;
  height: 32px;
  margin-bottom: 8px;
}
.spinner .path {
  stroke: #4f8ef7;
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}
@keyframes rotate {
  100% { transform: rotate(360deg); }
}
@keyframes dash {
  0% { stroke-dasharray: 1, 150; stroke-dashoffset: 0; }
  50% { stroke-dasharray: 90, 150; stroke-dashoffset: -35; }
  100% { stroke-dasharray: 90, 150; stroke-dashoffset: -124; }
}
.skeleton-wrap {
  display: flex;
  gap: 20px;
}
.skeleton-card, .skeleton-radar {
  flex: 1;
  height: 280px;
  border-radius: 16px;
  background: linear-gradient(90deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.07) 50%, rgba(255,255,255,0.03) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* ── Result section ── */
.result-section { margin-top: 8px; }

.analysis-row {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 20px;
  align-items: stretch;
}
@media (max-width: 768px) {
  .analysis-row { grid-template-columns: 1fr; }
  .nav-pills { display: none; }
}

/* ── Valuation section ── */
.valuation-section { margin-top: 20px; }

/* ── K-line section ── */
.kline-section { margin-top: 20px; }

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  color: #e8eaf0;
}
.section-icon { width: 18px; height: 18px; color: #4f8ef7; }
.section-meta {
  font-size: 13px;
  color: var(--text-secondary);
}

/* ── Empty state ── */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}
.empty-icon {
  width: 80px; height: 80px;
  margin: 0 auto 24px;
  color: #4f8ef7;
}
.empty-icon svg { width: 100%; height: 100%; }
.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #c9d1d9;
  margin-bottom: 8px;
}
.empty-sub {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}
.example-chips {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}
.chip {
  font-size: 13px;
  font-weight: 600;
  color: #4f8ef7;
  background: rgba(79,142,247,0.08);
  border: 1px solid rgba(79,142,247,0.2);
  border-radius: 20px;
  padding: 6px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Inter', monospace;
}
.chip:hover {
  background: rgba(79,142,247,0.18);
  border-color: rgba(79,142,247,0.5);
  transform: translateY(-1px);
}

/* ── Footer ── */
.footer {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: #4b5568;
  border-top: 1px solid rgba(255,255,255,0.04);
}

/* ── Transitions ── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-up-enter-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-up-enter-from { opacity: 0; transform: translateY(24px); }
</style>