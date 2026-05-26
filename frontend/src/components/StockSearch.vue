<template>
  <div class="search-wrapper">
    <div class="search-box-container">
      <div class="search-box" :class="{ focused: isFocused, loading }">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input
          id="stock-code-input"
          v-model="code"
          type="text"
          placeholder="输入股票代码、名称或拼音缩写（如 GZMT）"
          autocomplete="off"
          spellcheck="false"
          @input="onInput"
          @focus="onFocus"
          @blur="onBlur"
          @keydown.down.prevent="onKeyDown"
          @keydown.up.prevent="onKeyUp"
          @keydown.enter.prevent="onKeyEnter"
          @keydown.esc="onKeyEsc"
        />
        <button
          id="search-btn"
          class="search-btn"
          @click="onSearchClick"
          :disabled="loading"
          :class="{ 'is-loading': loading }"
          aria-label="查询股票"
        >
          <span v-if="!loading" class="btn-text">
            查询
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="btn-arrow">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </span>
          <span v-else class="btn-spinner">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spinner-svg">
              <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
              <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
            </svg>
            分析中
          </span>
        </button>
      </div>

      <!-- Suggestions Dropdown -->
      <transition name="dropdown-fade">
        <div
          v-if="showDropdown && suggestions.length"
          ref="dropdownRef"
          class="suggestions-dropdown"
        >
          <div
            v-for="(item, index) in suggestions"
            :key="item.code"
            class="suggestion-item"
            :class="{ active: index === selectedIndex }"
            @mousedown="selectSuggestion(item)"
            @mouseenter="selectedIndex = index"
          >
            <div class="item-info">
              <span class="stock-code">{{ item.code }}</span>
              <span class="stock-name">{{ item.name }}</span>
            </div>
            <span class="stock-pinyin" v-if="item.pinyin">{{ item.pinyin }}</span>
          </div>
        </div>
      </transition>
    </div>
    <p class="search-hint">支持代码、中文名称或拼音缩写 · 按 Enter 快速查询</p>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { searchStocks } from '../api/index.js'

const emit = defineEmits(['search'])
defineProps({ loading: Boolean })

const code = ref('')
const isFocused = ref(false)
const showDropdown = ref(false)
const suggestions = ref([])
const selectedIndex = ref(-1)
const dropdownRef = ref(null)

let debounceTimer = null

function onInput() {
  selectedIndex.value = -1
  if (debounceTimer) clearTimeout(debounceTimer)
  
  const q = code.value.trim()
  if (!q) {
    suggestions.value = []
    showDropdown.value = false
    return
  }
  
  debounceTimer = setTimeout(async () => {
    try {
      const res = await searchStocks(q)
      suggestions.value = res || []
      if (isFocused.value) {
        showDropdown.value = suggestions.value.length > 0
      }
    } catch (e) {
      console.error('Failed to search stocks:', e)
    }
  }, 150)
}

function onFocus() {
  isFocused.value = true
  if (code.value.trim() && suggestions.value.length > 0) {
    showDropdown.value = true
  }
}

function onBlur() {
  isFocused.value = false
  // Delay closing dropdown so that mouse click can register
  setTimeout(() => {
    if (!isFocused.value) {
      showDropdown.value = false
    }
  }, 200)
}

function selectSuggestion(item) {
  code.value = item.code
  showDropdown.value = false
  emit('search', item.code)
}

function onSearchClick() {
  showDropdown.value = false
  onSearch()
}

function onSearch() {
  const v = code.value.trim()
  if (v) emit('search', v)
}

function onKeyDown() {
  if (!showDropdown.value || suggestions.value.length === 0) return
  selectedIndex.value = (selectedIndex.value + 1) % suggestions.value.length
  scrollToActiveItem()
}

function onKeyUp() {
  if (!showDropdown.value || suggestions.value.length === 0) return
  selectedIndex.value = (selectedIndex.value - 1 + suggestions.value.length) % suggestions.value.length
  scrollToActiveItem()
}

function onKeyEnter() {
  if (showDropdown.value && selectedIndex.value >= 0 && selectedIndex.value < suggestions.value.length) {
    selectSuggestion(suggestions.value[selectedIndex.value])
  } else {
    showDropdown.value = false
    onSearch()
  }
}

