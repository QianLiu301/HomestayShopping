import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

export const useLangStore = defineStore('lang', () => {
  const current = ref(localStorage.getItem('lang') || 'zh')

  function setLang(lang) {
    current.value = lang
    localStorage.setItem('lang', lang)
    // Reload to apply language change fully
    window.location.reload()
  }

  return { current, setLang }
})
