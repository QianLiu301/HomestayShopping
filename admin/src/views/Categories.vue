<template>
  <div>
    <div class="page-header">
      <span></span>
      <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> {{ $t('categories.addCategory') }}</el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name_zh" :label="$t('categories.nameZh')" />
        <el-table-column prop="name_en" :label="$t('categories.nameEn')" />
        <el-table-column prop="icon" :label="$t('categories.icon')" width="80" />
        <el-table-column prop="sort_order" :label="$t('common.sort')" width="80" />
        <el-table-column :label="$t('common.status')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? $t('common.active') : $t('common.hidden') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">{{ $t('common.edit') }}</el-button>
            <el-popconfirm :title="$t('categories.deleteConfirm')" @confirm="onDelete(row.id)">
              <template #reference><el-button link type="danger">{{ $t('common.delete') }}</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? $t('categories.editCategory') : $t('categories.addCategory')" width="500px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="$t('categories.nameEn')" required><el-input v-model="form.name_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('categories.nameZh')"><el-input v-model="form.name_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('categories.nameRu')"><el-input v-model="form.name_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('categories.nameEs')"><el-input v-model="form.name_es" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item :label="$t('categories.icon')"><el-input v-model="form.icon" placeholder="e.g. 🎁" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('common.sort')"><el-input-number v-model="form.sort_order" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('common.status')"><el-radio-group v-model="form.status"><el-radio :value="1">{{ $t('common.active') }}</el-radio><el-radio :value="0">{{ $t('common.hidden') }}</el-radio></el-radio-group></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">{{ $t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../api'

const { t } = useI18n()
const list = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)

const defaultForm = () => ({ name_en: '', name_zh: '', name_ru: '', name_es: '', icon: '', sort_order: 0, status: 1 })
const form = reactive(defaultForm())

async function loadData() {
  loading.value = true
  try { const res = await getCategories(); list.value = res.data || [] } catch {}
  loading.value = false
}

function openDialog(row) {
  Object.assign(form, defaultForm())
  if (row) { isEdit.value = true; editId.value = row.id; Object.keys(form).forEach(k => { if (row[k] !== undefined) form[k] = row[k] }) }
  else { isEdit.value = false; editId.value = null }
  dialogVisible.value = true
}

async function onSave() {
  if (!form.name_zh) return ElMessage.warning('请填写中文分类名称')
  saving.value = true
  try {
    if (isEdit.value) { await updateCategory(editId.value, form); ElMessage.success(t('common.updated')) }
    else { await createCategory(form); ElMessage.success(t('common.created')) }
    dialogVisible.value = false; loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try { await deleteCategory(id); ElMessage.success(t('common.deleted')); loadData() } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; margin-bottom: 16px; }
</style>
