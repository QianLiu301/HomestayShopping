<template>
  <div>
    <div class="page-header">
      <span></span>
      <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> {{ $t('vehicles.addVehicle') }}</el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column :label="$t('common.image')" width="80">
          <template #default="{ row }">
            <el-image v-if="row.image" :src="resolveUrl(row.image)" style="width:50px;height:50px;border-radius:8px" fit="cover" />
            <div v-else style="width:50px;height:50px;border-radius:8px;background:#f5efe6;display:flex;align-items:center;justify-content:center;font-size:20px">🚗</div>
          </template>
        </el-table-column>
        <el-table-column prop="name_zh" :label="$t('vehicles.nameZh')" min-width="130" />
        <el-table-column prop="model_zh" :label="$t('vehicles.modelZh')" min-width="160" />
        <el-table-column prop="seats" :label="$t('vehicles.seats')" width="80" align="center" />
        <el-table-column :label="$t('vehicles.capacityDescZh')" min-width="160">
          <template #default="{ row }">
            {{ row.capacity_desc_zh || row.capacity_desc || '-' }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('vehicles.imageCount')" width="90" align="center">
          <template #default="{ row }">
            {{ row.images?.length || (row.image ? 1 : 0) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('vehicles.extraPrice')" width="110">
          <template #default="{ row }">¥{{ row.extra_price || 0 }}</template>
        </el-table-column>
        <el-table-column prop="sort_order" :label="$t('common.sort')" width="70" />
        <el-table-column :label="$t('common.status')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? $t('common.active') : $t('common.hidden') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">{{ $t('common.edit') }}</el-button>
            <el-popconfirm :title="$t('vehicles.deleteConfirm')" @confirm="onDelete(row.id)">
              <template #reference><el-button link type="danger">{{ $t('common.delete') }}</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? $t('vehicles.editVehicle') : $t('vehicles.addVehicle')" width="900px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <div class="section-title">{{ $t('vehicles.tierInfo') }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="$t('vehicles.nameEn')" required><el-input v-model="form.name_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('vehicles.nameZh')"><el-input v-model="form.name_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('vehicles.nameRu')"><el-input v-model="form.name_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('vehicles.nameEs')"><el-input v-model="form.name_es" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ $t('vehicles.modelInfo') }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="$t('vehicles.modelEn')"><el-input v-model="form.model_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('vehicles.modelZh')"><el-input v-model="form.model_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('vehicles.modelRu')"><el-input v-model="form.model_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('vehicles.modelEs')"><el-input v-model="form.model_es" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ $t('vehicles.displayInfo') }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="$t('vehicles.descEn')"><el-input v-model="form.desc_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('vehicles.descZh')"><el-input v-model="form.desc_zh" /></el-form-item></el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="8"><el-form-item :label="$t('vehicles.seats')" required><el-input-number v-model="form.seats" :min="1" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('vehicles.luggage28')"><el-input-number v-model="form.luggage_28" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('vehicles.luggage24')"><el-input-number v-model="form.luggage_24" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="$t('vehicles.capacityDescEn')"><el-input v-model="form.capacity_desc_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('vehicles.capacityDescZh')"><el-input v-model="form.capacity_desc_zh" /></el-form-item></el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="8"><el-form-item :label="$t('vehicles.luggage')"><el-input-number v-model="form.luggage_capacity" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('vehicles.extraPrice')"><el-input-number v-model="form.extra_price" :min="0" :precision="2" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('common.sort')"><el-input-number v-model="form.sort_order" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ $t('vehicles.imageGallery') }}</div>
        <el-form-item :label="$t('vehicles.vehicleImages')">
          <el-upload
            :file-list="fileList"
            list-type="picture-card"
            :http-request="handleUpload"
            :before-upload="beforeUpload"
            :on-remove="handleRemove"
            multiple
            accept="image/*"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="field-tip">{{ $t('vehicles.uploadTip') }}</div>
          <div class="field-tip warning">{{ $t('vehicles.renderUploadWarning') }}</div>
        </el-form-item>

        <div v-if="form.images.length" class="gallery-grid">
          <div
            v-for="(img, index) in form.images"
            :key="`${img}-${index}`"
            class="gallery-item"
            :class="{ active: index === 0 }"
          >
            <el-image :src="resolveUrl(img)" fit="cover" class="gallery-image" />
            <div class="gallery-actions">
              <el-button size="small" @click="setPrimary(index)">{{ index === 0 ? $t('vehicles.coverImage') : $t('vehicles.setAsCover') }}</el-button>
              <el-button size="small" type="danger" @click="removeImage(index)">{{ $t('common.delete') }}</el-button>
            </div>
          </div>
        </div>

        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="$t('common.status')"><el-radio-group v-model="form.status"><el-radio :value="1">{{ $t('common.active') }}</el-radio><el-radio :value="0">{{ $t('common.hidden') }}</el-radio></el-radio-group></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving || uploading" :disabled="uploading" @click="onSave">{{ $t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getVehicles, createVehicle, updateVehicle, deleteVehicle, uploadFile, resolveUrl } from '../api'

const { t } = useI18n()
const list = ref([])
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const fileList = ref([])

const defaultForm = () => ({
  name_en: '', name_zh: '', name_ru: '', name_es: '',
  desc_en: '', desc_zh: '', desc_ru: '', desc_es: '',
  model_en: '', model_zh: '', model_ru: '', model_es: '',
  seats: 5,
  luggage_capacity: 0,
  luggage_28: 0,
  luggage_24: 0,
  capacity_desc_en: '', capacity_desc_zh: '', capacity_desc_ru: '', capacity_desc_es: '',
  extra_price: 0,
  image: '',
  images: [],
  sort_order: 0,
  status: 1
})
const form = reactive(defaultForm())

watch(() => [form.luggage_28, form.luggage_24], ([size28, size24]) => {
  form.luggage_capacity = Number(size28 || 0) + Number(size24 || 0)
})

async function loadData() {
  loading.value = true
  try { const res = await getVehicles(); list.value = res.data || [] } catch {}
  loading.value = false
}

function syncFileList() {
  fileList.value = (form.images || []).map((img, index) => ({
    name: `vehicle-${index + 1}`,
    url: resolveUrl(img),
    uid: `${img}-${index}`
  }))
}

function openDialog(row) {
  Object.assign(form, defaultForm())
  fileList.value = []
  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.keys(form).forEach(k => { if (row[k] !== undefined && row[k] !== null) form[k] = row[k] })
    form.images = Array.isArray(row.images) && row.images.length ? [...row.images] : (row.image ? [row.image] : [])
    form.image = form.images[0] || ''
    syncFileList()
  } else {
    isEdit.value = false
    editId.value = null
  }
  dialogVisible.value = true
}

function beforeUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isImage) { ElMessage.error(t('products.imageError')); return false }
  if (!isLt10M) { ElMessage.error(t('products.imageSizeError')); return false }
  return true
}

