import { createI18n } from 'vue-i18n'
import zh from './zh'
import en from './en'
import ru from './ru'
import es from './es'

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('lang') || 'en',
  fallbackLocale: 'en',
  messages: { zh, en, ru, es }
})

export default i18n
