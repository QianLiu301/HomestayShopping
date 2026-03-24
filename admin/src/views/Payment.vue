<template>
  <div>
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>{{ $t('payment.qrCodes') }}</span>
          <el-button type="primary" :loading="savingQr" @click="onSaveQr">{{ $t('payment.saveQrCodes') }}</el-button>
        </div>
      </template>

      <el-form label-width="180px" v-loading="loading" style="max-width:700px">
        <el-form-item :label="$t('payment.wechatQr')">
          <div class="qr-upload-area">
            <el-upload
              :show-file-list="false"
              :http-request="(opts) => onUploadQr(opts, 'wechat')"
              accept="image/*"
            >
              <div v-if="form.wechat_qr_url" class="qr-preview">
                <img :src="resolveUrl(form.wechat_qr_url)" />
                <div class="qr-overlay">{{ $t('payment.clickToReplace') }}</div>
              </div>
              <div v-else class="qr-placeholder">
                <el-icon size="32"><Plus /></el-icon>
                <span>{{ $t('payment.uploadWechat') }}</span>
              </div>
            </el-upload>
            <el-button v-if="form.wechat_qr_url" link type="danger" @click="form.wechat_qr_url = ''">{{ $t('payment.remove') }}</el-button>
          </div>
        </el-form-item>

        <el-form-item :label="$t('payment.alipayQr')">
          <div class="qr-upload-area">
            <el-upload
              :show-file-list="false"
              :http-request="(opts) => onUploadQr(opts, 'alipay')"
              accept="image/*"
            >
              <div v-if="form.alipay_qr_url" class="qr-preview">
                <img :src="resolveUrl(form.alipay_qr_url)" />
                <div class="qr-overlay">{{ $t('payment.clickToReplace') }}</div>
              </div>
              <div v-else class="qr-placeholder">
                <el-icon size="32"><Plus /></el-icon>
                <span>{{ $t('payment.uploadAlipay') }}</span>
              </div>
            </el-upload>
            <el-button v-if="form.alipay_qr_url" link type="danger" @click="form.alipay_qr_url = ''">{{ $t('payment.remove') }}</el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <div style="font-size:12px;color:#8a7b6b;line-height:1.6">
            {{ $t('payment.qrTip') }}<br>
            {{ $t('payment.qrTip2') }}
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getSettings, updateSettings, uploadFile, resolveUrl } from '../api'

const { t } = useI18n()
const loading = ref(false)
const savingQr = ref(false)
const form = reactive({
  wechat_qr_url: '',
  alipay_qr_url: ''
})

async function loadData() {
  loading.value = true
  try {
    const res = await getSettings()
    const data = res.data
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      form.wechat_qr_url = data.wechat_qr_url || ''
      form.alipay_qr_url = data.alipay_qr_url || ''
    }
  } catch {}
  loading.value = false
}

async function onUploadQr(opts, type) {
  try {
    const res = await uploadFile(opts.file)
    const url = res.data?.url
    if (url) {
      if (type === 'wechat') form.wechat_qr_url = url
      else form.alipay_qr_url = url
      ElMessage.success(t('payment.imageUploaded'))
    }
  } catch {
    ElMessage.error(t('common.uploadFailed'))
  }
}

async function onSaveQr() {
  savingQr.value = true
  try {
    await updateSettings({
      wechat_qr_url: form.wechat_qr_url,
      alipay_qr_url: form.alipay_qr_url
    })
    ElMessage.success(t('payment.qrSaved'))
  } catch {}
  savingQr.value = false
}

onMounted(loadData)
</script>

<style scoped>
.qr-upload-area {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.qr-preview {
  width: 160px;
  height: 160px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.qr-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.qr-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  opacity: 0;
  transition: opacity 0.2s;
}

.qr-preview:hover .qr-overlay {
  opacity: 1;
}

.qr-placeholder {
  width: 160px;
  height: 160px;
  border: 2px dashed #d0d0d0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #999;
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.qr-placeholder:hover {
  border-color: #409eff;
  color: #409eff;
}
</style>