function onKeyEsc() {
  showDropdown.value = false
}

function scrollToActiveItem() {
  setTimeout(() => {
    if (!dropdownRef.value) return
    const activeItem = dropdownRef.value.querySelector('.suggestion-item.active')
    if (!activeItem) return
    
    const container = dropdownRef.value
    const itemTop = activeItem.offsetTop
    const itemHeight = activeItem.offsetHeight
    const containerHeight = container.clientHeight
    const containerScrollTop = container.scrollTop
    
    if (itemTop < containerScrollTop) {
      container.scrollTop = itemTop
    } else if (itemTop + itemHeight > containerScrollTop + containerHeight) {
      container.scrollTop = itemTop + itemHeight - containerHeight
    }
  }, 0)
}

onUnmounted(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<style scoped>
.search-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.search-box-container {
  position: relative;
  width: 100%;
  max-width: 520px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0;
  width: 100%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 6px 6px 6px 16px;
  transition: all 0.25s ease;
  backdrop-filter: blur(10px);
}

.search-box.focused {
  border-color: rgba(79, 142, 247, 0.6);
  background: rgba(79, 142, 247, 0.05);
  box-shadow: 0 0 0 4px rgba(79, 142, 247, 0.1), 0 4px 24px rgba(0, 0, 0, 0.3);
}

.search-icon {
  width: 18px;
  height: 18px;
  color: #8892a4;
  flex-shrink: 0;
  margin-right: 10px;
  transition: color 0.2s;
}
.search-box.focused .search-icon {
  color: #4f8ef7;
}

input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: #e8eaf0;
  font-size: 16px;
  font-family: 'Inter', 'Noto Sans SC', sans-serif;
  font-weight: 500;
  letter-spacing: 0.5px;
  padding: 8px 0;
  min-width: 0;
}

input::placeholder {
  color: #4b5568;
  font-weight: 400;
}

/* search button */
.search-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  font-family: 'Inter', 'Noto Sans SC', sans-serif;
  letter-spacing: 0.3px;
  transition: all 0.2s ease;
  background: linear-gradient(135deg, #4f8ef7 0%, #6366f1 100%);
  color: #fff;
  box-shadow: 0 2px 12px rgba(79, 142, 247, 0.3);
  min-width: 100px;
  justify-content: center;
}

.search-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #6aa0ff 0%, #818cf8 100%);
  box-shadow: 0 4px 20px rgba(79, 142, 247, 0.45);
  transform: translateY(-1px);
}

.search-btn:active:not(:disabled) {
  transform: translateY(0);
}

.search-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-text {
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-arrow {
  width: 14px;
  height: 14px;
  transition: transform 0.2s;
}
.search-btn:hover .btn-arrow {
  transform: translateX(2px);
}

.btn-spinner {
  display: flex;
  align-items: center;
  gap: 6px;
}

.spinner-svg {
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.search-hint {
  font-size: 12px;
  color: #4b5568;
}

/* Suggestions Dropdown (Glassmorphism) */
.suggestions-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(13, 20, 38, 0.88);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  max-height: 280px;
  overflow-y: auto;
  padding: 6px 0;
}

.suggestion-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.suggestion-item:hover,
.suggestion-item.active {
  background: rgba(79, 142, 247, 0.15);
}

.item-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-code {
  font-family: 'Inter', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #4f8ef7;
}

.stock-name {
  font-size: 14px;
  font-weight: 500;
  color: #e8eaf0;
}

.stock-pinyin {
  font-family: 'Inter', monospace;
  font-size: 11px;
  font-weight: 600;
  color: #718096;
  background: rgba(255, 255, 255, 0.04);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  text-transform: uppercase;
}

.suggestion-item.active .stock-pinyin {
  color: #e8eaf0;
  border-color: rgba(79, 142, 247, 0.3);
  background: rgba(79, 142, 247, 0.2);
}

/* Custom Scrollbar */
.suggestions-dropdown::-webkit-scrollbar {
  width: 6px;
}

.suggestions-dropdown::-webkit-scrollbar-track {
  background: transparent;
}

.suggestions-dropdown::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 3px;
}

.suggestions-dropdown::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.24);
}

/* Transitions */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>