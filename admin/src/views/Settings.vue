<template>
  <div>
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>{{ $t('settings.transferPricing') }}</span>
          <el-button type="primary" :loading="saving" @click="onSave">{{ $t('settings.saveChanges') }}</el-button>
        </div>
      </template>

      <el-form :model="form" label-width="180px" v-loading="loading" style="max-width:600px">
        <el-form-item :label="$t('settings.pickupPrice')">
          <el-input-number v-model="form.pickup_price" :min="0" :precision="2" style="width:240px" />
        </el-form-item>
        <el-form-item :label="$t('settings.dropoffPrice')">
          <el-input-number v-model="form.dropoff_price" :min="0" :precision="2" style="width:240px" />
        </el-form-item>
        <el-form-item :label="$t('settings.comboDiscount')">
          <el-input-number v-model="form.combo_discount" :min="0" :max="100" :precision="0" style="width:240px" />
          <div style="font-size:12px;color:#8a7b6b;margin-top:4px">{{ $t('settings.comboTip') }}</div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '../api'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const form = reactive({
  pickup_price: 0,
  dropoff_price: 0,
  combo_discount: 0
})

async function loadData() {
  loading.value = true
  try {
    const res = await getSettings()
    const data = res.data
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      form.pickup_price = Number(data.pickup_price) || 0
      form.dropoff_price = Number(data.dropoff_price) || 0
      form.combo_discount = Number(data.combo_discount) || 0
    }
  } catch {}
  loading.value = false
}

async function onSave() {
  saving.value = true
  try {
    await updateSettings({
      pickup_price: String(form.pickup_price),
      dropoff_price: String(form.dropoff_price),
      combo_discount: String(form.combo_discount)
    })
    ElMessage.success(t('settings.settingsSaved'))
  } catch {}
  saving.value = false
}

onMounted(loadData)
</script>
