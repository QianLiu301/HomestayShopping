<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-select
          v-model="attractionFilter"
          clearable
          filterable
          style="width: 220px"
          :placeholder="tPricing.attractionPlaceholder"
          @change="loadData"
        >
          <el-option v-for="item in attractions" :key="item.id" :label="item.name_zh || item.name_en" :value="item.id" />
        </el-select>

        <el-select
          v-model="serviceTypeFilter"
          clearable
          style="width: 180px"
          :placeholder="tPricing.serviceType"
          @change="loadData"
        >
          <el-option v-for="item in serviceTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>

        <el-select
          v-model="statusFilter"
          clearable
          style="width: 140px"
          :placeholder="$t('common.status')"
          @change="loadData"
        >
          <el-option :label="$t('common.active')" :value="1" />
          <el-option :label="$t('common.hidden')" :value="0" />
        </el-select>

        <el-button @click="loadData">{{ $t('common.search') }}</el-button>
      </div>

      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        {{ tPricing.addPrice }}
      </el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="filteredList" v-loading="loading" stripe>
        <el-table-column :label="tPricing.attraction" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ getAttractionName(row.attraction_id) }}
          </template>
        </el-table-column>

        <el-table-column :label="tPricing.vehicle" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ getVehicleName(row.vehicle) }}
          </template>
        </el-table-column>

        <el-table-column :label="tPricing.pickupPrice" width="140">
          <template #default="{ row }">{{ formatPrice(row.pickup_price) }}</template>
        </el-table-column>

        <el-table-column :label="tPricing.dropoffPrice" width="140">
          <template #default="{ row }">{{ formatPrice(row.dropoff_price) }}</template>
        </el-table-column>

        <el-table-column :label="tPricing.roundTripPrice" width="140">
          <template #default="{ row }">{{ formatPrice(row.round_trip_price) }}</template>
        </el-table-column>

        <el-table-column :label="tPricing.charterPrice" width="140">
          <template #default="{ row }">{{ formatPrice(row.charter_price) }}</template>
        </el-table-column>

        <el-table-column prop="sort_order" :label="$t('common.sort')" width="90" />

        <el-table-column :label="$t('common.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? $t('common.active') : $t('common.hidden') }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="$t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">{{ $t('common.edit') }}</el-button>
            <el-popconfirm :title="tPricing.deleteConfirm" @confirm="onDelete(row.id)">
              <template #reference>
                <el-button link type="danger">{{ $t('common.delete') }}</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? tPricing.editPrice : tPricing.addPrice"
      width="820px"
      destroy-on-close
    >
      <el-form :model="form" label-position="top">
        <div class="section-title">{{ tPricing.basicInfo }}</div>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="tPricing.attraction" required>
              <el-select v-model="form.attraction_id" filterable style="width: 100%">
                <el-option v-for="item in attractions" :key="item.id" :label="item.name_zh || item.name_en" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="tPricing.vehicle" required>
              <el-select v-model="form.vehicle_id" filterable style="width: 100%">
                <el-option v-for="item in vehicles" :key="item.id" :label="item.name_zh || item.name_en" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="section-title">{{ tPricing.servicePriceGroup }}</div>
        <div class="price-grid-tip">{{ tPricing.servicePriceGroupTip }}</div>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="tPricing.pickupPrice">
              <el-input-number v-model="form.pickup_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="tPricing.dropoffPrice">
              <el-input-number v-model="form.dropoff_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="tPricing.roundTripPrice">
              <el-input-number v-model="form.round_trip_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="tPricing.charterPrice">
              <el-input-number v-model="form.charter_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="$t('common.sort')">
              <el-input-number v-model="form.sort_order" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('common.status')">
              <el-radio-group v-model="form.status">
                <el-radio :value="1">{{ $t('common.active') }}</el-radio>
                <el-radio :value="0">{{ $t('common.hidden') }}</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getTicketAttractions,
  getTicketTransportPricing,
  createTicketTransportPrice,
  updateTicketTransportPrice,
  deleteTicketTransportPrice
} from '../api/tickets'
import { getVehicles } from '../api'

const { t, messages, locale } = useI18n()
const tPricing = computed(() => messages.value[locale.value]?.ticketTransportPricing || {})

const list = ref([])
const attractions = ref([])
const vehicles = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const attractionFilter = ref(undefined)
const serviceTypeFilter = ref('')
const statusFilter = ref(undefined)

