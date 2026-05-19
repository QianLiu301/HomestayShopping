<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-select
          v-model="attractionFilter"
          clearable
          filterable
          style="width: 220px"
          :placeholder="tPackages.attractionPlaceholder"
          @change="loadData"
        >
          <el-option v-for="item in attractions" :key="item.id" :label="item.name_zh || item.name_en" :value="item.id" />
        </el-select>

        <el-select
          v-model="ticketTypeFilter"
          clearable
          style="width: 160px"
          :placeholder="tPackages.ticketType"
          @change="loadData"
        >
          <el-option v-for="item in ticketTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
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

        <el-input
          v-model="keyword"
          :placeholder="tPackages.searchPlaceholder"
          clearable
          style="width: 220px"
          @keyup.enter="loadData"
        />

        <el-button @click="loadData">{{ $t('common.search') }}</el-button>
      </div>

      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        {{ tPackages.addPackage }}
      </el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column :label="tPackages.attraction" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ getAttractionName(row.attraction_id) }}
          </template>
        </el-table-column>

        <el-table-column prop="package_name_zh" :label="tPackages.packageNameZh" min-width="160" show-overflow-tooltip />
        <el-table-column prop="package_name_en" :label="tPackages.packageNameEn" min-width="180" show-overflow-tooltip />

        <el-table-column :label="tPackages.ticketType" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ getTicketTypeLabel(row.ticket_type) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="sale_price" :label="tPackages.salePrice" width="100">
          <template #default="{ row }">¥{{ row.sale_price }}</template>
        </el-table-column>

        <el-table-column prop="original_price" :label="tPackages.originalPrice" width="100">
          <template #default="{ row }">{{ row.original_price ? `¥${row.original_price}` : '-' }}</template>
        </el-table-column>

        <el-table-column :label="tPackages.inventoryMode" width="140">
          <template #default="{ row }">
            {{ getInventoryModeLabel(row.inventory_mode) }}
          </template>
        </el-table-column>

        <el-table-column :label="tPackages.quota" width="120">
          <template #default="{ row }">
            <span v-if="row.inventory_mode === 'manual_quota'">
              {{ row.quota_used || 0 }} / {{ row.quota_total || 0 }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column :label="tPackages.dateRules" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.date_rules?.length">{{ formatDateRulesSummary(row.date_rules) }}</span>
            <span v-else-if="row.available_days?.length">{{ formatAvailableDaysSummary(row.available_days) }}</span>
            <span v-else>{{ tPackages.noDateRules }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="sort_order" :label="$t('common.sort')" width="80" />

        <el-table-column :label="$t('common.status')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? $t('common.active') : $t('common.hidden') }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="$t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">{{ $t('common.edit') }}</el-button>
            <el-popconfirm :title="tPackages.deleteConfirm" @confirm="onDelete(row.id)">
              <template #reference>
                <el-button link type="danger">{{ $t('common.delete') }}</el-button>
              </template>
            </el-popconfirm>
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
      :title="isEdit ? tPackages.editPackage : tPackages.addPackage"
      width="1080px"
      destroy-on-close
    >
      <el-form :model="form" label-position="top">
        <div class="section-title">{{ tPackages.basicInfo }}</div>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="tPackages.attraction" required>
              <el-select v-model="form.attraction_id" filterable style="width: 100%">
                <el-option v-for="item in attractions" :key="item.id" :label="item.name_zh || item.name_en" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="tPackages.ticketType" required>
              <el-select v-model="form.ticket_type" style="width: 100%">
                <el-option v-for="item in ticketTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tPackages.packageNameEn" required><el-input v-model="form.package_name_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.packageNameZh"><el-input v-model="form.package_name_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.packageNameRu"><el-input v-model="form.package_name_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.packageNameEs"><el-input v-model="form.package_name_es" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tPackages.pricing }}</div>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item :label="tPackages.salePrice" required><el-input-number v-model="form.sale_price" :min="0" :precision="2" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="tPackages.originalPrice"><el-input-number v-model="form.original_price" :min="0" :precision="2" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('common.sort')"><el-input-number v-model="form.sort_order" :min="0" style="width: 100%" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tPackages.inventory }}</div>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item :label="tPackages.inventoryMode">
              <el-select v-model="form.inventory_mode" style="width: 100%">
                <el-option v-for="item in inventoryModeOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="tPackages.quotaTotal">
              <el-input-number v-model="form.quota_total" :min="0" :disabled="form.inventory_mode !== 'manual_quota'" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="tPackages.availableDays">
              <el-input :model-value="dateRulesSummary" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="section-title section-title-row">
          <span>{{ tPackages.dateRules }}</span>
          <el-button size="small" type="primary" plain @click="addDateRule">
            <el-icon><Plus /></el-icon>
            {{ tPackages.addDateRule }}
          </el-button>
        </div>
        <div class="date-rules-tip">{{ tPackages.dateRulesTip }}</div>
        <el-table :data="dateRules" size="small" border class="date-rules-table" empty-text="No rules">
          <el-table-column :label="tPackages.ruleDate" width="180">
            <template #default="{ row }">
              <el-date-picker v-model="row.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column :label="tPackages.ruleStatus" width="120">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" />
            </template>
          </el-table-column>
          <el-table-column :label="tPackages.rulePrice" width="180">
            <template #default="{ row }">
              <el-input-number v-model="row.price" :min="0" :precision="2" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column :label="tPackages.ruleTag" min-width="160">
            <template #default="{ row }">
              <el-input v-model="row.tag" :placeholder="tPackages.ruleTagPlaceholder" />
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.actions')" width="100">
            <template #default="{ $index }">
              <el-button link type="danger" @click="removeDateRule($index)">{{ $t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="section-title">{{ tPackages.ageRule }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tPackages.ageRuleEn"><el-input v-model="form.age_rule_en" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.ageRuleZh"><el-input v-model="form.age_rule_zh" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.ageRuleRu"><el-input v-model="form.age_rule_ru" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.ageRuleEs"><el-input v-model="form.age_rule_es" type="textarea" :rows="3" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tPackages.bookingNotice }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tPackages.bookingNoticeEn"><el-input v-model="form.booking_notice_en" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.bookingNoticeZh"><el-input v-model="form.booking_notice_zh" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.bookingNoticeRu"><el-input v-model="form.booking_notice_ru" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.bookingNoticeEs"><el-input v-model="form.booking_notice_es" type="textarea" :rows="3" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tPackages.refundRule }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tPackages.refundRuleEn"><el-input v-model="form.refund_rule_en" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.refundRuleZh"><el-input v-model="form.refund_rule_zh" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.refundRuleRu"><el-input v-model="form.refund_rule_ru" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tPackages.refundRuleEs"><el-input v-model="form.refund_rule_es" type="textarea" :rows="3" /></el-form-item></el-col>
        </el-row>

        <el-row :gutter="16">
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
  getTicketPackages,
  createTicketPackage,
  updateTicketPackage,
  deleteTicketPackage
} from '../api/tickets'

