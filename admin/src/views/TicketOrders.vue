<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input
          v-model="keyword"
          :placeholder="tOrders.searchPlaceholder"
          clearable
          style="width: 240px"
          @keyup.enter="loadData"
          @clear="loadData"
        >
          <template #append>
            <el-button :icon="Search" @click="loadData" />
          </template>
        </el-input>

        <el-select
          v-model="statusFilter"
          clearable
          style="width: 140px"
          :placeholder="tOrders.status"
          @change="loadData"
        >
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>

        <el-select
          v-model="paymentStatusFilter"
          clearable
          style="width: 140px"
          :placeholder="tOrders.paymentStatus"
          @change="loadData"
        >
          <el-option :label="tOrders.unpaid" :value="0" />
          <el-option :label="tOrders.paid" :value="1" />
        </el-select>

        <el-date-picker
          v-model="dateRange"
          type="daterange"
          value-format="YYYY-MM-DD"
          style="width: 260px"
          :start-placeholder="tOrders.dateStart"
          :end-placeholder="tOrders.dateEnd"
          clearable
          @change="loadData"
        />

        <el-dropdown @command="onQuickDate">
          <el-button><el-icon><Calendar /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="1m">{{ tOrders.recent1m }}</el-dropdown-item>
              <el-dropdown-item command="3m">{{ tOrders.recent3m }}</el-dropdown-item>
              <el-dropdown-item command="6m">{{ tOrders.recent6m }}</el-dropdown-item>
              <el-dropdown-item command="1y">{{ tOrders.recent1y }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="order_no" :label="tOrders.orderNo" width="190" />

        <el-table-column :label="tOrders.attraction" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.attraction?.name || row.attraction?.name_zh || '-' }}
          </template>
        </el-table-column>

        <el-table-column :label="tOrders.package" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ getPackageName(row.package_snapshot) }}
          </template>
        </el-table-column>

        <el-table-column prop="contact_name" :label="tOrders.customer" width="120" />
        <el-table-column prop="contact_phone" :label="tOrders.phone" width="140" />

        <el-table-column :label="tOrders.visitDate" width="120">
          <template #default="{ row }">{{ row.visit_date || '-' }}</template>
        </el-table-column>

        <el-table-column :label="tOrders.travelers" width="90">
          <template #default="{ row }">{{ row.travelers?.length || 0 }}</template>
        </el-table-column>

        <el-table-column :label="tOrders.transfer" width="120">
          <template #default="{ row }">
            <el-tag :type="row.need_transfer ? 'warning' : 'info'" size="small">
              {{ row.need_transfer ? tOrders.needTransfer : tOrders.noTransfer }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="tOrders.total" width="110">
          <template #default="{ row }">¥{{ row.total_price }}</template>
        </el-table-column>

        <el-table-column :label="tOrders.paymentStatus" width="120">
          <template #default="{ row }">
            <el-tag :type="row.payment_status === 1 ? 'success' : 'warning'" size="small">
              {{ row.payment_status === 1 ? tOrders.paid : tOrders.unpaid }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="tOrders.voucherStatus" width="120">
          <template #default="{ row }">
            <el-tag :type="row.voucher_delivery_status === 1 ? 'success' : 'info'" size="small">
              {{ row.voucher_delivery_status === 1 ? tOrders.voucherSent : tOrders.voucherPending }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="tOrders.status" width="110">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="tOrders.created" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>

        <el-table-column :label="$t('common.actions')" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">{{ $t('common.manage') }}</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="tOrders.orderDetail"
      width="1080px"
      destroy-on-close
    >
      <div v-if="current" class="detail-layout">
        <div class="detail-main">
          <el-descriptions :column="2" border>
            <el-descriptions-item :label="tOrders.orderNo">{{ current.order_no }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.status">
              <el-tag :type="statusTypeMap[current.status]" size="small">{{ getStatusLabel(current.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="tOrders.attraction">{{ current.attraction?.name || current.attraction?.name_zh || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.package">{{ getPackageName(current.package_snapshot) }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.visitDate">{{ current.visit_date || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.lang">{{ (current.lang || '').toUpperCase() || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.customer">{{ current.contact_name || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.phone">{{ current.contact_phone || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.email">{{ current.contact_email || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.bookingNo">{{ current.booking_no || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.total">¥{{ current.total_price }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.discount">{{ current.discount_amount ? `-¥${current.discount_amount}` : '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.paymentMethod">{{ paymentMethodLabel(current.payment_method) }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.paymentStatus">
              <el-tag :type="current.payment_status === 1 ? 'success' : 'warning'" size="small">
                {{ current.payment_status === 1 ? tOrders.paid : tOrders.unpaid }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="tOrders.paymentTime">{{ formatDateTime(current.payment_time) }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.transactionId">{{ current.transaction_id || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.transfer">{{ current.need_transfer ? tOrders.needTransfer : tOrders.noTransfer }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.transferServiceType">{{ transferServiceTypeLabel(current.transfer_service_type) }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.transferVehicle">{{ current.transfer_vehicle?.name || current.transfer_vehicle?.name_zh || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.transferPrice">{{ current.transfer_price_snapshot ? `¥${current.transfer_price_snapshot}` : '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.voucherStatus">
              <el-tag :type="current.voucher_delivery_status === 1 ? 'success' : 'info'" size="small">
                {{ current.voucher_delivery_status === 1 ? tOrders.voucherSent : tOrders.voucherPending }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="tOrders.created">{{ formatDateTime(current.created_at) }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.cancelledAt">{{ formatDateTime(current.cancelled_at) }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.refundStatus">
              <el-tag :type="refundStatusType(current.refund_status)" size="small">{{ refundStatusLabel(current.refund_status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="tOrders.refundAmount">{{ current.refund_amount !== null && current.refund_amount !== undefined ? `¥${current.refund_amount}` : '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.refundTime">{{ formatDateTime(current.refund_time) }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.remark">{{ current.remark || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="tOrders.adminNote">{{ current.admin_note || '-' }}</el-descriptions-item>
          </el-descriptions>

          <div class="section-block">
            <div class="section-title">{{ tOrders.packageSnapshot }}</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="tOrders.package">{{ getPackageName(current.package_snapshot) }}</el-descriptions-item>
              <el-descriptions-item :label="tOrders.ticketType">{{ ticketTypeLabel(current.package_snapshot?.ticket_type) }}</el-descriptions-item>
              <el-descriptions-item :label="tOrders.salePrice">{{ current.package_snapshot?.sale_price ? `¥${current.package_snapshot.sale_price}` : '-' }}</el-descriptions-item>
              <el-descriptions-item :label="tOrders.originalPrice">{{ current.package_snapshot?.original_price ? `¥${current.package_snapshot.original_price}` : '-' }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="section-block">
            <div class="section-title">{{ tOrders.travelerInfo }}</div>
            <el-table :data="current.travelers || []" size="small" border>
              <el-table-column :label="tOrders.travelerType" width="110">
                <template #default="{ row }">{{ travelerTypeLabel(row.traveler_type) }}</template>
              </el-table-column>
              <el-table-column prop="full_name" :label="tOrders.fullName" min-width="140" />
              <el-table-column prop="nationality" :label="tOrders.nationality" min-width="120" />
              <el-table-column prop="document_type" :label="tOrders.documentType" width="120">
                <template #default="{ row }">{{ documentTypeLabel(row.document_type) }}</template>
              </el-table-column>
              <el-table-column prop="document_no" :label="tOrders.documentNo" min-width="140" />
              <el-table-column prop="date_of_birth" :label="tOrders.dateOfBirth" width="120" />
              <el-table-column prop="gender" :label="tOrders.gender" width="100">
                <template #default="{ row }">{{ genderLabel(row.gender) }}</template>
              </el-table-column>
            </el-table>
            <el-empty v-if="!(current.travelers || []).length" :description="$t('common.noData')" :image-size="80" />
          </div>
        </div>

        <div class="detail-side">
          <div class="action-card" v-if="current.payment_status !== 1">
            <div class="action-title">{{ tOrders.confirmPayment }}</div>
            <el-form label-position="top">
              <el-form-item :label="tOrders.paymentMethod">
                <el-select v-model="paymentForm.payment_method" style="width: 100%" clearable>
                  <el-option value="wechat" :label="tOrders.wechat" />
                  <el-option value="alipay" :label="tOrders.alipay" />
                  <el-option value="credit_card" :label="tOrders.creditCard" />
                </el-select>
              </el-form-item>
              <el-form-item :label="tOrders.transactionId">
                <el-input v-model="paymentForm.transaction_id" />
              </el-form-item>
              <el-button type="warning" :loading="confirmingPayment" style="width: 100%" @click="onConfirmPayment">
                {{ tOrders.confirmPayment }}
              </el-button>
            </el-form>
          </div>

          <div class="action-card" v-else>
            <div class="paid-banner">{{ tOrders.paymentConfirmed }}</div>
          </div>

          <div class="action-card">
            <div class="action-title">{{ tOrders.updateStatus }}</div>
            <el-form label-position="top">
              <el-form-item :label="tOrders.updateStatus">
                <el-select v-model="updateForm.status" style="width: 100%">
                  <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
              <el-form-item :label="tOrders.adminNote">
                <el-input v-model="updateForm.admin_note" type="textarea" :rows="4" :placeholder="tOrders.adminNotePlaceholder" />
              </el-form-item>
              <el-button type="primary" :loading="saving" style="width: 100%" @click="onUpdateStatus">
                {{ $t('common.update') }}
              </el-button>
            </el-form>
          </div>

          <div class="action-card">
            <div class="action-header">
              <span class="action-title">{{ tOrders.vouchers }}</span>
              <el-button
                type="success"
                plain
                size="small"
                :disabled="!(current.vouchers || []).length"
                :loading="sendingVoucher"
                @click="onSendVoucher"
              >
                {{ tOrders.sendVoucher }}
              </el-button>
            </div>

            <el-upload
              class="voucher-upload"
              :show-file-list="false"
              :http-request="handleVoucherUpload"
              accept=".pdf,.jpg,.jpeg,.png,.webp"
            >
              <el-button type="primary" plain :loading="uploadingVoucher">{{ tOrders.uploadVoucher }}</el-button>
            </el-upload>

            <div v-if="current.vouchers?.length" class="voucher-list">
              <div v-for="item in current.vouchers" :key="item.id" class="voucher-item">
                <div class="voucher-meta">
                  <el-link :href="resolveUrl(item.file_url)" target="_blank" type="primary">
                    {{ item.file_name || item.file_url }}
                  </el-link>
                  <div class="voucher-submeta">
                    <span>{{ formatDateTime(item.created_at) }}</span>
                    <el-tag size="small" :type="item.sent_to_customer ? 'success' : 'info'">
                      {{ item.sent_to_customer ? tOrders.sent : tOrders.notSent }}
                    </el-tag>
                  </div>
                </div>
                <el-popconfirm :title="tOrders.deleteVoucherConfirm" @confirm="onDeleteVoucher(item)">
                  <template #reference>
                    <el-button link type="danger">{{ $t('common.delete') }}</el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
            <el-empty v-else :description="tOrders.noVouchers" :image-size="80" />
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Search, Calendar } from '@element-plus/icons-vue'
import {
  getTicketOrders,
  getTicketOrder,
  updateTicketOrderStatus,
  confirmTicketOrderPayment,
  uploadTicketVoucher,
  deleteTicketVoucher,
  sendTicketVoucher
} from '../api/tickets'
import { resolveUrl } from '../api'

const { t, messages, locale } = useI18n()
const tOrders = computed(() => messages.value[locale.value]?.ticketOrders || {})

const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const confirmingPayment = ref(false)
const uploadingVoucher = ref(false)
const sendingVoucher = ref(false)
const current = ref(null)
const page = ref(1)
const pageSize = 15
const total = ref(0)
const keyword = ref('')
const statusFilter = ref(undefined)
const paymentStatusFilter = ref(undefined)
const dateRange = ref(null)

const updateForm = reactive({
  status: 0,
  admin_note: ''
})

const paymentForm = reactive({
  payment_method: '',
  transaction_id: ''
})

const statusTypeMap = {
  0: 'warning',
  1: 'primary',
  2: 'success',
  3: 'info'
}

const statusOptions = computed(() => [
  { value: 0, label: tOrders.value.pending },
  { value: 1, label: tOrders.value.confirmed },
  { value: 2, label: tOrders.value.completed },
  { value: 3, label: tOrders.value.cancelled }
])

function getStatusLabel(status) {
  return statusOptions.value.find(item => item.value === status)?.label || tOrders.value.unknown || '-'
}

function refundStatusLabel(status) {
  const map = {
    0: tOrders.value.noRefundNeeded,
    1: tOrders.value.pendingRefund,
    2: tOrders.value.refunded
  }
  return map[status] || tOrders.value.unknown || '-'
}

function refundStatusType(status) {
  const map = { 0: 'info', 1: 'warning', 2: 'success' }
  return map[status] || 'info'
}

function paymentMethodLabel(method) {
  if (!method) return '-'
  const map = {
    wechat: tOrders.value.wechat,
    alipay: tOrders.value.alipay,
    credit_card: tOrders.value.creditCard
  }
  return map[method] || method
}

function transferServiceTypeLabel(type) {
  if (!type) return '-'
  const map = {
    pickup_only: tOrders.value.pickupOnly,
    dropoff_only: tOrders.value.dropoffOnly,
    round_trip: tOrders.value.roundTrip,
    charter: tOrders.value.charter
  }
  return map[type] || type
}

function travelerTypeLabel(type) {
  const map = {
    adult: tOrders.value.adult,
    child: tOrders.value.child,
    senior: tOrders.value.senior
  }
  return map[type] || type || '-'
}

function documentTypeLabel(type) {
  const map = {
    passport: tOrders.value.passport,
    id_card: tOrders.value.idCard
  }
  return map[type] || type || '-'
}

function genderLabel(gender) {
  const map = {
    male: tOrders.value.male,
    female: tOrders.value.female
  }
  return map[gender] || gender || '-'
}

function ticketTypeLabel(type) {
  const map = {
    adult: tOrders.value.adultTicket,
    child: tOrders.value.childTicket,
    senior: tOrders.value.seniorTicket,
    family: tOrders.value.familyTicket,
    combo: tOrders.value.comboTicket
  }
  return map[type] || type || '-'
}

function getPackageName(snapshot) {
  if (!snapshot) return '-'
  return snapshot.package_name_zh || snapshot.package_name_en || snapshot.package_name || '-'
}

function formatDateTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
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

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value !== undefined && statusFilter.value !== null && statusFilter.value !== '') params.status = statusFilter.value
    if (paymentStatusFilter.value !== undefined && paymentStatusFilter.value !== null && paymentStatusFilter.value !== '') params.payment_status = paymentStatusFilter.value
    if (dateRange.value?.[0]) params.date_start = dateRange.value[0]
    if (dateRange.value?.[1]) params.date_end = dateRange.value[1]

    const res = await getTicketOrders(params)
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

async function openDetail(row) {
  dialogVisible.value = true
  current.value = null
  try {
    const res = await getTicketOrder(row.id)
    current.value = res.data
    updateForm.status = res.data.status ?? 0
    updateForm.admin_note = res.data.admin_note || ''
    paymentForm.payment_method = res.data.payment_method || ''
    paymentForm.transaction_id = res.data.transaction_id || ''
  } catch {
    dialogVisible.value = false
  }
}

async function onUpdateStatus() {
  if (!current.value) return
  saving.value = true
  try {
    const res = await updateTicketOrderStatus(current.value.id, {
      status: updateForm.status,
      admin_note: updateForm.admin_note
    })
    ElMessage.success(res.message || t('common.updated'))
    current.value = res.data
    await loadData()
  } finally {
    saving.value = false
  }
}

async function onConfirmPayment() {
  if (!current.value) return
  confirmingPayment.value = true
  try {
    const res = await confirmTicketOrderPayment(current.value.id, {
      payment_method: paymentForm.payment_method || undefined,
      transaction_id: paymentForm.transaction_id || undefined
    })
    ElMessage.success(res.message || tOrders.value.paymentConfirmedMsg)
    current.value = res.data
    await loadData()
  } finally {
    confirmingPayment.value = false
  }
}

async function handleVoucherUpload(option) {
  if (!current.value) return
  uploadingVoucher.value = true
  try {
    const res = await uploadTicketVoucher(current.value.id, option.file)
    ElMessage.success(res.message || tOrders.value.uploadSuccess)
    current.value.vouchers = [...(current.value.vouchers || []), res.data]
    option.onSuccess?.(res)
    await refreshOrderMeta()
    await loadData()
  } catch (error) {
    option.onError?.(error)
  } finally {
    uploadingVoucher.value = false
  }
}

async function onDeleteVoucher(voucher) {
  if (!current.value) return
  try {
    const res = await deleteTicketVoucher(current.value.id, voucher.id)
    ElMessage.success(res.message || t('common.deleted'))
    current.value.vouchers = (current.value.vouchers || []).filter(item => item.id !== voucher.id)
    await refreshOrderMeta()
    await loadData()
  } catch {
    // handled by interceptor
  }
}

async function onSendVoucher() {
  if (!current.value) return
  sendingVoucher.value = true
  try {
    const res = await sendTicketVoucher(current.value.id)
    ElMessage.success(res.message || tOrders.value.sendSuccess)
    current.value = res.data
    await loadData()
  } finally {
    sendingVoucher.value = false
  }
}

async function refreshOrderMeta() {
  if (!current.value) return
  const res = await getTicketOrder(current.value.id)
  current.value = res.data
}

onMounted(loadData)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
  flex-wrap: wrap;
}

.header-filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) 320px;
  gap: 20px;
}

.detail-main,
.detail-side {
  min-width: 0;
}

.section-block {
  margin-top: 20px;
}

.section-title,
.action-title {
  font-size: 15px;
  font-weight: 600;
  color: #4a3728;
  margin-bottom: 12px;
}

.action-card {
  padding: 16px;
  border: 1px solid #ebe5df;
  border-radius: 12px;
  background: #fffdfb;
  margin-bottom: 16px;
}

.action-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.action-header .action-title {
  margin-bottom: 0;
}

.paid-banner {
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  color: #67c23a;
  background: #f0f9eb;
}

.voucher-upload {
  margin-bottom: 16px;
}

.voucher-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.voucher-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #ebeef5;
}

.voucher-meta {
  min-width: 0;
  flex: 1;
}

.voucher-submeta {
  margin-top: 6px;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  color: #909399;
  font-size: 12px;
}

@media (max-width: 960px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
