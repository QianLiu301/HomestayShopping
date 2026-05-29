<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input
          v-model="keyword"
          :placeholder="$t('reviews.searchPlaceholder')"
          clearable
          style="width: 240px"
          @keyup.enter="loadData(1)"
          @clear="loadData(1)"
        >
          <template #append>
            <el-button :icon="Search" @click="loadData(1)" />
          </template>
        </el-input>

        <el-select v-model="orderType" :placeholder="$t('reviews.typeAll')" clearable style="width: 140px" @change="loadData(1)">
          <el-option :label="$t('reviews.typeShop')" value="shop" />
          <el-option :label="$t('reviews.typeTransfer')" value="transfer" />
          <el-option :label="$t('reviews.typeTicket')" value="ticket" />
        </el-select>

        <el-select v-model="ratingFilter" :placeholder="$t('reviews.ratingAll')" clearable style="width: 120px" @change="loadData(1)">
          <el-option v-for="n in 5" :key="n" :label="`${n} ⭐`" :value="n" />
        </el-select>

        <el-select v-model="statusFilter" :placeholder="$t('reviews.statusAll')" clearable style="width: 130px" @change="loadData(1)">
          <el-option :label="$t('reviews.statusVisible')" :value="0" />
          <el-option :label="$t('reviews.statusHidden')" :value="1" />
        </el-select>
      </div>

      <div v-if="overall.total > 0" class="overall-badge">
        {{ $t('reviews.overall', { count: overall.total, avg: overall.avg_rating || '-' }) }}
      </div>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column :label="$t('reviews.type')" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="typeTagColor(row.order_type)">
              {{ typeLabel(row.order_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('reviews.rating')" width="170">
          <template #default="{ row }">
            <el-rate :model-value="row.rating" disabled size="small" />
          </template>
        </el-table-column>
        <el-table-column :label="$t('reviews.customer')" width="110">
          <template #default="{ row }">{{ row.reviewer_name || '-' }}</template>
        </el-table-column>
        <el-table-column :label="$t('reviews.content')" min-width="280">
          <template #default="{ row }">
            <div class="comment-cell">{{ row.comment || '—' }}</div>
            <div v-if="row.admin_reply" class="reply-cell">
              <el-tag size="small" type="warning">回复</el-tag>
              {{ row.admin_reply }}
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('reviews.orderNo')" width="170">
          <template #default="{ row }">
            <span style="font-size: 12px; color: #666">{{ row.order_no || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('reviews.status')" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 0 ? 'success' : 'info'">
              {{ row.status === 0 ? $t('reviews.statusVisible') : $t('reviews.statusHidden') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('reviews.createdAt')" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">{{ $t('common.manage') }}</el-button>
            <el-button v-if="row.status === 0" link type="warning" @click="toggleStatus(row, 1)">{{ $t('reviews.hide') }}</el-button>
            <el-button v-else link type="success" @click="toggleStatus(row, 0)">{{ $t('reviews.show') }}</el-button>
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

    <el-dialog v-model="dialogVisible" :title="$t('reviews.detailTitle')" width="600px">
      <el-descriptions :column="1" border v-if="current">
        <el-descriptions-item label="ID">#{{ current.id }}</el-descriptions-item>
        <el-descriptions-item :label="$t('reviews.type')">
          <el-tag size="small" :type="typeTagColor(current.order_type)">{{ typeLabel(current.order_type) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('reviews.orderNo')">{{ current.order_no || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('reviews.customer')">{{ current.reviewer_name || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('reviews.rating')">
          <el-rate :model-value="current.rating" disabled />
        </el-descriptions-item>
        <el-descriptions-item :label="$t('reviews.content')">
          <div style="white-space: pre-wrap; line-height: 1.7">{{ current.comment || '—' }}</div>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('reviews.createdAt')">
          {{ formatDateTime(current.created_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <div style="margin-top: 20px">
        <div style="margin-bottom: 8px; font-weight: 600">{{ $t('reviews.reply') }}</div>
        <el-input
          v-model="editReply"
          type="textarea"
          :rows="4"
          maxlength="1000"
          show-word-limit
          :placeholder="$t('reviews.replyPlaceholder')"
        />
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="onSaveReply" :loading="saving">
          {{ $t('reviews.saveReply') }}
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
import { getAdminReviews, updateReview, deleteReview } from '../api'

const { t } = useI18n()

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const keyword = ref('')
const orderType = ref('')
const ratingFilter = ref(null)
const statusFilter = ref('')
const overall = ref({ total: 0, avg_rating: null })

const dialogVisible = ref(false)
const current = ref(null)
const editReply = ref('')
const saving = ref(false)

function typeLabel(type) {
  return {
    shop: t('reviews.typeShop'),
    transfer: t('reviews.typeTransfer'),
    ticket: t('reviews.typeTicket'),
  }[type] || type
}
function typeTagColor(type) {
  return { shop: 'success', transfer: 'warning', ticket: 'danger' }[type] || ''
}

function formatDateTime(s) {
  if (!s) return '-'
  const d = new Date(s)
  if (isNaN(d.getTime())) return s
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadData(p) {
  if (p) page.value = p
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize }
    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    if (orderType.value) params.order_type = orderType.value
    if (ratingFilter.value) params.rating = ratingFilter.value
    if (statusFilter.value !== '' && statusFilter.value !== null) params.status = statusFilter.value

    const res = await getAdminReviews(params)
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
    overall.value = res.data?.overall || { total: 0, avg_rating: null }
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Load failed')
  } finally {
    loading.value = false
  }
}

function openDetail(row) {
  current.value = row
  editReply.value = row.admin_reply || ''
  dialogVisible.value = true
}

async function toggleStatus(row, newStatus) {
  try {
    await updateReview(row.id, { status: newStatus })
    ElMessage.success(t('reviews.saved'))
    row.status = newStatus
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Failed')
  }
}

async function onSaveReply() {
  if (!current.value) return
  saving.value = true
  try {
    await updateReview(current.value.id, { admin_reply: editReply.value })
    ElMessage.success(t('reviews.saved'))
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Failed')
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(t('reviews.deleteConfirm'), '', {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    })
  } catch { return }
  try {
    await deleteReview(row.id)
    ElMessage.success(t('reviews.deleted'))
    await loadData()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Failed')
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
  flex-wrap: wrap;
  gap: 12px;
}
.header-filters {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.overall-badge {
  font-size: 13px;
  color: #8a6635;
  background: #fff7e6;
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 600;
}
.comment-cell {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
  font-size: 13px;
  color: #444;
}
.reply-cell {
  margin-top: 6px;
  font-size: 12px;
  color: #8a6635;
  line-height: 1.5;
}
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
