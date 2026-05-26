<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input
          v-model="keyword"
          :placeholder="$t('wishes.searchPlaceholder')"
          clearable
          style="width:280px"
          @keyup.enter="loadData(1)"
          @clear="loadData(1)"
        >
          <template #append>
            <el-button :icon="Search" @click="loadData(1)" />
          </template>
        </el-input>
        <el-select
          v-model="statusFilter"
          :placeholder="$t('wishes.statusAll')"
          clearable
          style="width:140px"
          @change="loadData(1)"
        >
          <el-option :label="$t('wishes.status.pending')" :value="0" />
          <el-option :label="$t('wishes.status.contacted')" :value="1" />
          <el-option :label="$t('wishes.status.completed')" :value="2" />
          <el-option :label="$t('wishes.status.closed')" :value="3" />
        </el-select>
      </div>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column :label="$t('wishes.name')" width="120">
          <template #default="{ row }">{{ row.contact_name }}</template>
        </el-table-column>
        <el-table-column :label="$t('wishes.contact')" width="200">
          <template #default="{ row }">
            <div v-if="row.contact_phone" style="font-size:13px">{{ row.contact_phone }}</div>
            <div v-if="row.contact_email" style="font-size:12px;color:#666">{{ row.contact_email }}</div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('wishes.content')" min-width="280">
          <template #default="{ row }">
            <div class="content-cell">{{ row.content }}</div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('wishes.expectedDate')" width="160">
          <template #default="{ row }">{{ formatDateTime(row.expected_date) }}</template>
        </el-table-column>
        <el-table-column :label="$t('wishes.budget')" width="120">
          <template #default="{ row }">
            <span v-if="row.budget != null">
              {{ row.budget_currency === 'USD' ? '$' : '¥' }}{{ row.budget }}
            </span>
            <span v-else style="color:#aaa">-</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('wishes.lang')" width="70">
          <template #default="{ row }">{{ row.lang || '-' }}</template>
        </el-table-column>
        <el-table-column :label="$t('wishes.statusCol')" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('wishes.createdAt')" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">{{ $t('common.manage') }}</el-button>
            <el-button link type="danger" @click="onDelete(row)">{{ $t('common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadData()"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="$t('wishes.detailTitle')" width="600px">
      <el-descriptions :column="1" border v-if="current">
        <el-descriptions-item label="ID">#{{ current.id }}</el-descriptions-item>
        <el-descriptions-item :label="$t('wishes.name')">{{ current.contact_name }}</el-descriptions-item>
        <el-descriptions-item :label="$t('wishes.contact')">
          <div v-if="current.contact_phone">📞 {{ current.contact_phone }}</div>
          <div v-if="current.contact_email">✉️ {{ current.contact_email }}</div>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('wishes.expectedDate')">
          {{ formatDateTime(current.expected_date) }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('wishes.budget')">
          <span v-if="current.budget != null">
            {{ current.budget_currency === 'USD' ? '$' : '¥' }}{{ current.budget }}
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('wishes.content')">
          <div style="white-space:pre-wrap; line-height:1.7">{{ current.content }}</div>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('wishes.createdAt')">
          {{ formatDateTime(current.created_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <div style="margin-top:20px">
        <div style="margin-bottom:8px;font-weight:600">{{ $t('wishes.updateStatus') }}</div>
        <el-radio-group v-model="editStatus">
          <el-radio :value="0">{{ $t('wishes.status.pending') }}</el-radio>
          <el-radio :value="1">{{ $t('wishes.status.contacted') }}</el-radio>
          <el-radio :value="2">{{ $t('wishes.status.completed') }}</el-radio>
          <el-radio :value="3">{{ $t('wishes.status.closed') }}</el-radio>
        </el-radio-group>
      </div>

      <div style="margin-top:16px">
        <div style="margin-bottom:8px;font-weight:600">{{ $t('wishes.noteLabel') }}</div>
        <el-input
          v-model="editNote"
          type="textarea"
          :rows="3"
          :placeholder="$t('wishes.notePlaceholder')"
        />
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="onSave" :loading="saving">
          {{ $t('wishes.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { getWishes, updateWish, deleteWish } from '../api'

const { t } = useI18n()

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const keyword = ref('')
const statusFilter = ref('')

const dialogVisible = ref(false)
const current = ref(null)
const editStatus = ref(0)
const editNote = ref('')
const saving = ref(false)

function formatDateTime(s) {
  if (!s) return '-'
  const d = new Date(s)
  if (isNaN(d.getTime())) return s
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function statusLabel(s) {
  return {
    0: t('wishes.status.pending'),
    1: t('wishes.status.contacted'),
    2: t('wishes.status.completed'),
    3: t('wishes.status.closed'),
  }[s] || '-'
}

function statusTagType(s) {
  return { 0: 'warning', 1: 'primary', 2: 'success', 3: 'info' }[s] || ''
}

async function loadData(p) {
  if (p) page.value = p
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize }
    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    if (statusFilter.value !== '' && statusFilter.value !== null) {
      params.status = statusFilter.value
    }
    const res = await getWishes(params)
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Load failed')
  } finally {
    loading.value = false
  }
}

function openDetail(row) {
  current.value = row
  editStatus.value = row.status
  editNote.value = row.admin_note || ''
  dialogVisible.value = true
}

async function onSave() {
  if (!current.value) return
  saving.value = true
  try {
    await updateWish(current.value.id, {
      status: editStatus.value,
      admin_note: editNote.value,
    })
    ElMessage.success(t('wishes.updated'))
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Save failed')
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(t('wishes.deleteConfirm'), '', {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    await deleteWish(row.id)
    ElMessage.success(t('wishes.deleted'))
    await loadData()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Delete failed')
  }
}

onMounted(() => loadData(1))
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.header-filters {
  display: flex;
  gap: 12px;
  align-items: center;
}
.content-cell {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
  font-size: 13px;
  color: #444;
}
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