async function handleUpload(options) {
  uploading.value = true
  try {
    const res = await uploadFile(options.file)
    const url = res.data?.url
    if (!url) throw new Error(t('common.uploadFailed'))
    form.images.push(url)
    form.image = form.images[0] || ''
    syncFileList()
    options.onSuccess?.(res)
  } catch (err) {
    options.onError?.(err)
  } finally {
    uploading.value = false
  }
}

function handleRemove(file) {
  const target = (file.url || '').replace(resolveUrl(''), '')
  const index = form.images.findIndex(img => resolveUrl(img) === file.url || img === target)
  if (index >= 0) removeImage(index)
}

function removeImage(index) {
  form.images.splice(index, 1)
  form.image = form.images[0] || ''
  syncFileList()
}

function setPrimary(index) {
  if (index <= 0) return
  const [selected] = form.images.splice(index, 1)
  form.images.unshift(selected)
  form.image = form.images[0] || ''
  syncFileList()
}

async function onSave() {
  if (!form.name_en && !form.name_zh) return ElMessage.warning(t('common.nameRequired'))
  form.image = form.images[0] || ''
  saving.value = true
  try {
    const payload = {
      ...form,
      images: [...form.images],
      image: form.images[0] || ''
    }
    if (isEdit.value) { await updateVehicle(editId.value, payload); ElMessage.success(t('common.updated')) }
    else { await createVehicle(payload); ElMessage.success(t('common.created')) }
    dialogVisible.value = false; loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try { await deleteVehicle(id); ElMessage.success(t('common.deleted')); loadData() } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; margin-bottom: 16px; }
.section-title {
  margin: 4px 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: #8b6f47;
}
.field-tip {
  margin-top: 6px;
  font-size: 12px;
  color: #999;
  line-height: 1.5;
}
.field-tip.warning {
  color: #e6a23c;
}
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin: 8px 0 16px;
}
.gallery-item {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 10px;
  background: #fff;
}
.gallery-item.active {
  border-color: #409eff;
  box-shadow: 0 0 0 1px rgba(64, 158, 255, 0.15);
}
.gallery-image {
  width: 100%;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
}
.gallery-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
</style>
