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
          <div style="font-size:12px;color:#1a73e8;margin-top:2px">
            {{ $t('settings.comboPreview') }}: ¥{{ comboPreview }}
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Contact Settings -->
    <el-card shadow="hover" style="margin-top:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>{{ $t('settings.contactSettings') }}</span>
          <el-button type="primary" :loading="savingContact" @click="onSaveContact">{{ $t('settings.saveChanges') }}</el-button>
        </div>
      </template>

      <p style="font-size:13px;color:#8a7b6b;margin:0 0 20px">{{ $t('settings.contactTip') }}</p>

      <el-form :model="contactForm" label-width="180px" v-loading="loading" style="max-width:700px">
        <el-form-item :label="$t('settings.wechatId')">
          <el-input v-model="contactForm.contact_wechat_id" :placeholder="$t('settings.wechatIdPlaceholder')" style="width:300px" />
        </el-form-item>
        <el-form-item :label="$t('settings.wechatQr')">
          <div class="qr-upload-area">
            <div v-if="contactForm.contact_wechat_qr" class="qr-preview">
              <el-image :src="contactForm.contact_wechat_qr" style="width:160px;height:160px;border-radius:8px" fit="contain" :preview-src-list="[contactForm.contact_wechat_qr]" />
              <div class="qr-actions">
                <el-button size="small" @click="triggerUpload('wechat')">{{ $t('settings.clickToReplace') }}</el-button>
                <el-button size="small" type="danger" @click="contactForm.contact_wechat_qr = ''">{{ $t('settings.remove') }}</el-button>
              </div>
            </div>
            <el-button v-else @click="triggerUpload('wechat')" :loading="uploadingWechat">
              {{ $t('settings.uploadWechatQr') }}
            </el-button>
          </div>
        </el-form-item>

        <el-divider />

        <el-form-item :label="$t('settings.whatsapp')">
          <el-input v-model="contactForm.contact_whatsapp" :placeholder="$t('settings.whatsappPlaceholder')" style="width:300px" />
        </el-form-item>
        <el-form-item :label="$t('settings.whatsappQr')">
          <div class="qr-upload-area">
            <div v-if="contactForm.contact_whatsapp_qr" class="qr-preview">
              <el-image :src="contactForm.contact_whatsapp_qr" style="width:160px;height:160px;border-radius:8px" fit="contain" :preview-src-list="[contactForm.contact_whatsapp_qr]" />
              <div class="qr-actions">
                <el-button size="small" @click="triggerUpload('whatsapp')">{{ $t('settings.clickToReplace') }}</el-button>
                <el-button size="small" type="danger" @click="contactForm.contact_whatsapp_qr = ''">{{ $t('settings.remove') }}</el-button>
              </div>
            </div>
            <el-button v-else @click="triggerUpload('whatsapp')" :loading="uploadingWhatsapp">
              {{ $t('settings.uploadWhatsappQr') }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileChange" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings, uploadFile } from '../api'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const savingContact = ref(false)
const uploadingWechat = ref(false)
const uploadingWhatsapp = ref(false)
const uploadTarget = ref('') // 'wechat' or 'whatsapp'
const fileInput = ref(null)

const form = reactive({
  pickup_price: 0,
  dropoff_price: 0,
  combo_discount: 0
})

const contactForm = reactive({
  contact_wechat_id: '',
  contact_whatsapp: '',
  contact_wechat_qr: '',
  contact_whatsapp_qr: ''
})

const comboPreview = computed(() => {
  const total = form.pickup_price + form.dropoff_price
  return Math.round(total * (1 - form.combo_discount / 100) * 100) / 100
})

function triggerUpload(target) {
  uploadTarget.value = target
  fileInput.value?.click()
}

async function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const target = uploadTarget.value
  if (target === 'wechat') uploadingWechat.value = true
  else uploadingWhatsapp.value = true

  try {
    const res = await uploadFile(file)
    const url = res.data?.url || ''
    if (target === 'wechat') {
      contactForm.contact_wechat_qr = url
    } else {
      contactForm.contact_whatsapp_qr = url
    }
  } catch {
    ElMessage.error(t('common.uploadFailed'))
  } finally {
    uploadingWechat.value = false
    uploadingWhatsapp.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function loadData() {
  loading.value = true
  try {
    const res = await getSettings()
    const data = res.data
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      form.pickup_price = Number(data.pickup_price) || 0
      form.dropoff_price = Number(data.dropoff_price) || 0
      form.combo_discount = Number(data.combo_discount) || 0
      contactForm.contact_wechat_id = data.contact_wechat_id || ''
      contactForm.contact_whatsapp = data.contact_whatsapp || ''
      contactForm.contact_wechat_qr = data.contact_wechat_qr || ''
      contactForm.contact_whatsapp_qr = data.contact_whatsapp_qr || ''
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

async function onSaveContact() {
  savingContact.value = true
  try {
    await updateSettings({
      contact_wechat_id: contactForm.contact_wechat_id,
      contact_whatsapp: contactForm.contact_whatsapp,
      contact_wechat_qr: contactForm.contact_wechat_qr,
      contact_whatsapp_qr: contactForm.contact_whatsapp_qr
    })
    ElMessage.success(t('settings.contactSaved'))
  } catch {}
  savingContact.value = false
}

onMounted(loadData)
</script>

<style scoped>
.qr-upload-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.qr-preview {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.qr-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
