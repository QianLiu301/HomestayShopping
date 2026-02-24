<template>
  <div>
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>Transfer Pricing Settings</span>
          <el-button type="primary" :loading="saving" @click="onSave">Save Changes</el-button>
        </div>
      </template>

      <el-form :model="form" label-width="180px" v-loading="loading" style="max-width:600px">
        <el-form-item label="Pickup Price (¥)">
          <el-input-number v-model="form.pickup_price" :min="0" :precision="2" style="width:240px" />
        </el-form-item>
        <el-form-item label="Dropoff Price (¥)">
          <el-input-number v-model="form.dropoff_price" :min="0" :precision="2" style="width:240px" />
        </el-form-item>
        <el-form-item label="Combo Discount (%)">
          <el-input-number v-model="form.combo_discount" :min="0" :max="100" :precision="0" style="width:240px" />
          <div style="font-size:12px;color:#8a7b6b;margin-top:4px">Combo price = (pickup + dropoff) × (1 - discount%/100)</div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '../api'

const loading = ref(false)
const saving = ref(false)
const form = reactive({ pickup_price: 0, dropoff_price: 0, combo_discount: 0 })

async function loadData() {
  loading.value = true
  try {
    const res = await getSettings()
    const settings = res.data || []
    if (Array.isArray(settings)) {
      settings.forEach(s => {
        if (s.key === 'pickup_price') form.pickup_price = Number(s.value) || 0
        if (s.key === 'dropoff_price') form.dropoff_price = Number(s.value) || 0
        if (s.key === 'combo_discount') form.combo_discount = Number(s.value) || 0
      })
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
    ElMessage.success('Settings saved')
  } catch {}
  saving.value = false
}

onMounted(loadData)
</script>
