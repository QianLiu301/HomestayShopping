<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input v-model="keyword" :placeholder="$t('orders.searchPlaceholder')" clearable style="width:240px" @keyup.enter="loadData" @clear="loadData">
          <template #append>
            <el-button :icon="Search" @click="loadData" />
          </template>
        </el-input>
        <el-select v-model="statusFilter" :placeholder="$t('common.status')" clearable style="width:130px" @change="loadData">
          <el-option :label="$t('orders.pending')" :value="0" /><el-option :label="$t('orders.confirmed')" :value="1" /><el-option :label="$t('orders.delivering')" :value="2" /><el-option :label="$t('orders.completed')" :value="3" /><el-option :label="$t('orders.cancelled')" :value="4" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" :start-placeholder="$t('orders.dateStart')" :end-placeholder="$t('orders.dateEnd')" value-format="YYYY-MM-DD" style="width:260px" @change="loadData" clearable />
        <el-dropdown @command="onQuickDate" style="margin-left:4px">
          <el-button><el-icon><Calendar /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="1m">{{ $t('orders.recent1m') }}</el-dropdown-item>
              <el-dropdown-item command="3m">{{ $t('orders.recent3m') }}</el-dropdown-item>
              <el-dropdown-item command="6m">{{ $t('orders.recent6m') }}</el-dropdown-item>
              <el-dropdown-item command="1y">{{ $t('orders.recent1y') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <div class="header-actions">
        <el-button type="danger" :disabled="!selectedIds.length" :icon="Delete" @click="onBatchDelete">
          {{ $t('orders.batchDelete') }} <span v-if="selectedIds.length">({{ selectedIds.length }})</span>
        </el-button>
      </div>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe @selection-change="onSelectionChange">
        <el-table-column type="selection" width="45" />
        <el-table-column prop="order_no" :label="$t('orders.orderNo')" width="190" />
        <el-table-column prop="contact_name" :label="$t('orders.customer')" width="120" />
        <el-table-column :label="$t('orders.bookingNo')" width="150">
          <template #default="{ row }">
            <el-button v-if="row.booking_no" link type="primary" @click="openDetail(row)">{{ row.booking_no }}</el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('orders.items')" min-width="200">
          <template #default="{ row }">
            <span v-for="(item, i) in (row.items || [])" :key="i">{{ item.product_name }} x{{ item.quantity }}<span v-if="i < row.items.length - 1">, </span></span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('orders.total')" width="100">
          <template #default="{ row }">¥{{ row.total_price }}</template>
        </el-table-column>
        <el-table-column :label="$t('orders.payment')" width="110">
          <template #default="{ row }">
            <el-tag :type="row.payment_status === 1 ? 'success' : 'warning'" size="small">
              {{ row.payment_status === 1 ? $t('orders.paid') : $t('orders.unpaid') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('orders.status')" width="140">
          <template #default="{ row }">
            <el-tag :type="statusTypes[row.status]" size="small">{{ statusLabel(row.status) }}</el-tag>
            <el-tag v-if="row.refund_status === 1" type="danger" size="small" style="margin-left:4px">{{ $t('orders.refunded') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('orders.created')" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">{{ $t('common.manage') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="$t('orders.orderDetail')" width="500px">
      <el-descriptions :column="1" border v-if="current">
        <el-descriptions-item :label="$t('orders.orderNo')">{{ current.order_no }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.bookingNo')">{{ current.booking_no || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.resolvedAddress')">{{ current.resolved_address || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.expectedDelivery')">
          <template v-if="current.expected_delivery_date">
            {{ current.expected_delivery_date }} {{ current.expected_delivery_time ? $t(`orders.timePeriod.${current.expected_delivery_time}`) : '' }}
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('orders.checkoutDate')">{{ current.checkout_date || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.customer')">{{ current.contact_name }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.phone')">{{ current.contact_phone }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.email')">{{ current.contact_email }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.items')">
          <span v-for="(item, i) in (current.items || [])" :key="i">
            {{ item.product_name }}<span v-if="item.spec_name"> ({{ item.spec_name }})</span> x{{ item.quantity }} ¥{{ item.subtotal }}<br v-if="i < current.items.length - 1" />
          </span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('orders.total')">¥{{ current.total_price }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.paymentMethod')">{{ paymentMethodLabel(current.payment_method) }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.paymentStatus')">
          <el-tag :type="current.payment_status === 1 ? 'success' : 'warning'" size="small">
            {{ current.payment_status === 1 ? $t('orders.paid') : $t('orders.unpaid') }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item v-if="current.transaction_id" :label="$t('orders.transactionId')">
          <span style="font-family:monospace">{{ current.transaction_id }}</span>
        </el-descriptions-item>
        <el-descriptions-item v-if="current.payment_screenshot" :label="$t('orders.paymentScreenshot')">
          <el-image :src="resolveUrl(current.payment_screenshot)" style="max-width:200px;max-height:200px;border-radius:8px" :preview-src-list="[resolveUrl(current.payment_screenshot)]" fit="contain" />
        </el-descriptions-item>
        <el-descriptions-item v-if="current.refund_status === 1" :label="$t('orders.refundStatus')">
          <el-tag type="danger" size="small">{{ $t('orders.refunded') }}</el-tag>
          <span v-if="current.refund_time" style="margin-left:8px;color:#999;font-size:12px">{{ formatDateTime(current.refund_time) }}</span>
        </el-descriptions-item>
        <el-descriptions-item v-if="current.remark" :label="$t('orders.remark')">{{ current.remark }}</el-descriptions-item>
        <el-descriptions-item v-if="current.review" :label="$t('orders.review')">
          <el-rate :model-value="current.review.rating" disabled size="small" />
          <div v-if="current.review.comment" style="margin-top:4px;color:#666;font-size:13px">{{ current.review.comment }}</div>
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="current && current.payment_status !== 1" style="margin-top:16px;padding:12px;background:#fff7e6;border-radius:8px;text-align:center">
        <p v-if="current.payment_method" style="margin:0 0 10px;color:#e6a23c;font-size:13px">{{ $t('orders.confirmPaymentTip', { method: paymentMethodLabel(current.payment_method) }) }}</p>
        <p v-else style="margin:0 0 10px;color:#e6a23c;font-size:13px">{{ $t('orders.notYetPaid') }}</p>
        <el-button type="warning" :loading="confirmingPayment" @click="onConfirmPayment">
          {{ $t('orders.confirmPayment') }}
        </el-button>
      </div>
      <div v-else-if="current && current.payment_status === 1" style="margin-top:16px;padding:12px;background:#f0f9eb;border-radius:8px;text-align:center">
        <p style="margin:0;color:#67c23a;font-size:13px">{{ $t('orders.paymentConfirmed') }}</p>
      </div>

      <el-form style="margin-top:20px" label-position="top">
        <el-form-item :label="$t('orders.bookingNo')">
          <el-input v-model="updateForm.booking_no" :placeholder="$t('orders.bookingNoPlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('orders.resolvedAddress')">
          <el-input v-model="updateForm.resolved_address" :placeholder="$t('orders.resolvedAddressPlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('orders.checkoutDate')">
          <el-date-picker v-model="updateForm.checkout_date" type="date" value-format="YYYY-MM-DD" :placeholder="$t('orders.checkoutDatePlaceholder')" clearable style="width:100%" />
        </el-form-item>
        <el-form-item :label="$t('orders.updateStatus')">
          <el-select v-model="updateForm.status" style="width:100%">
            <el-option :label="$t('orders.pending')" :value="0" /><el-option :label="$t('orders.confirmed')" :value="1" /><el-option :label="$t('orders.delivering')" :value="2" /><el-option :label="$t('orders.completed')" :value="3" /><el-option :label="$t('orders.cancelled')" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('orders.remark')">
          <el-input v-model="updateForm.remark" type="textarea" :rows="2" :placeholder="$t('orders.remarkPlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.close') }}</el-button>
        <el-button type="primary" :loading="saving" @click="onUpdate">{{ $t('common.update') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Delete, Calendar } from '@element-plus/icons-vue'
import { getShopOrders, updateShopOrder, confirmShopPayment, batchDeleteShopOrders, resolveUrl } from '../api'

const { t } = useI18n()
const list = ref([])
const loading = ref(false)
const saving = ref(false)
const confirmingPayment = ref(false)
const dialogVisible = ref(false)
const current = ref(null)
const page = ref(1)
const pageSize = 15
const total = ref(0)
const keyword = ref('')
const statusFilter = ref('')
const dateRange = ref(null)
const selectedIds = ref([])
const updateForm = reactive({ status: 0, remark: '', booking_no: '', resolved_address: '', checkout_date: '' })

function formatDateTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  if (isNaN(d.getTime())) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

const statusTypes = { 0: 'warning', 1: 'primary', 2: '', 3: 'success', 4: 'info' }
const statusLabel = s => t(`orders.${['pending','confirmed','delivering','completed','cancelled'][s] || 'unknown'}`)

function paymentMethodLabel(method) {
  if (!method) return '-'
  const map = { wechat: t('orders.wechat'), alipay: t('orders.alipay'), credit_card: t('orders.creditCard') }
  return map[method] || method
}

function onQuickDate(cmd) {
  const now = new Date()
  const end = now.toISOString().slice(0, 10)
  const d = new Date(now)
  if (cmd === '1m') d.setMonth(d.getMonth() - 1)
  else if (cmd === '3m') d.setMonth(d.getMonth() - 3)
  else if (cmd === '6m') d.setMonth(d.getMonth() - 6)
  else if (cmd === '1y') d.setFullYear(d.getFullYear() - 1)
  dateRange.value = [d.toISOString().slice(0, 10), end]
  loadData()
}

function onSelectionChange(rows) {
  selectedIds.value = rows.map(r => r.id)
}

async function onBatchDelete() {
  try {
    await ElMessageBox.confirm(
      t('orders.batchDeleteConfirm', { count: selectedIds.value.length }),
      t('orders.batchDeleteTitle'),
      { type: 'warning', confirmButtonText: t('orders.confirmDelete'), cancelButtonText: t('common.close') }
    )
  } catch { return }
  try {
    const res = await batchDeleteShopOrders(selectedIds.value)
    ElMessage.success(res.message || t('common.updated'))
    selectedIds.value = []
    loadData()
  } catch {}
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value !== '' && statusFilter.value !== null) params.status = statusFilter.value
    if (dateRange.value && dateRange.value[0]) params.date_start = dateRange.value[0]
    if (dateRange.value && dateRange.value[1]) params.date_end = dateRange.value[1]
    const res = await getShopOrders(params)
    list.value = res.data?.list || res.data?.items || []
    total.value = res.data?.total || list.value.length
  } catch {}
  loading.value = false
}

function openDetail(row) {
  current.value = row
  updateForm.status = row.status
  updateForm.remark = row.remark || ''
  updateForm.booking_no = row.booking_no || ''
  updateForm.resolved_address = row.resolved_address || ''
  updateForm.checkout_date = row.checkout_date || ''
  dialogVisible.value = true
}

async function onUpdate() {
  saving.value = true
  try {
    await updateShopOrder(current.value.id, updateForm)
    ElMessage.success(t('common.updated'))
    dialogVisible.value = false
    loadData()
  } catch {}
  saving.value = false
}

async function onConfirmPayment() {
  confirmingPayment.value = true
  try {
    await confirmShopPayment(current.value.id)
    ElMessage.success(t('orders.paymentConfirmedMsg'))
    current.value.payment_status = 1
    loadData()
  } catch {}
  confirmingPayment.value = false
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.header-filters { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.header-actions { display: flex; gap: 8px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