const serviceTypeOptions = computed(() => [
  { value: 'pickup_only', label: tPricing.value.pickupOnly || '单程去景点' },
  { value: 'dropoff_only', label: tPricing.value.dropoffOnly || '单程返回' },
  { value: 'round_trip', label: tPricing.value.roundTrip || '往返' },
  { value: 'charter', label: tPricing.value.charter || '包车' }
])

const serviceTypeFieldMap = {
  pickup_only: 'pickup_price',
  dropoff_only: 'dropoff_price',
  round_trip: 'round_trip_price',
  charter: 'charter_price'
}

const defaultForm = () => ({
  attraction_id: null,
  vehicle_id: null,
  pickup_price: null,
  dropoff_price: null,
  round_trip_price: null,
  charter_price: null,
  sort_order: 0,
  status: 1
})

const form = reactive(defaultForm())

const filteredList = computed(() => {
  return list.value.filter(item => {
    if (serviceTypeFilter.value) {
      const field = serviceTypeFieldMap[serviceTypeFilter.value]
      if (!field || item[field] === null || item[field] === undefined) return false
    }
    if (statusFilter.value !== undefined && statusFilter.value !== null && statusFilter.value !== '' && item.status !== statusFilter.value) return false
    return true
  })
})

function normalizePrice(value) {
  return value === null || value === undefined || value === '' ? null : Number(value)
}

function formatPrice(value) {
  return value === null || value === undefined ? '-' : `¥${value}`
}

async function loadAttractions() {
  try {
    const res = await getTicketAttractions({ page: 1, per_page: 200 })
    attractions.value = res.data?.list || []
  } catch {}
}

async function loadVehicles() {
  try {
    const res = await getVehicles()
    vehicles.value = res.data || []
  } catch {}
}

async function loadData() {
  loading.value = true
  try {
    const res = await getTicketTransportPricing({ attraction_id: attractionFilter.value })
    list.value = res.data || []
  } catch {}
  loading.value = false
}

function getAttractionName(id) {
  const item = attractions.value.find(v => v.id === id)
  return item ? (item.name_zh || item.name_en) : '-'
}

function getVehicleName(vehicle) {
  if (!vehicle) return '-'
  return vehicle.name_zh || vehicle.name_en || '-'
}

function openDialog(row) {
  Object.assign(form, defaultForm())

  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.keys(form).forEach(k => {
      if (row[k] !== undefined && row[k] !== null) form[k] = row[k]
    })
  } else {
    isEdit.value = false
    editId.value = null
  }

  dialogVisible.value = true
}

async function onSave() {
  if (!form.attraction_id) {
    ElMessage.error(tPricing.value.attractionRequired || '请选择景点')
    return
  }
  if (!form.vehicle_id) {
    ElMessage.error(tPricing.value.vehicleRequired || '请选择车型')
    return
  }

  const payload = {
    attraction_id: form.attraction_id,
    vehicle_id: form.vehicle_id,
    pickup_price: normalizePrice(form.pickup_price),
    dropoff_price: normalizePrice(form.dropoff_price),
    round_trip_price: normalizePrice(form.round_trip_price),
    charter_price: normalizePrice(form.charter_price),
    sort_order: form.sort_order || 0,
    status: form.status
  }

  if ([payload.pickup_price, payload.dropoff_price, payload.round_trip_price, payload.charter_price].every(v => v === null)) {
    ElMessage.error(tPricing.value.atLeastOnePrice || '请至少填写一个服务价格')
    return
  }

  saving.value = true
  try {
    if (isEdit.value) {
      await updateTicketTransportPrice(editId.value, payload)
      ElMessage.success(t('common.updated'))
    } else {
      await createTicketTransportPrice(payload)
      ElMessage.success(t('common.created'))
    }
    dialogVisible.value = false
    loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try {
    await deleteTicketTransportPrice(id)
    ElMessage.success(t('common.deleted'))
    loadData()
  } catch {}
}

onMounted(async () => {
  await Promise.all([loadAttractions(), loadVehicles()])
  await loadData()
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
}

.header-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #4a3728;
  margin: 8px 0 12px;
}

.price-grid-tip {
  margin-bottom: 12px;
  font-size: 12px;
  line-height: 1.6;
  color: #8d7b67;
}
</style>
