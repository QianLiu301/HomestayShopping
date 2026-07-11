import { createI18n } from 'vue-i18n'
import zh from './zh'
import en from './en'
import ru from './ru'
import es from './es'
import ja from './ja'
import ko from './ko'

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('lang') || 'en',
  fallbackLocale: 'en',
  messages: { zh, en, ru, es, ja, ko }
})

export default i18n
