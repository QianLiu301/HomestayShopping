<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input v-model="keyword" :placeholder="$t('delivery.searchPlaceholder')" clearable style="width:240px" @keyup.enter="loadData" @clear="loadData">
          <template #append>
            <el-button :icon="Search" @click="loadData" />
          </template>
        </el-input>
        <el-radio-group v-model="statusFilter" @change="loadData">
          <el-radio-button :value="''">{{ $t('delivery.all') }}</el-radio-button>
          <el-radio-button :value="1">{{ $t('delivery.waitingDelivery') }}</el-radio-button>
          <el-radio-button :value="2">{{ $t('delivery.delivering') }}</el-radio-button>
        </el-radio-group>
      </div>
      <div class="header-actions">
        <el-button type="primary" :disabled="!selectedIds.length" :icon="Van" @click="onBatchStart">
          {{ $t('delivery.startDelivery') }} <span v-if="selectedIds.length">({{ selectedIds.length }})</span>
        </el-button>
        <el-button type="success" :disabled="!selectedIds.length" :icon="CircleCheck" @click="onBatchComplete">
          {{ $t('delivery.completeDelivery') }} <span v-if="selectedIds.length">({{ selectedIds.length }})</span>
        </el-button>
      </div>
    </div>

    <div v-loading="loading">
      <el-empty v-if="!loading && !groups.length" :description="$t('delivery.noOrders')" />

      <div v-for="(group, gi) in groups" :key="gi" class="address-group">
        <div class="address-header">
          <el-icon><Location /></el-icon>
          <span class="address-text">{{ group.address }}</span>
          <el-tag size="small" type="info">{{ group.orders.length }} {{ $t('delivery.orderUnit') }}</el-tag>
        </div>
        <el-card shadow="hover">
          <el-table :data="group.orders" size="small" stripe @selection-change="rows => onGroupSelectionChange(gi, rows)">
            <el-table-column type="selection" width="45" />
            <el-table-column prop="order_no" :label="$t('orders.orderNo')" width="190" />
            <el-table-column prop="contact_name" :label="$t('orders.customer')" width="120" />
            <el-table-column prop="room_number" :label="$t('delivery.roomNumber')" width="100">
              <template #default="{ row }">{{ row.room_number || '-' }}</template>
            </el-table-column>
            <el-table-column :label="$t('orders.items')" min-width="200">
              <template #default="{ row }">
                <span v-for="(item, i) in (row.items || [])" :key="i">{{ item.product_name }} x{{ item.quantity }}<span v-if="i < row.items.length - 1">, </span></span>
              </template>
            </el-table-column>
            <el-table-column :label="$t('orders.total')" width="100">
              <template #default="{ row }">¥{{ row.total_price }}</template>
            </el-table-column>
            <el-table-column :label="$t('orders.status')" width="110">
              <template #default="{ row }">
                <el-tag :type="statusTypes[row.status]" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('delivery.deliveryTime')" width="170">
              <template #default="{ row }">{{ formatDateTime(row.delivery_time) }}</template>
            </el-table-column>
            <el-table-column :label="$t('common.actions')" width="160" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.status === 1" link type="primary" @click="onStartSingle(row)">{{ $t('delivery.startDelivery') }}</el-button>
                <el-button v-if="row.status === 2" link type="success" @click="onCompleteSingle(row)">{{ $t('delivery.completeDelivery') }}</el-button>
                <el-button link type="info" @click="openDetail(row)">{{ $t('common.manage') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>

    <!-- Detail dialog -->
    <el-dialog v-model="dialogVisible" :title="$t('orders.orderDetail')" width="500px">
      <el-descriptions :column="1" border v-if="current">
        <el-descriptions-item :label="$t('orders.orderNo')">{{ current.order_no }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.customer')">{{ current.contact_name }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.phone')">{{ current.contact_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('delivery.roomNumber')">{{ current.room_number || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.resolvedAddress')">{{ current.resolved_address || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.bookingNo')">{{ current.booking_no || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.items')">
          <span v-for="(item, i) in (current.items || [])" :key="i">
            {{ item.product_name }}<span v-if="item.spec_name"> ({{ item.spec_name }})</span> x{{ item.quantity }} ¥{{ item.subtotal }}<br v-if="i < current.items.length - 1" />
          </span>
        </el-descriptions-item>
        <el-descriptions-item :label="$t('orders.total')">¥{{ current.total_price }}</el-descriptions-item>
        <el-descriptions-item :label="$t('orders.status')">
          <el-tag :type="statusTypes[current.status]" size="small">{{ statusLabel(current.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item v-if="current.delivery_time" :label="$t('delivery.deliveryTime')">{{ formatDateTime(current.delivery_time) }}</el-descriptions-item>
        <el-descriptions-item v-if="current.remark" :label="$t('orders.remark')">{{ current.remark }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.close') }}</el-button>
        <el-button v-if="current && current.status === 1" type="primary" @click="onStartSingle(current); dialogVisible = false">{{ $t('delivery.startDelivery') }}</el-button>
        <el-button v-if="current && current.status === 2" type="success" @click="onCompleteSingle(current); dialogVisible = false">{{ $t('delivery.completeDelivery') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Van, CircleCheck, Location } from '@element-plus/icons-vue'
import { getDeliveryOrders, startDelivery, completeDelivery } from '../api'

const { t } = useI18n()
const groups = ref([])
const loading = ref(false)
const keyword = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)
const current = ref(null)

// Track selections across all groups
const groupSelections = ref({})
const selectedIds = ref([])

const statusTypes = { 0: 'warning', 1: 'primary', 2: '', 3: 'success', 4: 'info' }
const statusLabel = s => t(`orders.${['pending', 'confirmed', 'delivering', 'completed', 'cancelled'][s] || 'unknown'}`)

function formatDateTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  if (isNaN(d.getTime())) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function onGroupSelectionChange(gi, rows) {
  groupSelections.value[gi] = rows.map(r => r.id)
  // Merge all group selections
  const all = []
  for (const ids of Object.values(groupSelections.value)) {
    all.push(...ids)
  }
  selectedIds.value = all
}

async function loadData() {
  loading.value = true
  groupSelections.value = {}
  selectedIds.value = []
  try {
    const params = {}
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value !== '') params.status = statusFilter.value
    const res = await getDeliveryOrders(params)
    groups.value = res.data?.groups || []
  } catch {}
  loading.value = false
}

function openDetail(row) {
  current.value = row
  dialogVisible.value = true
}

async function onStartSingle(row) {
  try {
    await startDelivery([row.id])
    ElMessage.success(t('delivery.startSuccess'))
    loadData()
  } catch {}
}

async function onCompleteSingle(row) {
  try {
    await completeDelivery([row.id])
    ElMessage.success(t('delivery.completeSuccess'))
    loadData()
  } catch {}
}

async function onBatchStart() {
  try {
    await ElMessageBox.confirm(
      t('delivery.batchStartConfirm', { count: selectedIds.value.length }),
      t('delivery.startDelivery'),
      { type: 'info', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
    )
  } catch { return }
  try {
    await startDelivery(selectedIds.value)
    ElMessage.success(t('delivery.startSuccess'))
    loadData()
  } catch {}
}

async function onBatchComplete() {
  try {
    await ElMessageBox.confirm(
      t('delivery.batchCompleteConfirm', { count: selectedIds.value.length }),
      t('delivery.completeDelivery'),
      { type: 'success', confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel') }
    )
  } catch { return }
  try {
    await completeDelivery(selectedIds.value)
    ElMessage.success(t('delivery.completeSuccess'))
    loadData()
  } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.header-filters { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.header-actions { display: flex; gap: 8px; flex-wrap: wrap; }

.address-group { margin-bottom: 20px; }
.address-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 4px;
  font-size: 15px;
  font-weight: 600;
  color: #4a3728;
}
.address-text { flex: 1; }
</style>
