<template>
  <div class="guest-reg-page">
    <div class="page-header">
      <div class="header-filters">
        <el-radio-group v-model="viewMode" @change="onViewChange">
          <el-radio-button value="grouped">{{ $t('guestReg.groupedView') }}</el-radio-button>
          <el-radio-button value="all">{{ $t('guestReg.allView') }}</el-radio-button>
        </el-radio-group>
        <el-input
          v-model="keyword"
          :placeholder="$t('guestReg.searchPlaceholder')"
          clearable
          style="width: 240px"
          @keyup.enter="reload"
          @clear="reload"
        >
          <template #append>
            <el-button :icon="Search" @click="reload" />
          </template>
        </el-input>
        <el-select
          v-if="viewMode === 'all'"
          v-model="statusFilter"
          :placeholder="$t('guestReg.statusFilter')"
          clearable
          style="width: 130px"
          @change="reload"
        >
          <el-option :label="$t('guestReg.pending')" :value="0" />
          <el-option :label="$t('guestReg.declared')" :value="1" />
          <el-option :label="$t('guestReg.cancelledStatus')" :value="2" />
        </el-select>
        <el-date-picker
          v-model="filterDate"
          type="date"
          value-format="YYYY-MM-DD"
          :placeholder="$t('guestReg.filterDate')"
          clearable
          style="width: 170px"
          @change="reload"
        />
        <el-button size="default" plain @click="setToday">{{ $t('guestReg.today') }}</el-button>
      </div>
      <div class="header-actions">
        <el-button
          v-if="viewMode === 'all'"
          type="primary"
          plain
          :disabled="selectedIds.length < 2"
          @click="onMerge"
        >{{ $t('guestReg.mergeBtn') }}</el-button>
        <el-button type="success" plain :icon="Download" @click="onExport">
          {{ filterDate ? $t('guestReg.exportDayBtn') : $t('guestReg.exportBtn') }}
        </el-button>
      </div>
    </div>

    <!-- ===== 按订单分组视图 ===== -->
    <template v-if="viewMode === 'grouped'">
      <el-table v-loading="loading" :data="groups" row-key="key" stripe>
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="group-members">
              <el-table :data="row.items" size="small" border style="min-width: 960px">
                <el-table-column prop="id" label="ID" width="60" />
                <el-table-column :label="$t('guestReg.name')" min-width="140">
                  <template #default="{ row: m }"><span style="font-weight:600">{{ m.full_name }}</span></template>
                </el-table-column>
                <el-table-column :label="$t('guestReg.dob')" width="110">
                  <template #default="{ row: m }">{{ m.date_of_birth || '-' }}</template>
                </el-table-column>
                <el-table-column :label="$t('guestReg.docType')" width="100">
                  <template #default="{ row: m }">{{ docTypeLabel(m.document_type) }}</template>
                </el-table-column>
                <el-table-column prop="document_no" :label="$t('guestReg.docNo')" min-width="120" show-overflow-tooltip />
                <el-table-column :label="$t('guestReg.photos')" width="100">
                  <template #default="{ row: m }">
                    <el-button link type="primary" size="small" @click="openDetail(m)">{{ $t('guestReg.viewPhotos') }}</el-button>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('guestReg.status')" width="90">
                  <template #default="{ row: m }">
                    <el-tag :type="statusType(m.status)" size="small">{{ statusLabel(m.status) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="$t('common.actions')" width="260">
                  <template #default="{ row: m }">
                    <template v-if="m.status === 2">
                      <el-button link type="primary" size="small" @click="onSetStatus(m, 0)">{{ $t('guestReg.restorePending') }}</el-button>
                    </template>
                    <template v-else>
                      <el-button v-if="m.status === 0" link type="success" size="small" @click="onSetStatus(m, 1)">{{ $t('guestReg.markDeclared') }}</el-button>
                      <el-button v-else link type="warning" size="small" @click="onSetStatus(m, 0)">{{ $t('guestReg.markPending') }}</el-button>
                      <el-button link type="info" size="small" @click="onSetStatus(m, 2)">{{ $t('guestReg.markCancelled') }}</el-button>
                    </template>
                    <el-button v-if="row.count > 1" link size="small" @click="onUngroup(m)">{{ $t('guestReg.ungroup') }}</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.roomNote')" min-width="150">
          <template #default="{ row }">
            <span :style="{ fontWeight: 600, color: row.room_note ? '#4a3728' : '#c0b6a8' }">
              {{ row.room_note || $t('guestReg.noNote') }}
            </span>
            <el-button link type="primary" size="small" :icon="EditPen" @click="onEditRoomNote(row)" />
          </template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.platform')" width="110">
          <template #default="{ row }">{{ platformLabel(row.platform) }}</template>
        </el-table-column>
        <el-table-column prop="booking_no" :label="$t('guestReg.bookingNo')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="$t('guestReg.guests')" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.groupStatus')" width="160">
          <template #default="{ row }">
            <el-tag v-if="activeCount(row) === 0" type="info" size="small">{{ $t('guestReg.cancelledStatus') }}</el-tag>
            <el-tag v-else :type="row.declared_count === activeCount(row) ? 'success' : (row.declared_count > 0 ? 'primary' : 'warning')" size="small">
              {{ row.declared_count }} / {{ activeCount(row) }} {{ $t('guestReg.declared') }}
            </el-tag>
            <span v-if="row.cancelled_count && activeCount(row) > 0" class="cancelled-hint">
              {{ $t('guestReg.cancelledSuffix', { count: row.cancelled_count }) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.stayDates')" width="180">
          <template #default="{ row }">
            <span v-if="row.checkin_date">{{ row.checkin_date }} ~ {{ row.checkout_date || '?' }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.createdAt')" width="150">
          <template #default="{ row }">{{ formatDateTime(row.latest_at) }}</template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="230" fixed="right">
          <template #default="{ row }">
            <template v-if="activeCount(row) === 0">
              <el-button link type="primary" size="small" @click="onMarkGroup(row, 0, true)">{{ $t('guestReg.restorePending') }}</el-button>
            </template>
            <template v-else>
              <el-button
                v-if="row.declared_count < activeCount(row)"
                link
                type="success"
                size="small"
                @click="onMarkGroup(row, 1)"
              >{{ $t('guestReg.markGroupDeclared') }}</el-button>
              <el-button
                v-else
                link
                type="warning"
                size="small"
                @click="onMarkGroup(row, 0)"
              >{{ $t('guestReg.markGroupPending') }}</el-button>
              <el-button link type="info" size="small" @click="onCancelGroup(row)">{{ $t('guestReg.markGroupCancelled') }}</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="groupPage"
          :page-size="groupPageSize"
          :total="groupTotal"
          layout="total, prev, pager, next"
          @current-change="loadGroups"
        />
      </div>
    </template>

    <!-- ===== 全部记录视图 ===== -->
    <template v-else>
      <el-table v-loading="loading" :data="list" stripe @selection-change="onSelectionChange">
        <el-table-column type="selection" width="45" />
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column :label="$t('guestReg.name')" min-width="150">
          <template #default="{ row }">
            <span style="font-weight:600">{{ row.full_name }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.roomNote')" min-width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ row.room_note || '-' }}</template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.dob')" width="110">
          <template #default="{ row }">{{ row.date_of_birth || '-' }}</template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.docType')" width="105">
          <template #default="{ row }">{{ docTypeLabel(row.document_type) }}</template>
        </el-table-column>
        <el-table-column prop="document_no" :label="$t('guestReg.docNo')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="booking_no" :label="$t('guestReg.bookingNo')" min-width="130" show-overflow-tooltip />
        <el-table-column :label="$t('guestReg.stayDates')" width="175">
          <template #default="{ row }">
            <span v-if="row.checkin_date">{{ row.checkin_date }} ~ {{ row.checkout_date || '?' }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.photos')" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDetail(row)">{{ $t('guestReg.viewPhotos') }}</el-button>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.status')" width="95">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guestReg.createdAt')" width="150">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="200" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 2">
              <el-button link type="primary" size="small" @click="onSetStatus(row, 0)">{{ $t('guestReg.restorePending') }}</el-button>
            </template>
            <template v-else>
              <el-button v-if="row.status === 0" link type="success" size="small" @click="onSetStatus(row, 1)">{{ $t('guestReg.markDeclared') }}</el-button>
              <el-button v-else link type="warning" size="small" @click="onSetStatus(row, 0)">{{ $t('guestReg.markPending') }}</el-button>
              <el-button link type="info" size="small" @click="onSetStatus(row, 2)">{{ $t('guestReg.markCancelled') }}</el-button>
            </template>
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
    </template>

    <!-- 详情/照片弹窗 -->
    <el-dialog v-model="dialogVisible" :title="$t('guestReg.detailTitle')" width="720px">
      <template v-if="current">
        <el-descriptions :column="2" border style="margin-bottom:16px">
          <el-descriptions-item :label="$t('guestReg.name')">{{ current.full_name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.dob')">{{ current.date_of_birth }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.docType')">{{ docTypeLabel(current.document_type) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.docNo')">{{ current.document_no || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.platform')">{{ platformLabel(current.platform) }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.bookingNo')">{{ current.booking_no }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.checkinDate')">{{ current.checkin_date || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.checkoutDate')">{{ current.checkout_date || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.roomNote')">{{ current.room_note || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="$t('guestReg.status')">
            <el-tag :type="statusType(current.status)" size="small">{{ statusLabel(current.status) }}</el-tag>
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
import { Search, Download, EditPen } from '@element-plus/icons-vue'
import {
  getGuestRegistrations,
  getGuestRegistrationsGrouped,
  updateGuestRegistrationStatus,
  batchGuestRegistrationStatus,
  setGuestRegistrationRoomNote,
  mergeGuestRegistrations,
  ungroupGuestRegistration,
  guestDocUrl,
  guestRegistrationsExportUrl,
} from '../api'

const { t } = useI18n()

const viewMode = ref('grouped')
const loading = ref(false)
const keyword = ref('')
const statusFilter = ref(undefined)
const filterDate = ref(null)

function setToday() {
  const d = new Date()
  const pad = n => String(n).padStart(2, '0')
  filterDate.value = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
  reload()
}
const dialogVisible = ref(false)
const current = ref(null)

// 全部记录视图
const list = ref([])
const page = ref(1)
const pageSize = 15
const total = ref(0)
const selectedIds = ref([])

// 分组视图
const groups = ref([])
const groupPage = ref(1)
const groupPageSize = 10
const groupTotal = ref(0)

const platformLabels = { booking: 'Booking.com', trip: 'Trip.com', agoda: 'Agoda', expedia: 'Expedia' }
const platformLabel = p => platformLabels[p] || p

const docTypeLabels = { passport: t('guestReg.docPassport'), hkmo: t('guestReg.docHkMo'), taiwan: t('guestReg.docTaiwan') }
const docTypeLabel = d => docTypeLabels[d || 'passport'] || d

// 申报状态：0待申报 1已申报 2已取消
const statusLabel = s => (s === 1 ? t('guestReg.declared') : s === 2 ? t('guestReg.cancelledStatus') : t('guestReg.pending'))
const statusType = s => (s === 1 ? 'success' : s === 2 ? 'info' : 'warning')
// 组内有效人数（排除已取消）
const activeCount = g => g.count - (g.cancelled_count || 0)

function formatDateTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  if (isNaN(d.getTime())) return val
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function commonParams() {
  const params = {}
  if (keyword.value) params.keyword = keyword.value
  // 按入住日期筛选：选中某天 → 只看当天入住的客人
  if (filterDate.value) {
    params.checkin_date = filterDate.value
  }
  return params
}

function reload() {
  if (viewMode.value === 'grouped') loadGroups(1)
  else loadData(1)
}

function onViewChange() {
  reload()
}

async function loadGroups(p = groupPage.value) {
  groupPage.value = p
  loading.value = true
  try {
    const res = await getGuestRegistrationsGrouped({ ...commonParams(), page: p, per_page: groupPageSize })
    groups.value = res.data?.list || []
    groupTotal.value = res.data?.total || 0
  } catch {}
  loading.value = false
}

async function loadData(p = page.value) {
  page.value = p
  loading.value = true
  try {
    const params = { ...commonParams(), page: p, per_page: pageSize }
    if (statusFilter.value !== undefined && statusFilter.value !== null && statusFilter.value !== '') params.status = statusFilter.value
    const res = await getGuestRegistrations(params)
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch {}
  loading.value = false
}

function onSelectionChange(rows) {
  selectedIds.value = rows.map(r => r.id)
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
    if (viewMode.value === 'grouped') loadGroups()
  } catch {}
}

async function onMarkGroup(group, status, includeCancelled = false) {
  try {
    // 默认只更新未取消的成员；恢复整组时（includeCancelled）才包含已取消的
    const ids = group.items.filter(m => includeCancelled || m.status !== 2).map(m => m.id)
    if (!ids.length) return
    await batchGuestRegistrationStatus(ids, status)
    ElMessage.success(t('common.updated'))
    loadGroups()
  } catch {}
}

async function onCancelGroup(group) {
  try {
    await ElMessageBox.confirm(t('guestReg.groupCancelConfirm'), t('common.warning'), { type: 'warning' })
  } catch {
    return
  }
  try {
    const ids = group.items.map(m => m.id)
    await batchGuestRegistrationStatus(ids, 2)
    ElMessage.success(t('common.updated'))
    loadGroups()
  } catch {}
}

async function onEditRoomNote(group) {
  let value
  try {
    const res = await ElMessageBox.prompt(t('guestReg.roomNotePrompt'), t('guestReg.roomNote'), {
      inputValue: group.room_note || '',
      inputPlaceholder: t('guestReg.roomNotePlaceholder'),
      confirmButtonText: t('common.save'),
      cancelButtonText: t('common.cancel'),
    })
    value = res.value
  } catch {
    return
  }
  try {
    const ids = group.items.map(m => m.id)
    await setGuestRegistrationRoomNote(ids, value || '')
    ElMessage.success(t('guestReg.noteSaved'))
    loadGroups()
  } catch {}
}

async function onMerge() {
  if (selectedIds.value.length < 2) {
    return ElMessage.warning(t('guestReg.selectAtLeastTwo'))
  }
  try {
    await ElMessageBox.confirm(t('guestReg.mergeConfirm', { count: selectedIds.value.length }), t('common.warning'), { type: 'info' })
  } catch {
    return
  }
  try {
    await mergeGuestRegistrations(selectedIds.value)
    ElMessage.success(t('guestReg.mergeSuccess'))
    loadData()
  } catch {}
}

async function onUngroup(row) {
  try {
    await ungroupGuestRegistration(row.id)
    ElMessage.success(t('common.updated'))
    loadGroups()
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
  // 选了入住日期 → 只导出当天入住的客人；未选 → 默认导出近一个月的登记
  if (filterDate.value) {
    params.checkin_date = filterDate.value
  }
  window.open(guestRegistrationsExportUrl(params), '_blank')
}

onMounted(() => reload())
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
.header-actions {
  display: flex;
  gap: 8px;
}
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.group-members {
  padding: 8px 16px 12px 48px;
  background: #fdfaf5;
  overflow-x: auto;
}
.cancelled-hint {
  margin-left: 6px;
  font-size: 12px;
  color: #909399;
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
