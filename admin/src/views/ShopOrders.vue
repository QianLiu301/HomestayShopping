<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input v-model="keyword" placeholder="Search order no / customer..." clearable style="width:260px" @keyup.enter="loadData" />
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width:140px" @change="loadData">
          <el-option label="Pending" :value="0" /><el-option label="Confirmed" :value="1" /><el-option label="Completed" :value="2" /><el-option label="Cancelled" :value="3" />
        </el-select>
      </div>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="Order No" width="190" />
        <el-table-column prop="contact_name" label="Customer" width="120" />
        <el-table-column prop="contact_phone" label="Phone" width="130" />
        <el-table-column label="Items" min-width="200">
          <template #default="{ row }">
            <span v-for="(item, i) in (row.items || [])" :key="i">{{ item.product_name }} x{{ item.quantity }}<span v-if="i < row.items.length - 1">, </span></span>
          </template>
        </el-table-column>
        <el-table-column label="Total" width="100">
          <template #default="{ row }">¥{{ row.total_price }}</template>
        </el-table-column>
        <el-table-column label="Payment" width="110">
          <template #default="{ row }">
            <el-tag :type="row.payment_status === 1 ? 'success' : 'warning'" size="small">
              {{ row.payment_status === 1 ? 'Paid' : 'Unpaid' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="statusTypes[row.status]" size="small">{{ statusLabels[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Created" width="170" />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">Manage</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="Order Detail" width="500px">
      <el-descriptions :column="1" border v-if="current">
        <el-descriptions-item label="Order No">{{ current.order_no }}</el-descriptions-item>
        <el-descriptions-item label="Customer">{{ current.contact_name }}</el-descriptions-item>
        <el-descriptions-item label="Phone">{{ current.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="Email">{{ current.contact_email }}</el-descriptions-item>
        <el-descriptions-item label="Total">¥{{ current.total_price }}</el-descriptions-item>
        <el-descriptions-item label="Payment Method">{{ paymentMethodLabel(current.payment_method) }}</el-descriptions-item>
        <el-descriptions-item label="Payment Status">
          <el-tag :type="current.payment_status === 1 ? 'success' : 'warning'" size="small">
            {{ current.payment_status === 1 ? 'Paid' : 'Unpaid' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- Confirm Payment Button -->
      <div v-if="current && current.payment_status !== 1" style="margin-top:16px;padding:12px;background:#fff7e6;border-radius:8px;text-align:center">
        <p style="margin:0 0 10px;color:#e6a23c;font-size:13px">Customer selected: {{ paymentMethodLabel(current.payment_method) }}. Please verify payment received before confirming.</p>
        <el-button type="warning" :loading="confirmingPayment" @click="onConfirmPayment">
          Confirm Payment Received
        </el-button>
      </div>
      <div v-else-if="current && current.payment_status === 1" style="margin-top:16px;padding:12px;background:#f0f9eb;border-radius:8px;text-align:center">
        <p style="margin:0;color:#67c23a;font-size:13px">Payment confirmed ✓</p>
      </div>

      <el-form style="margin-top:20px" label-position="top">
        <el-form-item label="Update Status">
          <el-select v-model="updateForm.status" style="width:100%">
            <el-option label="Pending" :value="0" /><el-option label="Confirmed" :value="1" /><el-option label="Completed" :value="2" /><el-option label="Cancelled" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="Remark">
          <el-input v-model="updateForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <el-button type="primary" :loading="saving" @click="onUpdate">Update</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getShopOrders, updateShopOrder, confirmShopPayment } from '../api'

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
const updateForm = reactive({ status: 0, remark: '' })

const statusLabels = { 0: 'Pending', 1: 'Confirmed', 2: 'Completed', 3: 'Cancelled' }
const statusTypes = { 0: 'warning', 1: 'primary', 2: 'success', 3: 'info' }
const paymentMethods = { wechat: 'WeChat Pay', alipay: 'Alipay', credit_card: 'Credit Card' }

function paymentMethodLabel(method) {
  return paymentMethods[method] || method || '-'
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value !== '' && statusFilter.value !== null) params.status = statusFilter.value
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
  dialogVisible.value = true
}

async function onUpdate() {
  saving.value = true
  try {
    await updateShopOrder(current.value.id, updateForm)
    ElMessage.success('Updated')
    dialogVisible.value = false
    loadData()
  } catch {}
  saving.value = false
}

async function onConfirmPayment() {
  confirmingPayment.value = true
  try {
    await confirmShopPayment(current.value.id)
    ElMessage.success('Payment confirmed')
    current.value.payment_status = 1
    loadData()
  } catch {}
  confirmingPayment.value = false
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; margin-bottom: 16px; }
.header-filters { display: flex; gap: 12px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
