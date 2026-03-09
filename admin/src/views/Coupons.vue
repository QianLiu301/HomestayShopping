<template>
  <div>
    <div class="page-header">
      <span></span>
      <el-button type="primary" @click="openDialog()"><el-icon><Plus /></el-icon> {{ $t('coupons.addCoupon') }}</el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="code" :label="$t('coupons.code')" width="140" />
        <el-table-column prop="name_en" :label="$t('coupons.nameEn')" min-width="160" />
        <el-table-column :label="$t('coupons.discountValue')" width="130">
          <template #default="{ row }">
            {{ row.discount_type === 'percent' ? `${row.discount_value}%` : `¥${row.discount_value}` }}
          </template>
        </el-table-column>
        <el-table-column prop="apply_to" :label="$t('coupons.applyTo')" width="100" />
        <el-table-column :label="$t('coupons.usage')" width="100">
          <template #default="{ row }">{{ row.used_count }} / {{ row.total_count || '∞' }}</template>
        </el-table-column>
        <el-table-column prop="end_time" :label="$t('coupons.expires')" width="170" />
        <el-table-column :label="$t('common.status')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? $t('common.active') : $t('common.disabled') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">{{ $t('common.edit') }}</el-button>
            <el-popconfirm :title="$t('coupons.deleteConfirm')" @confirm="onDelete(row.id)">
              <template #reference><el-button link type="danger">{{ $t('common.delete') }}</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? $t('coupons.editCoupon') : $t('coupons.addCoupon')" width="600px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="$t('coupons.code')" required><el-input v-model="form.code" placeholder="e.g. WELCOME10" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('coupons.applyTo')"><el-select v-model="form.apply_to" style="width:100%"><el-option :label="$t('coupons.all')" value="all" /><el-option :label="$t('coupons.shop')" value="shop" /><el-option :label="$t('coupons.transferLabel')" value="transfer" /></el-select></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="$t('coupons.nameEn')"><el-input v-model="form.name_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('coupons.nameZh')"><el-input v-model="form.name_zh" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item :label="$t('coupons.discountType')"><el-select v-model="form.discount_type" style="width:100%"><el-option :label="$t('coupons.fixedAmount')" value="fixed" /><el-option :label="$t('coupons.percentage')" value="percent" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('coupons.discountValue')" required><el-input-number v-model="form.discount_value" :min="0" :precision="2" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('coupons.minAmount')"><el-input-number v-model="form.min_amount" :min="0" :precision="2" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item :label="$t('coupons.maxDiscount')"><el-input-number v-model="form.max_discount" :min="0" :precision="2" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('coupons.totalCount')"><el-input-number v-model="form.total_count" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('coupons.perUserLimit')"><el-input-number v-model="form.per_limit" :min="1" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="$t('coupons.startTime')"><el-date-picker v-model="form.start_time" type="datetime" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="$t('coupons.endTime')"><el-date-picker v-model="form.end_time" type="datetime" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item :label="$t('common.status')"><el-radio-group v-model="form.status"><el-radio :value="1">{{ $t('common.active') }}</el-radio><el-radio :value="0">{{ $t('common.disabled') }}</el-radio></el-radio-group></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">{{ $t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getCoupons, createCoupon, updateCoupon, deleteCoupon } from '../api'

const { t } = useI18n()
const list = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const page = ref(1)
const pageSize = 15
const total = ref(0)

const defaultForm = () => ({ code: '', name_en: '', name_zh: '', discount_type: 'fixed', discount_value: 0, min_amount: 0, max_discount: null, apply_to: 'all', total_count: null, per_limit: 1, start_time: null, end_time: null, status: 1 })
const form = reactive(defaultForm())

async function loadData() {
  loading.value = true
  try {
    const res = await getCoupons({ page: page.value, per_page: pageSize })
    list.value = res.data?.list || res.data?.items || []
    total.value = res.data?.total || list.value.length
  } catch {}
  loading.value = false
}

function openDialog(row) {
  Object.assign(form, defaultForm())
  if (row) { isEdit.value = true; editId.value = row.id; Object.keys(form).forEach(k => { if (row[k] !== undefined) form[k] = row[k] }) }
  else { isEdit.value = false; editId.value = null }
  dialogVisible.value = true
}

async function onSave() {
  if (!form.code) return ElMessage.warning(t('coupons.codeRequired'))
  saving.value = true
  try {
    if (isEdit.value) { await updateCoupon(editId.value, form); ElMessage.success(t('common.updated')) }
    else { await createCoupon(form); ElMessage.success(t('common.created')) }
    dialogVisible.value = false; loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try { await deleteCoupon(id); ElMessage.success(t('common.deleted')); loadData() } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; margin-bottom: 16px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
