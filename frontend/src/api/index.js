import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 60000 })

export function getSignal(code) {
  return api.get('/signal', { params: { code } }).then(r => r.data)
}

export function searchStocks(q) {
  return api.get('/stock/search', { params: { q } }).then(r => r.data)
}

export function getStockInfo(code) {
  return api.get('/stock/info', { params: { code } }).then(r => r.data)
}

export function getKline(code, days = 120) {
  return api.get('/stock/kline', { params: { code, days } }).then(r => r.data)
}

export function getDetail(code) {
  return api.get('/stock/detail', { params: { code } }).then(r => r.data)
}