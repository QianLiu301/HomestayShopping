<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input v-model="keyword" :placeholder="$t('refund.searchPlaceholder')" clearable style="width:240px" @keyup.enter="loadData" @clear="loadData">
          <template #append>
            <el-button :icon="Search" @click="loadData" />
          </template>
        </el-input>
        <el-select v-model="refundStatusFilter" :placeholder="$t('refund.refundStatus')" clearable style="width:130px" @change="loadData">
          <el-option :label="$t('refund.noRefundNeeded')" :value="0" />
          <el-option :label="$t('refund.pendingRefund')" :value="1" />
          <el-option :label="$t('refund.refunded')" :value="2" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" :start-placeholder="$t('orders.dateStart')" :end-placeholder="$t('orders.dateEnd')" value-format="YYYY-MM-DD" style="width:260px" @change="loadData" clearable />
        <el-dropdown @command="onQuickDate" style="margin-left:4px">
          <el-button><el-icon><Calendar /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="today">{{ $t('refund.today') }}</el-dropdown-item>
              <el-dropdown-item command="yesterday">{{ $t('refund.yesterday') }}</el-dropdown-item>
              <el-dropdown-item command="7d">{{ $t('refund.last7days') }}</el-dropdown-item>
              <el-dropdown-item command="30d">{{ $t('refund.last30days') }}</el-dropdown-item>
              <el-dropdown-item command="3m">{{ $t('orders.recent3m') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Download" @click="onExport">
          {{ $t('refund.exportCsv') }}
        </el-button>
      </div>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="cancelled_at" :label="$t('refund.cancelledAt')" width="170">
          <template #default="{ row }">{{ formatDateTime(row.cancelled_at || row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="order_type" :label="$t('refund.orderType')" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.order_type === 'shop' ? 'success' : 'primary'">{{ row.service_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_no" :label="$t('orders.orderNo')" width="190" />
        <el-table-column prop="contact_name" :label="$t('orders.customer')" width="120" />
        <el-table-column :label="$t('refund.contact')" width="180">
          <template #default="{ row }">
            <div style="font-size:12px">
              <div v-if="row.contact_phone">📱 {{ row.contact_phone }}</div>
              <div v-if="row.contact_email">✉️ {{ row.contact_email }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('orders.total')" width="100">
          <template #default="{ row }">¥{{ row.total_price }}</template>
        </el-table-column>
        <el-table-column :label="$t('refund.refundAmount')" width="100">
          <template #default="{ row }">
            <span v-if="row.refund_amount !== null && row.refund_amount !== undefined">¥{{ row.refund_amount }}</span>
            <span v-else style="color:#999">-</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('orders.payment')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.payment_status === 1 ? 'success' : 'info'" size="small">
              {{ row.payment_status === 1 ? $t('orders.paid') : $t('orders.unpaid') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('refund.refundStatus')" width="110">
          <template #default="{ row }">
            <el-tag :type="refundStatusTypes[row.refund_status || 0]" size="small">
              {{ refundStatusLabel(row.refund_status || 0) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('orders.remark')" min-width="150">
          <template #default="{ row }">{{ row.remark || '-' }}</template>
        </el-table-column>
        <el-table-column :label="$t('refund.actions')" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="onEditRefund(row)">
              {{ $t('refund.editRefund') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
      </div>
    </el-card>

    <!-- 退款状态编辑对话框 -->
    <el-dialog v-model="editDialogVisible" :title="$t('refund.editRefundStatus')" width="500px">
      <el-form :model="editForm" label-width="120px">
        <el-form-item :label="$t('refund.orderNo')">
          <el-input v-model="editForm.order_no" disabled />
        </el-form-item>
        <el-form-item :label="$t('refund.refundStatus')">
          <el-select v-model="editForm.refund_status" style="width:100%">
            <el-option :label="$t('refund.noRefundNeeded')" :value="0" />
            <el-option :label="$t('refund.pendingRefund')" :value="1" />
            <el-option :label="$t('refund.refunded')" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('refund.refundAmount')">
          <el-input-number v-model="editForm.refund_amount" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item :label="$t('orders.remark')">
          <el-input v-model="editForm.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">{{ $t('refund.cancel') }}</el-button>
        <el-button type="primary" @click="onSaveRefund">{{ $t('refund.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Search, Calendar, Download } from '@element-plus/icons-vue'
import { getCancelledOrders, exportCancelledOrdersUrl, updateRefundStatus } from '../api'

const { t } = useI18n()
const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 15
const total = ref(0)
const keyword = ref('')
const refundStatusFilter = ref('')
const dateRange = ref(null)

function formatDateTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  if (isNaN(d.getTime())) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const refundStatusTypes = { 0: 'info', 1: 'warning', 2: 'success' }
const refundStatusLabel = s => t(`refund.${['noRefundNeeded','pendingRefund','refunded'][s] || 'unknown'}`)

function onQuickDate(cmd) {
  const now = new Date()
  const today = now.toISOString().slice(0, 10)
  
  if (cmd === 'today') {
    dateRange.value = [today, today]
  } else if (cmd === 'yesterday') {
    const yesterday = new Date(now)
    yesterday.setDate(yesterday.getDate() - 1)
    const yesterdayStr = yesterday.toISOString().slice(0, 10)
    dateRange.value = [yesterdayStr, yesterdayStr]
  } else if (cmd === '7d') {
    const d = new Date(now)
    d.setDate(d.getDate() - 7)
    dateRange.value = [d.toISOString().slice(0, 10), today]
  } else if (cmd === '30d') {
    const d = new Date(now)
    d.setDate(d.getDate() - 30)
    dateRange.value = [d.toISOString().slice(0, 10), today]
  } else if (cmd === '3m') {
    const d = new Date(now)
    d.setMonth(d.getMonth() - 3)
    dateRange.value = [d.toISOString().slice(0, 10), today]
  }
  loadData()
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize }
    if (keyword.value) params.keyword = keyword.value
    if (refundStatusFilter.value !== '' && refundStatusFilter.value !== null) params.refund_status = refundStatusFilter.value
    if (dateRange.value && dateRange.value[0]) params.date_start = dateRange.value[0]
    if (dateRange.value && dateRange.value[1]) params.date_end = dateRange.value[1]
    const res = await getCancelledOrders(params)
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch {}
  loading.value = false
}

function onExport() {
  const params = {}
  if (keyword.value) params.keyword = keyword.value
  if (refundStatusFilter.value !== '' && refundStatusFilter.value !== null) params.refund_status = refundStatusFilter.value
  if (dateRange.value && dateRange.value[0]) params.date_start = dateRange.value[0]
  if (dateRange.value && dateRange.value[1]) params.date_end = dateRange.value[1]
  
  const url = exportCancelledOrdersUrl(params)
  window.open(url, '_blank')
  ElMessage.success(t('refund.exportStarted'))
}

// 退款状态编辑
const editDialogVisible = ref(false)
const editForm = ref({
  id: null,
  order_type: '',
  order_no: '',
  refund_status: 0,
  refund_amount: 0,
  remark: ''
})

function onEditRefund(row) {
  editForm.value = {
    id: row.id,
    order_type: row.order_type,
    order_no: row.order_no,
    refund_status: row.refund_status || 0,
    refund_amount: row.refund_amount || row.total_price || 0,
    remark: row.remark || ''
  }
  editDialogVisible.value = true
}

async function onSaveRefund() {
  try {
    await updateRefundStatus(editForm.value.order_type, editForm.value.id, {
      refund_status: editForm.value.refund_status,
      refund_amount: editForm.value.refund_amount,
      remark: editForm.value.remark
    })
    ElMessage.success(t('refund.updateSuccess'))
    editDialogVisible.value = false
    loadData()
  } catch (err) {
    console.error(err)
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.header-filters { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.header-actions { display: flex; gap: 8px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
