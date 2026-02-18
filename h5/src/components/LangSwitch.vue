<template>
  <div class="lang-switch" @click="showPicker = true">
    <van-icon name="globe-o" size="18" />
    <span class="lang-text">{{ langLabels[current] }}</span>
  </div>

  <van-action-sheet
    v-model:show="showPicker"
    :title="t('lang.title')"
    :actions="actions"
    @select="onSelect"
    cancel-text=""
  />
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLangStore } from '../stores/lang'

const { t } = useI18n()
const langStore = useLangStore()
const current = ref(langStore.current)
const showPicker = ref(false)

const langLabels = { zh: '中文', en: 'EN', ru: 'РУ', es: 'ES' }

const actions = [
  { name: '中文', value: 'zh' },
  { name: 'English', value: 'en' },
  { name: 'Русский', value: 'ru' },
  { name: 'Español', value: 'es' }
]

function onSelect(action) {
  showPicker.value = false
  if (action.value !== current.value) {
    langStore.setLang(action.value)
  }
}
</script>

<style scoped>
.lang-switch {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font-size: 13px;
  color: var(--text);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.lang-text {
  font-weight: 500;
}
</style>
