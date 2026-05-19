<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input
          v-model="keyword"
          :placeholder="tAttractions.searchPlaceholder"
          clearable
          style="width: 240px"
          @keyup.enter="loadData"
        />
        <el-input
          v-model="cityFilter"
          :placeholder="tAttractions.cityPlaceholder"
          clearable
          style="width: 180px"
          @keyup.enter="loadData"
        />
        <el-select v-model="statusFilter" clearable style="width: 140px" @change="loadData">
          <el-option :label="$t('common.active')" :value="1" />
          <el-option :label="$t('common.hidden')" :value="0" />
        </el-select>
        <el-button @click="loadData">{{ $t('common.search') }}</el-button>
      </div>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        {{ tAttractions.addAttraction }}
      </el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column :label="$t('common.image')" width="86">
          <template #default="{ row }">
            <el-image
              v-if="row.cover_image"
              :src="resolveUrl(row.cover_image)"
              style="width: 52px; height: 52px; border-radius: 8px"
              fit="cover"
            />
            <div
              v-else
              style="width:52px;height:52px;border-radius:8px;background:#f5efe6;display:flex;align-items:center;justify-content:center;color:#c8a97e;font-size:20px"
            >🎫</div>
          </template>
        </el-table-column>

        <el-table-column prop="name_zh" :label="tAttractions.nameZh" min-width="140" show-overflow-tooltip />
        <el-table-column prop="name_en" :label="tAttractions.nameEn" min-width="160" show-overflow-tooltip />
        <el-table-column prop="city" :label="tAttractions.city" width="120" />
        <el-table-column prop="category" :label="tAttractions.category" width="120" />

        <el-table-column :label="tAttractions.featured" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.featured" type="warning" size="small">{{ $t('common.yes') }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column :label="tAttractions.realNameRequired" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.real_name_required ? 'danger' : 'info'" size="small">
              {{ row.real_name_required ? $t('common.yes') : $t('common.no') }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="tAttractions.passportRequired" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.passport_required ? 'danger' : 'info'" size="small">
              {{ row.passport_required ? $t('common.yes') : $t('common.no') }}
            </el-tag>
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
            <el-popconfirm :title="tAttractions.deleteConfirm" @confirm="onDelete(row.id)">
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
      :title="isEdit ? tAttractions.editAttraction : tAttractions.addAttraction"
      width="1100px"
      destroy-on-close
    >
      <el-form :model="form" label-position="top">
        <div class="section-title">{{ tAttractions.basicInfo }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tAttractions.nameEn" required><el-input v-model="form.name_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.nameZh"><el-input v-model="form.name_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.nameRu"><el-input v-model="form.name_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.nameEs"><el-input v-model="form.name_es" /></el-form-item></el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tAttractions.subtitleEn"><el-input v-model="form.subtitle_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.subtitleZh"><el-input v-model="form.subtitle_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.subtitleRu"><el-input v-model="form.subtitle_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.subtitleEs"><el-input v-model="form.subtitle_es" /></el-form-item></el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="8"><el-form-item :label="tAttractions.city"><el-input v-model="form.city" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="tAttractions.category"><el-input v-model="form.category" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="tAttractions.tags"><el-input v-model="tagsText" :placeholder="tAttractions.tagsPlaceholder" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tAttractions.addressInfo }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tAttractions.addressEn"><el-input v-model="form.address_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.addressZh"><el-input v-model="form.address_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.addressRu"><el-input v-model="form.address_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.addressEs"><el-input v-model="form.address_es" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tAttractions.openHours }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tAttractions.openHoursEn"><el-input v-model="form.open_hours_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.openHoursZh"><el-input v-model="form.open_hours_zh" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.openHoursRu"><el-input v-model="form.open_hours_ru" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.openHoursEs"><el-input v-model="form.open_hours_es" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tAttractions.description }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tAttractions.descEn"><el-input v-model="form.desc_en" type="textarea" :rows="4" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.descZh"><el-input v-model="form.desc_zh" type="textarea" :rows="4" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.descRu"><el-input v-model="form.desc_ru" type="textarea" :rows="4" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.descEs"><el-input v-model="form.desc_es" type="textarea" :rows="4" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tAttractions.visitNotice }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tAttractions.visitNoticeEn"><el-input v-model="form.visit_notice_en" type="textarea" :rows="4" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.visitNoticeZh"><el-input v-model="form.visit_notice_zh" type="textarea" :rows="4" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.visitNoticeRu"><el-input v-model="form.visit_notice_ru" type="textarea" :rows="4" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.visitNoticeEs"><el-input v-model="form.visit_notice_es" type="textarea" :rows="4" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tAttractions.refundRule }}</div>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tAttractions.refundRuleEn"><el-input v-model="form.refund_rule_en" type="textarea" :rows="4" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.refundRuleZh"><el-input v-model="form.refund_rule_zh" type="textarea" :rows="4" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.refundRuleRu"><el-input v-model="form.refund_rule_ru" type="textarea" :rows="4" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.refundRuleEs"><el-input v-model="form.refund_rule_es" type="textarea" :rows="4" /></el-form-item></el-col>
        </el-row>

        <div class="section-title">{{ tAttractions.images }}</div>
        <el-form-item :label="tAttractions.gallery">
          <el-upload
            :file-list="fileList"
            list-type="picture-card"
            :http-request="handleUpload"
            :before-upload="beforeUpload"
            :on-remove="handleRemove"
            multiple
            accept="image/*"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="field-tip">{{ tAttractions.uploadTip }}</div>
        </el-form-item>

        <div v-if="form.images.length" class="gallery-grid">
          <div
            v-for="(img, index) in form.images"
            :key="`${img}-${index}`"
            class="gallery-item"
            :class="{ active: index === 0 }"
          >
            <el-image :src="resolveUrl(img)" fit="cover" class="gallery-image" />
            <div class="gallery-actions">
              <el-button size="small" @click="setPrimary(index)">
                {{ index === 0 ? tAttractions.coverImage : tAttractions.setAsCover }}
              </el-button>
              <el-button size="small" type="danger" @click="removeImage(index)">{{ $t('common.delete') }}</el-button>
            </div>
          </div>
        </div>

        <div class="section-title">{{ tAttractions.settings }}</div>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item :label="$t('common.sort')"><el-input-number v-model="form.sort_order" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="tAttractions.featured"><el-switch v-model="form.featured" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item :label="$t('common.status')"><el-radio-group v-model="form.status"><el-radio :value="1">{{ $t('common.active') }}</el-radio><el-radio :value="0">{{ $t('common.hidden') }}</el-radio></el-radio-group></el-form-item></el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12"><el-form-item :label="tAttractions.realNameRequired"><el-switch v-model="form.real_name_required" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="tAttractions.passportRequired"><el-switch v-model="form.passport_required" /></el-form-item></el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving || uploading" :disabled="uploading" @click="onSave">
          {{ $t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { uploadFile, resolveUrl } from '../api'
import {
  getTicketAttractions,
  createTicketAttraction,
  updateTicketAttraction,
  deleteTicketAttraction
} from '../api/tickets'

const { t, messages, locale } = useI18n()
const tAttractions = computed(() => messages.value[locale.value]?.ticketAttractions || {})

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const fileList = ref([])
const page = ref(1)
const pageSize = 15
const total = ref(0)
const keyword = ref('')
const cityFilter = ref('')
const statusFilter = ref(undefined)
const tagsText = ref('')

const defaultForm = () => ({
  name_en: '', name_zh: '', name_ru: '', name_es: '',
  subtitle_en: '', subtitle_zh: '', subtitle_ru: '', subtitle_es: '',
  desc_en: '', desc_zh: '', desc_ru: '', desc_es: '',
  address_en: '', address_zh: '', address_ru: '', address_es: '',
  open_hours_en: '', open_hours_zh: '', open_hours_ru: '', open_hours_es: '',
  visit_notice_en: '', visit_notice_zh: '', visit_notice_ru: '', visit_notice_es: '',
  refund_rule_en: '', refund_rule_zh: '', refund_rule_ru: '', refund_rule_es: '',
  city: '', category: '', tags: [], cover_image: '', images: [],
  featured: false, real_name_required: false, passport_required: false,
  sort_order: 0, status: 1
})
const form = reactive(defaultForm())

async function loadData() {
  loading.value = true
  try {
    const res = await getTicketAttractions({
      page: page.value,
      per_page: pageSize,
      keyword: keyword.value,
      city: cityFilter.value,
      status: statusFilter.value
    })
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch {}
  loading.value = false
}

function syncFileList() {
  fileList.value = (form.images || []).map((img, index) => ({
    name: `attraction-${index + 1}`,
    url: resolveUrl(img),
    uid: `${img}-${index}`
  }))
}

function openDialog(row) {
  Object.assign(form, defaultForm())
  fileList.value = []
  tagsText.value = ''

  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.keys(form).forEach(k => {
      if (row[k] !== undefined && row[k] !== null) form[k] = row[k]
    })
    form.images = Array.isArray(row.images) ? [...row.images] : []
    form.cover_image = row.cover_image || form.images[0] || ''
    tagsText.value = Array.isArray(row.tags) ? row.tags.join(', ') : ''
    syncFileList()
  } else {
    isEdit.value = false
    editId.value = null
  }

  dialogVisible.value = true
}

function beforeUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isImage) {
    ElMessage.error(t('products.imageError'))
    return false
  }
  if (!isLt10M) {
    ElMessage.error(t('products.imageSizeError'))
    return false
  }
  return true
}