const { t, messages, locale } = useI18n()
const tPackages = computed(() => messages.value[locale.value]?.ticketPackages || {})

const list = ref([])
const attractions = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const page = ref(1)
const pageSize = 15
const total = ref(0)
const keyword = ref('')
const attractionFilter = ref(undefined)
const ticketTypeFilter = ref('')
const statusFilter = ref(undefined)
const dateRules = ref([])

const ticketTypeOptions = computed(() => [
  { value: 'adult', label: tPackages.value.adult || '成人票' },
  { value: 'child', label: tPackages.value.child || '儿童票' },
  { value: 'senior', label: tPackages.value.senior || '老人票' },
  { value: 'family', label: tPackages.value.family || '家庭票' },
  { value: 'combo', label: tPackages.value.combo || '套餐票' }
])

const inventoryModeOptions = computed(() => [
  { value: 'unlimited', label: tPackages.value.unlimited || '不限库存' },
  { value: 'manual_quota', label: tPackages.value.manualQuota || '手动配额' }
])

const defaultForm = () => ({
  attraction_id: null,
  package_name_en: '', package_name_zh: '', package_name_ru: '', package_name_es: '',
  ticket_type: 'adult',
  sale_price: 0,
  original_price: null,
  age_rule_en: '', age_rule_zh: '', age_rule_ru: '', age_rule_es: '',
  booking_notice_en: '', booking_notice_zh: '', booking_notice_ru: '', booking_notice_es: '',
  refund_rule_en: '', refund_rule_zh: '', refund_rule_ru: '', refund_rule_es: '',
  inventory_mode: 'unlimited',
  quota_total: null,
  available_days: null,
  date_rules: null,
  sort_order: 0,
  status: 1
})

const form = reactive(defaultForm())

const dateRulesSummary = computed(() => {
  if (!dateRules.value.length) return tPackages.value.noDateRules || '未配置'
  return `${dateRules.value.length} ${tPackages.value.datesConfigured || '个日期规则'}`
})

function createEmptyDateRule() {
  return {
    date: '',
    enabled: true,
    price: null,
    tag: ''
  }
}

