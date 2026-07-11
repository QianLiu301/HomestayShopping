<template>
  <div class="guest-reg-page">
    <div class="page-header">
      <div class="header-filters">
        <el-input
          v-model="keyword"
          :placeholder="$t('guestReg.searchPlaceholder')"
          clearable
          style="width: 240px"
          @keyup.enter="loadData(1)"
          @clear="loadData(1)"
        >
          <template #append>
            <el-button :icon="Search" @click="loadData(1)" />
          </template>
        </el-input>
        <el-select v-model="statusFilter" :placeholder="$t('guestReg.statusFilter')" clearable style="width: 130px" @change="loadData(1)">
          <el-option :label="$t('guestReg.pending')" :value="0" />
          <el-option :label="$t('guestReg.declared')" :value="1" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          value-format="YYYY-MM-DD"
          :start-placeholder="$t('guestReg.dateStart')"
          :end-placeholder="$t('guestReg.dateEnd')"
          style="width: 260px"
          @change="loadData(1)"
        />
      </div>
      <div class="header-actions">
        <el-button type="success" plain :icon="Download" @click="onExport">{{ $t('guestReg.exportBtn') }}</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="list" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column :label="$t('guestReg.name')" min-width="160">
        <template #default="{ row }">
          <span style="font-weight:600">{{ row.full_name }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('guestReg.dob')" width="120">
        <template #default="{ row }">{{ row.date_of_birth || '-' }}</template>
      </el-table-column>
      <el-table-column :label="$t('guestReg.platform')" width="120">
        <template #default="{ row }">{{ platformLabel(row.platform) }}</template>
      </el-table-column>
      <el-table-column prop="booking_no" :label="$t('guestReg.bookingNo')" min-width="150" show-overflow-tooltip />
      <el-table-column :label="$t('guestReg.photos')" width="150">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="openDetail(row)">{{ $t('guestReg.viewPhotos') }}</el-button>
        </template>
      </el-table-column>
      <el-table-column :label="$t('guestReg.status')" width="110">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'warning'" size="small">
            {{ row.status === 1 ? $t('guestReg.declared') : $t('guestReg.pending') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="$t('guestReg.createdAt')" width="160">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column :label="$t('common.actions')" width="200" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 0"
            link
            type="success"
            size="small"
            @click="onSetStatus(row, 1)"
          >{{ $t('guestReg.markDeclared') }}</el-button>
          <el-button
            v-else
            link
            type="warning"
            size="small"
            @click="onSetStatus(row, 0)"
          >{{ $t('guestReg.markPending') }}</el-button>
          <el-button link type="danger" size="small" @click="onDelete(row)">{{ $t('common.delete') }}</el-button>
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

    <!-- 详情/照片弹窗 -->
    <el-dialog v-model="dialogVisible" :title="$t('guestReg.detailTitle')" width="720px">
      <template v-if="current">
        <el-descriptions :column="2" border style="margin-bottom:16px">
          <el-descriptions-item :label="$t('guestReg.name')">{{ current.full_name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.dob')">{{ current.date_of_birth }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.platform')">{{ platformLabel(current.platform) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.bookingNo')">{{ current.booking_no }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.status')">
            <el-tag :type="current.status === 1 ? 'success' : 'warning'" size="small">
              {{ current.status === 1 ? $t('guestReg.declared') : $t('guestReg.pending') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.createdAt')">{{ formatDateTime(current.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="photo-grid">
          <div class="photo-block">
            <div class="photo-label">{{ $t('guestReg.passportPhoto') }}</div>
            <el-image
              :src="guestDocUrl(current.passport_image)"
              :preview-src-list="[guestDocUrl(current.passport_image), guestDocUrl(current.handheld_image)]"
              fit="contain"
              class="photo-img"
            />
            <el-button size="small" style="margin-top:8px" @click="downloadDoc(current.passport_image, `passport_${current.id}`)">
              {{ $t('guestReg.download') }}
            </el-button>
          </div>
          <div class="photo-block">
            <div class="photo-label">{{ $t('guestReg.handheldPhoto') }}</div>
            <el-image
              :src="guestDocUrl(current.handheld_image)"
              :preview-src-list="[guestDocUrl(current.handheld_image), guestDocUrl(current.passport_image)]"
              fit="contain"
              class="photo-img"
            />
            <el-button size="small" style="margin-top:8px" @click="downloadDoc(current.handheld_image, `handheld_${current.id}`)">
              {{ $t('guestReg.download') }}
            </el-button>
          </div>
        </div>
      </template>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.close') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'
import {
  getGuestRegistrations,
  updateGuestRegistrationStatus,
  deleteGuestRegistration,
  guestDocUrl,
  guestRegistrationsExportUrl,
} from '../api'

const { t } = useI18n()

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 15
const total = ref(0)
const keyword = ref('')
const statusFilter = ref(undefined)
const dateRange = ref(null)
const dialogVisible = ref(false)
const current = ref(null)

const platformLabels = { booking: 'Booking.com', trip: 'Trip.com', agoda: 'Agoda', expedia: 'Expedia' }
const platformLabel = p => platformLabels[p] || p

function formatDateTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  if (isNaN(d.getTime())) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadData(p = page.value) {
  page.value = p
  loading.value = true
  try {
    const params = { page: p, per_page: pageSize }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value !== undefined && statusFilter.value !== null && statusFilter.value !== '') params.status = statusFilter.value
    if (dateRange.value?.length === 2) {
      params.date_start = dateRange.value[0]
      params.date_end = dateRange.value[1]
    }
    const res = await getGuestRegistrations(params)
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch {}
  loading.value = false
}

function openDetail(row) {
  current.value = row
  dialogVisible.value = true
}

async function onSetStatus(row, status) {
  try {
    await updateGuestRegistrationStatus(row.id, status)
    ElMessage.success(t('common.updated'))
    row.status = status
    if (current.value?.id === row.id) current.value.status = status
  } catch {}
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(t('guestReg.deleteConfirm'), t('common.warning'), { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteGuestRegistration(row.id)
    ElMessage.success(t('common.deleted'))
    loadData()
  } catch {}
}

function downloadDoc(key, name) {
  const url = guestDocUrl(key)
  const a = document.createElement('a')
  a.href = url
  a.download = name
  a.target = '_blank'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

function onExport() {
  const params = {}
  if (dateRange.value?.length === 2) {
    params.date_start = dateRange.value[0]
    params.date_end = dateRange.value[1]
  }
  window.open(guestRegistrationsExportUrl(params), '_blank')
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
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.photo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.photo-block {
  text-align: center;
}
.photo-label {
  font-size: 13px;
  font-weight: 600;
  color: #4a3728;
  margin-bottom: 8px;
}
.photo-img {
  width: 100%;
  height: 220px;
  border: 1px solid #ebe5df;
  border-radius: 8px;
  background: #faf7f2;
}
</style>