async function handleUpload(options) {
  uploading.value = true
  try {
    const res = await uploadFile(options.file)
    const url = res.data?.url
    if (!url) throw new Error(t('common.uploadFailed'))
    form.images.push(url)
    form.cover_image = form.images[0] || ''
    syncFileList()
    options.onSuccess?.(res)
  } catch (err) {
    options.onError?.(err)
  } finally {
    uploading.value = false
  }
}

function handleRemove(file) {
  const index = form.images.findIndex(img => resolveUrl(img) === file.url)
  if (index >= 0) removeImage(index)
}

function removeImage(index) {
  form.images.splice(index, 1)
  form.cover_image = form.images[0] || ''
  syncFileList()
}

function setPrimary(index) {
  if (index <= 0) return
  const [selected] = form.images.splice(index, 1)
  form.images.unshift(selected)
  form.cover_image = form.images[0] || ''
  syncFileList()
}

async function onSave() {
  if (!form.name_en && !form.name_zh) {
    ElMessage.error(t('common.nameRequired'))
    return
  }

  saving.value = true
  try {
    const payload = {
      ...form,
      tags: tagsText.value
        .split(',')
        .map(item => item.trim())
        .filter(Boolean),
      images: form.images,
      cover_image: form.cover_image || form.images[0] || ''
    }

    if (isEdit.value) {
      await updateTicketAttraction(editId.value, payload)
      ElMessage.success(t('common.updated'))
    } else {
      await createTicketAttraction(payload)
      ElMessage.success(t('common.created'))
    }

    dialogVisible.value = false
    loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try {
    await deleteTicketAttraction(id)
    ElMessage.success(t('common.deleted'))
    loadData()
  } catch {}
}

onMounted(loadData)
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

.field-tip {
  font-size: 12px;
  color: #8a7b6b;
  margin-top: 6px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin: 8px 0 16px;
}

.gallery-item {
  border: 1px solid #eadfce;
  border-radius: 10px;
  padding: 10px;
  background: #fff;
}

.gallery-item.active {
  border-color: #c8a97e;
  box-shadow: 0 0 0 2px rgba(200, 169, 126, 0.12);
}

.gallery-image {
  width: 100%;
  height: 140px;
  border-radius: 8px;
}

.gallery-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 10px;
}
</style>
