import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLangStore = defineStore('lang', () => {
  const current = ref(localStorage.getItem('lang') || 'en')

  function setLang(lang) {
    current.value = lang
    localStorage.setItem('lang', lang)
    window.location.reload()
  }

  return { current, setLang }
})
