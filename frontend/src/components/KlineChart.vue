<template>
  <div class="kline-card">
    <div ref="chartRef" class="kline-chart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props    = defineProps({ kline: Array })
const chartRef = ref(null)
let chart      = null

function render() {
  if (!chartRef.value || !props.kline || !props.kline.length) return
  if (!chart) chart = echarts.init(chartRef.value)

  const dates  = props.kline.map(k => k.date?.slice(0, 10) || k.date)
  // ECharts candlestick: [open, close, low, high]
  const ohlc   = props.kline.map(k => [
    +k.open.toFixed(2),
    +k.close.toFixed(2),
    +k.low.toFixed(2),
    +k.high.toFixed(2),
  ])
  const volumes = props.kline.map(k => k.volume)
  const closes  = props.kline.map(k => k.close)

  function ma(n) {
    return closes.map((_, i) => {
      if (i < n - 1) return null
      return +(closes.slice(i - n + 1, i + 1).reduce((a, b) => a + b, 0) / n).toFixed(2)
    })
  }

  const COLOR_RED   = '#ef5350'
  const COLOR_GREEN = '#26a69a'

  // ── Pattern Detection Algorithm ──
  const pts = []
  const markedDates = new Set()

  function addPt(idx, pt) {
    const d = dates[idx]
    if (markedDates.has(d)) return
    markedDates.add(d)
    pts.push(pt)
  }

  // 1. Detect Double Tops & Bottoms first (High Priority, needs window check)
  const valleys = []
  const peaks = []
  for (let i = 1; i < props.kline.length - 1; i++) {
    const prevLow = props.kline[i - 1].low
    const currLow = props.kline[i].low
    const nextLow = props.kline[i + 1].low
    if (currLow <= prevLow && currLow <= nextLow) {
      valleys.push({ idx: i, low: currLow })
    }

    const prevHigh = props.kline[i - 1].high
    const currHigh = props.kline[i].high
    const nextHigh = props.kline[i + 1].high
    if (currHigh >= prevHigh && currHigh >= nextHigh) {
      peaks.push({ idx: i, high: currHigh })
    }
  }

  // Match Double Bottoms
  for (let v2 = 1; v2 < valleys.length; v2++) {
    for (let v1 = 0; v1 < v2; v1++) {
      const idx1 = valleys[v1].idx
      const idx2 = valleys[v2].idx
      const dist = idx2 - idx1
      if (dist >= 5 && dist <= 25) {
        const diff = Math.abs(valleys[v1].low - valleys[v2].low) / valleys[v1].low
        if (diff <= 0.015) {
          const middlePrices = props.kline.slice(idx1 + 1, idx2).map(k => k.high)
          const maxMid = Math.max(...middlePrices)
          if (maxMid > valleys[v1].low * 1.03) {
            addPt(idx2, {
              name: '双底',
              coord: [dates[idx2], valleys[v2].low],
              value: '双底',
              symbol: 'pin',
              symbolSize: 14,
              symbolOffset: [0, 12],
              itemStyle: { color: '#ef5350' },
              label: { show: true, position: 'bottom', color: '#ef5350', fontSize: 10, formatter: '双底' }
            })
            break
          }
        }
      }
    }
  }

  // Match Double Tops
  for (let p2 = 1; p2 < peaks.length; p2++) {
    for (let p1 = 0; p1 < p2; p1++) {
      const idx1 = peaks[p1].idx
      const idx2 = peaks[p2].idx
      const dist = idx2 - idx1
      if (dist >= 5 && dist <= 25) {
        const diff = Math.abs(peaks[p1].high - peaks[p2].high) / peaks[p1].high
        if (diff <= 0.015) {
          const middlePrices = props.kline.slice(idx1 + 1, idx2).map(k => k.low)
          const minMid = Math.min(...middlePrices)
          if (minMid < peaks[p1].high * 0.97) {
            addPt(idx2, {
              name: '双顶',
              coord: [dates[idx2], peaks[p2].high],
              value: '双顶',
              symbol: 'pin',
              symbolSize: 14,
              symbolOffset: [0, -12],
              itemStyle: { color: '#26a69a' },
              label: { show: true, position: 'top', color: '#26a69a', fontSize: 10, formatter: '双顶' }
            })
            break
          }
        }
      }
    }
  }

  // 2. Scan single/triple candle patterns
  for (let i = 2; i < props.kline.length; i++) {
    const k2 = props.kline[i - 2]
    const k1 = props.kline[i - 1]
    const k = props.kline[i]

    const open = k.open
    const close = k.close
    const high = k.high
    const low = k.low
    const body = Math.abs(close - open)
    const totalRange = high - low
    const bodyMax = Math.max(open, close)
    const bodyMin = Math.min(open, close)
    const upperShadow = high - bodyMax
    const lowerShadow = bodyMin - low

    // Morning Star (早晨之星)
    const isMorningStar = (
      k2.close < k2.open && (k2.open - k2.close) / k2.open > 0.01 &&
      Math.max(k1.open, k1.close) < k2.close && Math.abs(k1.close - k1.open) / k1.open < 0.008 &&
      k.close > k.open && k.close > (k2.open + k2.close) / 2
    )
    if (isMorningStar) {
      addPt(i, {
        name: '早晨之星',
        coord: [dates[i], low],
        value: '早晨之星',
        symbol: 'path://M12 2L15 9H22L17 14L19 21L12 17L5 21L7 14L2 9H9L12 2Z',
        symbolSize: 15,
        symbolOffset: [0, 15],
        itemStyle: { color: '#ef5350' },
        label: { show: true, position: 'bottom', color: '#ef5350', fontSize: 10, formatter: '早晨之星' }
      })
      continue
    }

    // Evening Star (黄昏之星)
    const isEveningStar = (
      k2.close > k2.open && (k2.close - k2.open) / k2.open > 0.01 &&
      Math.min(k1.open, k1.close) > k2.close && Math.abs(k1.close - k1.open) / k1.open < 0.008 &&
      k.close < k.open && k.close < (k2.open + k2.close) / 2
    )
    if (isEveningStar) {
      addPt(i, {
        name: '黄昏之星',
        coord: [dates[i], high],
        value: '黄昏之星',
        symbol: 'path://M12 2L15 9H22L17 14L19 21L12 17L5 21L7 14L2 9H9L12 2Z',
        symbolSize: 15,
        symbolOffset: [0, -15],
        itemStyle: { color: '#26a69a' },
        label: { show: true, position: 'top', color: '#26a69a', fontSize: 10, formatter: '黄昏之星' }
      })
      continue
    }

    // Bullish Engulfing (看涨吞没)
    const isBullishEngulfing = (
      k1.close < k1.open && k.close > k.open &&
      k.close > k1.open && k.open < k1.close &&
      (k.close - k.open) / k.open > 0.015
    )
    if (isBullishEngulfing) {
      addPt(i, {
        name: '看涨吞没',
        coord: [dates[i], low],
        value: '看涨吞没',
        symbol: 'arrow',
        symbolSize: 10,
        symbolOffset: [0, 10],
        itemStyle: { color: '#ef5350' },
        label: { show: true, position: 'bottom', color: '#ef5350', fontSize: 10, formatter: '看涨吞没' }
      })
      continue
    }

    // Bearish Engulfing (看跌吞没)
    const isBearishEngulfing = (
      k1.close > k1.open && k.close < k.open &&
      k.close < k1.open && k.open > k1.close &&
      (k.open - k.close) / k.open > 0.015
    )
    if (isBearishEngulfing) {
      addPt(i, {
        name: '看跌吞没',
        coord: [dates[i], high],
        value: '看跌吞没',
        symbol: 'arrow',
        symbolSize: 10,
        symbolOffset: [0, -10],
        symbolRotate: 180,
        itemStyle: { color: '#26a69a' },
        label: { show: true, position: 'top', color: '#26a69a', fontSize: 10, formatter: '看跌吞没' }
      })
      continue
    }

    // Doji (十字星)
    const isDoji = (
      totalRange > 0 && 
      body <= totalRange * 0.1 && 
      upperShadow > body && 
      lowerShadow > body
    )
    if (isDoji) {
      addPt(i, {
        name: '十字星',
        coord: [dates[i], high],
        value: '十字星',
        symbol: 'circle',
        symbolSize: 6,
        symbolOffset: [0, -8],
        itemStyle: { color: '#f6c90e' },
        label: { show: true, position: 'top', color: '#f6c90e', fontSize: 10, formatter: '十字星' }
      })
      continue
    }

    // Hammer (锤子线)
    const isHammer = (
      lowerShadow >= 2 * body &&
      upperShadow <= body * 0.2 &&
      body > 0 &&
      (body / open) < 0.03
    )
    if (isHammer) {
      addPt(i, {
        name: '锤子线',
        coord: [dates[i], low],
        value: '锤子线',
        symbol: 'pin',
        symbolSize: 12,
        symbolOffset: [0, 10],
        itemStyle: { color: '#ef5350' },
        label: { show: true, position: 'bottom', color: '#ef5350', fontSize: 10, formatter: '锤子线' }
      })
      continue
    }

    // Inverted Hammer (倒锤子线)
    const isInvertedHammer = (
      upperShadow >= 2 * body &&
      lowerShadow <= body * 0.2 &&
      body > 0 &&
      (body / open) < 0.03
    )
    if (isInvertedHammer) {
      addPt(i, {
        name: '倒锤子',
        coord: [dates[i], high],
        value: '倒锤子',
        symbol: 'pin',
        symbolSize: 12,
        symbolOffset: [0, -10],
        itemStyle: { color: '#26a69a' },
        label: { show: true, position: 'top', color: '#26a69a', fontSize: 10, formatter: '倒锤子' }
      })
      continue
    }
  }

  chart.setOption({
    backgroundColor: 'transparent',

    animation: true,
    animationDuration: 600,
    animationEasing: 'cubicOut',

    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', crossStyle: { color: 'rgba(79,142,247,0.4)' } },
      backgroundColor: 'rgba(13,18,33,0.95)',
      borderColor: 'rgba(79,142,247,0.3)',
      borderWidth: 1,
      borderRadius: 10,
      padding: [10, 14],
      textStyle: { color: '#c9d1d9', fontSize: 12 },
      extraCssText: 'backdrop-filter:blur(12px);box-shadow:0 8px 32px rgba(0,0,0,0.5);',
      formatter: (params) => {
        const kp = params.find(p => p.seriesName === 'K线')
        const vp = params.find(p => p.seriesName === '成交量')
        if (!kp) return ''
        const [o, c, l, h] = kp.data
        const isRed  = c >= o
        const clr    = isRed ? COLOR_RED : COLOR_GREEN
        const pct    = o ? (((c - o) / o) * 100).toFixed(2) : '0.00'
        const vol    = vp ? (vp.data / 10000).toFixed(0) + '万' : '--'
        return `
          <div style="min-width:160px;">
            <div style="font-size:11px;color:#8892a4;margin-bottom:6px;">${kp.axisValue}</div>
            <div style="display:grid;grid-template-columns:auto auto;gap:4px 12px;font-size:12px;">
              <span style="color:#8892a4;">开盘</span><span style="font-weight:600;">${o}</span>
              <span style="color:#8892a4;">收盘</span>
              <span style="font-weight:700;color:${clr};">${c} <small>(${isRed ? '+' : ''}${pct}%)</small></span>
              <span style="color:#8892a4;">最高</span><span style="color:${COLOR_RED};font-weight:600;">${h}</span>
              <span style="color:#8892a4;">最低</span><span style="color:${COLOR_GREEN};font-weight:600;">${l}</span>
              <span style="color:#8892a4;">成交量</span><span>${vol}</span>
            </div>
          </div>`
      },
    },

    legend: {
      data: ['K线', 'MA5', 'MA10', 'MA20'],
      top: 8,
      right: 16,
      icon: 'roundRect',
      itemWidth: 12,
      itemHeight: 4,
      textStyle: { color: '#c9d1d9', fontSize: 12 },
      inactiveColor: '#4b5568',
    },

    grid: [
      { left: 60, right: 16, top: 40, height: '52%' },
      { left: 60, right: 16, top: '73%', height: '15%' },
    ],

    xAxis: [
      {
        type: 'category',
        data: dates,
        gridIndex: 0,
        axisLabel: {
          color: '#a0aec0',
          fontSize: 12,
          formatter: v => v?.slice(5),  // show MM-DD
        },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
        axisTick: { show: false },
        splitLine: { show: false },
        boundaryGap: true,
      },
      {
        type: 'category',
        data: dates,
        gridIndex: 1,
        show: false,
        boundaryGap: true,
      },
    ],

    yAxis: [
      {
        gridIndex: 0,
        axisLabel: { color: '#a0aec0', fontSize: 12 },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)', type: 'dashed' } },
        scale: true,
        min: 'dataMin',
        max: 'dataMax',
      },
      {
        gridIndex: 1,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
      },
    ],

    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 55, end: 100, filterMode: 'weakFilter' },
      {
        type: 'slider',
        xAxisIndex: [0, 1],
        start: 55, end: 100,
        bottom: 4, height: 20,
        borderColor: 'rgba(255,255,255,0.06)',
        backgroundColor: 'rgba(255,255,255,0.02)',
        fillerColor: 'rgba(79,142,247,0.1)',
        handleStyle: { color: '#4f8ef7', borderColor: '#4f8ef7' },
        moveHandleStyle: { color: 'rgba(79,142,247,0.5)' },
        selectedDataBackground: {
          lineStyle: { color: '#4f8ef7' },
          areaStyle: { color: 'rgba(79,142,247,0.05)' },
        },
        textStyle: { color: '#a0aec0', fontSize: 11 },
        filterMode: 'weakFilter',
      },
    ],

    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: ohlc,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color:        COLOR_RED,
          color0:       COLOR_GREEN,
          borderColor:  COLOR_RED,
          borderColor0: COLOR_GREEN,
          borderWidth:  2.0,
        },
        markPoint: {
          data: pts,
          tooltip: {
            formatter: (params) => {
              return `<div style="font-weight:700;color:${params.color};font-size:12px;">形态: ${params.name}</div>`
            }
          }
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma(5),
        smooth: true,
        symbol: 'none',
        xAxisIndex: 0,
        yAxisIndex: 0,
        lineStyle: { color: '#f6c90e', width: 2.2, opacity: 0.85 },
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma(10),
        smooth: true,
        symbol: 'none',
        xAxisIndex: 0,
        yAxisIndex: 0,
        lineStyle: { color: '#a78bfa', width: 2.2, opacity: 0.85 },
      },
      {
        name: 'MA20',
        type: 'line',
        data: ma(20),
        smooth: true,
        symbol: 'none',
        xAxisIndex: 0,
        yAxisIndex: 0,
        lineStyle: { color: '#34d399', width: 2.2, opacity: 0.85 },
      },
      {
        name: '成交量',
        type: 'bar',
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1,
        itemStyle: {
          color: p => props.kline[p.dataIndex]?.close >= props.kline[p.dataIndex]?.open
            ? COLOR_RED
            : COLOR_GREEN,
          opacity: 0.7,
        },
        emphasis: { itemStyle: { opacity: 1 } },
      },
    ],
  })
}

onMounted(() => {
  render()
  const ro = new ResizeObserver(() => chart?.resize())
  ro.observe(chartRef.value)
  onUnmounted(() => { ro.disconnect(); chart?.dispose(); chart = null })
})
watch(() => props.kline, render, { deep: true })
</script>

<style scoped>
.kline-card {
  background: rgba(17,24,39,0.8);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 20px 16px 16px;
  backdrop-filter: blur(20px);
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}
.kline-card:hover {
  border-color: rgba(255,255,255,0.14);
  box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}
.kline-chart {
  width: 100%;
  height: 500px;
}
</style>