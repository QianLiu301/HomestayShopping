<template>
  <div>
    <div class="page-header">
      <span></span>
      <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> Add Location</el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name_en" label="Name (EN)" min-width="160" />
        <el-table-column prop="name_zh" label="Name (ZH)" min-width="120" />
        <el-table-column prop="district" label="District" width="120" />
        <el-table-column prop="address_en" label="Address" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="Sort" width="70" />
        <el-table-column label="Status" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? 'Active' : 'Hidden' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">Edit</el-button>
            <el-popconfirm title="Delete this location?" @confirm="onDelete(row.id)">
              <template #reference><el-button link type="danger">Delete</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Edit Location' : 'Add Location'" width="600px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="Name (EN)" required><el-input v-model="form.name_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Name (ZH)"><el-input v-model="form.name_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Name (RU)"><el-input v-model="form.name_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Name (ES)"><el-input v-model="form.name_es" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="Address (EN)"><el-input v-model="form.address_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="Address (ZH)"><el-input v-model="form.address_zh" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="District"><el-input v-model="form.district" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="Sort Order"><el-input-number v-model="form.sort_order" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="Status"><el-radio-group v-model="form.status"><el-radio :value="1">Active</el-radio><el-radio :value="0">Hidden</el-radio></el-radio-group></el-form-item></el-col>
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
import { getLocations, createLocation, updateLocation, deleteLocation } from '../api'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)

const defaultForm = () => ({ name_en: '', name_zh: '', name_ru: '', name_es: '', address_en: '', address_zh: '', district: '', sort_order: 0, status: 1 })
const form = reactive(defaultForm())

async function loadData() {
  loading.value = true
  try { const res = await getLocations(); list.value = res.data || [] } catch {}
  loading.value = false
}

function openDialog(row) {
  Object.assign(form, defaultForm())
  if (row) { isEdit.value = true; editId.value = row.id; Object.keys(form).forEach(k => { if (row[k] !== undefined) form[k] = row[k] }) }
  else { isEdit.value = false; editId.value = null }
  dialogVisible.value = true
}

async function onSave() {
  if (!form.name_en && !form.name_zh) return ElMessage.warning('Name is required')
  saving.value = true
  try {
    if (isEdit.value) { await updateLocation(editId.value, form); ElMessage.success('Updated') }
    else { await createLocation(form); ElMessage.success('Created') }
    dialogVisible.value = false; loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try { await deleteLocation(id); ElMessage.success('Deleted'); loadData() } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