function normalizeDateRule(rule) {
  return {
    date: rule?.date || '',
    enabled: rule?.enabled !== false,
    price: rule?.price !== undefined && rule?.price !== null && rule?.price !== '' ? Number(rule.price) : null,
    tag: rule?.tag || ''
  }
}

function addDateRule() {
  dateRules.value.push(createEmptyDateRule())
}

function removeDateRule(index) {
  dateRules.value.splice(index, 1)
}

async function loadAttractions() {
  try {
    const res = await getTicketAttractions({ page: 1, per_page: 200, status: 1 })
    attractions.value = res.data?.list || []
  } catch {}
}

async function loadData() {
  loading.value = true
  try {
    const res = await getTicketPackages({
      page: page.value,
      per_page: pageSize,
      attraction_id: attractionFilter.value,
      ticket_type: ticketTypeFilter.value,
      status: statusFilter.value,
      keyword: keyword.value
    })
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch {}
  loading.value = false
}

function getAttractionName(id) {
  const item = attractions.value.find(v => v.id === id)
  return item ? (item.name_zh || item.name_en) : '-'
}

function getTicketTypeLabel(value) {
  return ticketTypeOptions.value.find(item => item.value === value)?.label || value || '-'
}

function getInventoryModeLabel(value) {
  return inventoryModeOptions.value.find(item => item.value === value)?.label || value || '-'
}

function formatDateRulesSummary(rules) {
  if (!Array.isArray(rules) || !rules.length) return tPackages.value.noDateRules || '未配置'
  const preview = rules
    .filter(item => item?.date)
    .slice(0, 3)
    .map(item => `${item.date}${item.tag ? `(${item.tag})` : ''}`)
    .join(', ')
  return `${preview}${rules.length > 3 ? '...' : ''}`
}

function formatAvailableDaysSummary(days) {
  if (!Array.isArray(days) || !days.length) return tPackages.value.noDateRules || '未配置'
  const preview = days.slice(0, 3).join(', ')
  return `${preview}${days.length > 3 ? '...' : ''}`
}

function openDialog(row) {
  Object.assign(form, defaultForm())
  dateRules.value = []

  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.keys(form).forEach(k => {
      if (row[k] !== undefined && row[k] !== null) form[k] = row[k]
    })

    if (Array.isArray(row.date_rules) && row.date_rules.length) {
      dateRules.value = row.date_rules.map(normalizeDateRule)
    } else if (Array.isArray(row.available_days) && row.available_days.length) {
      dateRules.value = row.available_days.map(date => normalizeDateRule({ date, enabled: true, price: row.sale_price, tag: '' }))
    }
  } else {
    isEdit.value = false
    editId.value = null
  }

  dialogVisible.value = true
}

async function onSave() {
  if (!form.attraction_id) {
    ElMessage.error(tPackages.value.attractionRequired || '请选择所属景点')
    return
  }
  if (!form.package_name_en && !form.package_name_zh) {
    ElMessage.error(tPackages.value.packageNameRequired || '票种名称不能为空')
    return
  }
  if (form.sale_price === null || form.sale_price === undefined) {
    ElMessage.error(tPackages.value.salePriceRequired || '请填写售价')
    return
  }

  const normalizedDateRules = dateRules.value
    .filter(item => item.date)
    .map(item => ({
      date: item.date,
      enabled: item.enabled !== false,
      price: item.price !== null && item.price !== undefined && item.price !== '' ? Number(item.price) : Number(form.sale_price),
      tag: item.tag || ''
    }))

  saving.value = true
  try {
    const payload = {
      ...form,
      date_rules: normalizedDateRules.length ? normalizedDateRules : null,
      available_days: normalizedDateRules.length ? normalizedDateRules.filter(item => item.enabled).map(item => item.date) : null,
      quota_total: form.inventory_mode === 'manual_quota' ? form.quota_total : null
    }

    if (isEdit.value) {
      await updateTicketPackage(editId.value, payload)
      ElMessage.success(t('common.updated'))
    } else {
      await createTicketPackage(payload)
      ElMessage.success(t('common.created'))
    }

    dialogVisible.value = false
    loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try {
    await deleteTicketPackage(id)
    ElMessage.success(t('common.deleted'))
    loadData()
  } catch {}
}

onMounted(async () => {
  await loadAttractions()
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

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #4a3728;
  margin: 8px 0 12px;
}

.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.date-rules-tip {
  margin-bottom: 12px;
  font-size: 12px;
  color: #8a7b6b;
  line-height: 1.6;
}

.date-rules-table {
  margin-bottom: 16px;
}
</style>
