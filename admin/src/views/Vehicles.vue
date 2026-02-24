<template>
  <div>
    <div class="page-header">
      <span></span>
      <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> Add Vehicle</el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="Image" width="80">
          <template #default="{ row }">
            <el-image v-if="row.image" :src="row.image" style="width:50px;height:50px;border-radius:8px" fit="cover" />
            <div v-else style="width:50px;height:50px;border-radius:8px;background:#f5efe6;display:flex;align-items:center;justify-content:center;font-size:20px">🚗</div>
          </template>
        </el-table-column>
        <el-table-column prop="name_en" label="Name (EN)" min-width="140" />
        <el-table-column prop="name_zh" label="Name (ZH)" min-width="120" />
        <el-table-column prop="seats" label="Seats" width="80" align="center" />
        <el-table-column prop="luggage_capacity" label="Luggage" width="90" align="center" />
        <el-table-column label="Extra Price" width="110">
          <template #default="{ row }">¥{{ row.extra_price || 0 }}</template>
        </el-table-column>
        <el-table-column prop="sort_order" label="Sort" width="70" />
        <el-table-column label="Status" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? 'Active' : 'Hidden' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">Edit</el-button>
            <el-popconfirm title="Delete this vehicle?" @confirm="onDelete(row.id)">
              <template #reference><el-button link type="danger">Delete</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Edit Vehicle' : 'Add Vehicle'" width="600px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="Name (EN)" required><el-input v-model="form.name_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Name (ZH)"><el-input v-model="form.name_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Name (RU)"><el-input v-model="form.name_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Name (ES)"><el-input v-model="form.name_es" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="Description (EN)"><el-input v-model="form.desc_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Description (ZH)"><el-input v-model="form.desc_zh" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="Seats" required><el-input-number v-model="form.seats" :min="1" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="Luggage Capacity" required><el-input-number v-model="form.luggage_capacity" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="Extra Price"><el-input-number v-model="form.extra_price" :min="0" :precision="2" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="Vehicle Image">
          <el-upload
            :file-list="fileList"
            :http-request="handleUpload"
            :on-remove="handleRemove"
            :before-upload="beforeUpload"
            :limit="1"
            list-type="picture-card"
            accept="image/*"
          >
            <el-icon v-if="!form.image"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="Sort Order"><el-input-number v-model="form.sort_order" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Status"><el-radio-group v-model="form.status"><el-radio :value="1">Active</el-radio><el-radio :value="0">Hidden</el-radio></el-radio-group></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getVehicles, createVehicle, updateVehicle, deleteVehicle, uploadFile } from '../api'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const fileList = ref([])

const defaultForm = () => ({ name_en: '', name_zh: '', name_ru: '', name_es: '', desc_en: '', desc_zh: '', seats: 4, luggage_capacity: 2, extra_price: 0, image: '', sort_order: 0, status: 1 })
const form = reactive(defaultForm())

async function loadData() {
  loading.value = true
  try { const res = await getVehicles(); list.value = res.data || [] } catch {}
  loading.value = false
}

function openDialog(row) {
  Object.assign(form, defaultForm())
  fileList.value = []
  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.keys(form).forEach(k => { if (row[k] !== undefined && row[k] !== null) form[k] = row[k] })
    if (row.image) {
      fileList.value = [{ name: 'vehicle-image', url: row.image }]
    }
  } else {
    isEdit.value = false
    editId.value = null
  }
  dialogVisible.value = true
}

function beforeUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isImage) { ElMessage.error('Only image files are allowed'); return false }
  if (!isLt10M) { ElMessage.error('Image must be less than 10MB'); return false }
  return true
}

async function handleUpload(options) {
  try {
    const res = await uploadFile(options.file)
    const url = res.data?.url
    if (url) { form.image = url; options.onSuccess(res) }
    else { options.onError(new Error('Upload failed')) }
  } catch (err) { options.onError(err) }
}

function handleRemove() {
  form.image = ''
}

async function onSave() {
  if (!form.name_en && !form.name_zh) return ElMessage.warning('Name is required')
  saving.value = true
  try {
    if (isEdit.value) { await updateVehicle(editId.value, form); ElMessage.success('Updated') }
    else { await createVehicle(form); ElMessage.success('Created') }
    dialogVisible.value = false; loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try { await deleteVehicle(id); ElMessage.success('Deleted'); loadData() } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
