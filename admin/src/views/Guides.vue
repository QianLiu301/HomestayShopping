<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input
          v-model="keyword"
          :placeholder="$t('guides.searchPlaceholder')"
          clearable
          style="width:280px"
          @keyup.enter="loadData(1)"
          @clear="loadData(1)"
        >
          <template #append>
            <el-button :icon="Search" @click="loadData(1)" />
          </template>
        </el-input>
        <el-select v-model="statusFilter" clearable placeholder="状态" style="width:120px" @change="loadData(1)">
          <el-option label="上架" :value="1" />
          <el-option label="下架" :value="0" />
        </el-select>
        <el-select v-model="categoryFilter" clearable :placeholder="$t('guides.categoryPlaceholder')" style="width:120px" @change="loadData(1)">
          <el-option :label="$t('guides.cat_attraction')" value="attraction" />
          <el-option :label="$t('guides.cat_food')" value="food" />
          <el-option :label="$t('guides.cat_entertainment')" value="entertainment" />
          <el-option :label="$t('guides.cat_shopping')" value="shopping" />
        </el-select>
      </div>
      <el-button type="primary" :icon="Plus" @click="openForm()">{{ $t('guides.addGuide') }}</el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column :label="$t('guides.coverImage')" width="100">
          <template #default="{ row }">
            <el-image v-if="row.cover_image" :src="resolveUrl(row.cover_image)" style="width:60px;height:60px;border-radius:6px" fit="cover" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guides.titleZh')" min-width="200">
          <template #default="{ row }">
            <div style="font-weight:600">{{ row.title_zh || row.title_en || '-' }}</div>
            <div v-if="row.summary_zh" style="font-size:12px;color:#999;margin-top:2px" class="content-cell">{{ row.summary_zh }}</div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guides.category')" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.category" size="small">{{ $t(`guides.cat_${row.category}`) }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('guides.attraction')" width="160">
          <template #default="{ row }">{{ row.attraction ? (row.attraction.name_zh || row.attraction.name_en) : '-' }}</template>
        </el-table-column>
        <el-table-column :label="$t('guides.sortOrder')" width="80" prop="sort_order" />
        <el-table-column :label="$t('common.status')" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? $t('common.enabled') : $t('common.disabled') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openForm(row)">{{ $t('common.edit') }}</el-button>
            <el-popconfirm :title="$t('guides.deleteConfirm')" @confirm="onDelete(row.id)">
              <template #reference>
                <el-button link type="danger">{{ $t('common.delete') }}</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <el-pagination
          v-model:current-page="page"
          :page-size="perPage"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- Form Dialog -->
    <el-dialog
      v-model="showForm"
      :title="editingId ? $t('guides.editGuide') : $t('guides.addGuide')"
      width="900px"
      top="3vh"
      destroy-on-close
    >
      <el-tabs v-model="activeTab">
        <el-tab-pane :label="$t('guides.basicInfo')" name="basic">
          <el-form :model="form" label-width="140px" style="max-width:700px">
            <el-form-item :label="$t('guides.titleZh')" required>
              <el-input v-model="form.title_zh" />
            </el-form-item>
            <el-form-item :label="$t('guides.titleEn')">
              <el-input v-model="form.title_en" />
            </el-form-item>
            <el-form-item :label="$t('guides.titleRu')">
              <el-input v-model="form.title_ru" />
            </el-form-item>
            <el-form-item :label="$t('guides.titleEs')">
              <el-input v-model="form.title_es" />
            </el-form-item>

            <el-form-item :label="$t('guides.summaryZh')">
              <el-input v-model="form.summary_zh" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item :label="$t('guides.summaryEn')">
              <el-input v-model="form.summary_en" type="textarea" :rows="2" />
            </el-form-item>

            <el-form-item :label="$t('guides.coverImage')">
              <div class="cover-upload">
                <el-image v-if="form.cover_image" :src="resolveUrl(form.cover_image)" style="width:120px;height:80px;border-radius:6px" fit="cover" />
                <el-upload
                  action=""
                  :auto-upload="false"
                  :show-file-list="false"
                  accept="image/*"
                  @change="onCoverChange"
                >
                  <el-button size="small">{{ form.cover_image ? $t('common.replace') : $t('common.upload') }}</el-button>
                </el-upload>
              </div>
            </el-form-item>

            <el-form-item :label="$t('guides.category')">
              <el-select v-model="form.category" :placeholder="$t('guides.categoryPlaceholder')" clearable>
                <el-option :label="$t('guides.cat_attraction')" value="attraction" />
                <el-option :label="$t('guides.cat_food')" value="food" />
                <el-option :label="$t('guides.cat_entertainment')" value="entertainment" />
                <el-option :label="$t('guides.cat_shopping')" value="shopping" />
              </el-select>
            </el-form-item>

            <el-form-item :label="$t('guides.attraction')">
              <el-select v-model="form.attraction_id" :placeholder="$t('guides.attractionPlaceholder')" clearable filterable>
                <el-option v-for="a in attractions" :key="a.id" :label="a.name_zh || a.name_en" :value="a.id" />
              </el-select>
            </el-form-item>

            <el-form-item :label="$t('guides.sortOrder')">
              <el-input-number v-model="form.sort_order" :min="0" />
            </el-form-item>

            <el-form-item :label="$t('common.status')">
              <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane :label="$t('guides.contentTab')" name="content">
          <el-form :model="form" label-width="140px">
            <el-form-item :label="$t('guides.contentZh')">
              <el-input v-model="form.content_zh" type="textarea" :rows="12" placeholder="支持 HTML 格式" />
            </el-form-item>
            <el-form-item :label="$t('guides.contentEn')">
              <el-input v-model="form.content_en" type="textarea" :rows="12" placeholder="Supports HTML format" />
            </el-form-item>
            <el-form-item :label="$t('guides.contentRu')">
              <el-input v-model="form.content_ru" type="textarea" :rows="8" />
            </el-form-item>
            <el-form-item :label="$t('guides.contentEs')">
              <el-input v-model="form.content_es" type="textarea" :rows="8" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="showForm = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">{{ $t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getGuides, createGuide, updateGuide, deleteGuide, uploadFile as apiUploadFile, resolveUrl } from '../api'
import http from '../api'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = 20
const total = ref(0)
const keyword = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const attractions = ref([])

const showForm = ref(false)
const editingId = ref(null)
const saving = ref(false)
const activeTab = ref('basic')

const defaultForm = () => ({
  title_zh: '', title_en: '', title_ru: '', title_es: '',
  summary_zh: '', summary_en: '', summary_ru: '', summary_es: '',
  content_zh: '', content_en: '', content_ru: '', content_es: '',
  cover_image: '',
  category: '',
  attraction_id: null,
  sort_order: 0,
  status: 1,
})
const form = ref(defaultForm())

async function loadData(p = 1) {
  page.value = p
  loading.value = true
  try {
    const params = { page: p, per_page: perPage }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value !== '') params.status = statusFilter.value
    if (categoryFilter.value) params.category = categoryFilter.value
    const res = await getGuides(params)
    list.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadAttractions() {
  try {
    const res = await http.get('/admin/ticket-attractions', { params: { per_page: 200 } })
    attractions.value = res.data?.list || []
  } catch (e) {
    console.error(e)
  }
}

function openForm(row = null) {
  activeTab.value = 'basic'
  if (row) {
    editingId.value = row.id
    form.value = {
      title_zh: row.title_zh || '',
      title_en: row.title_en || '',
      title_ru: row.title_ru || '',
      title_es: row.title_es || '',
      summary_zh: row.summary_zh || '',
      summary_en: row.summary_en || '',
      summary_ru: row.summary_ru || '',
      summary_es: row.summary_es || '',
      content_zh: row.content_zh || '',
      content_en: row.content_en || '',
      content_ru: row.content_ru || '',
      content_es: row.content_es || '',
      cover_image: row.cover_image || '',
      category: row.category || '',
      attraction_id: row.attraction_id || null,
      sort_order: row.sort_order || 0,
      status: row.status ?? 1,
    }
  } else {
    editingId.value = null
    form.value = defaultForm()
  }
  showForm.value = true
}

async function onCoverChange(upload) {
  const file = upload.raw
  if (!file) return
  try {
    const res = await apiUploadFile(file)
    form.value.cover_image = res.data?.url || ''
    ElMessage.success('上传成功')
  } catch (e) {
    ElMessage.error('上传失败')
  }
}

async function onSave() {
  if (!form.value.title_zh && !form.value.title_en) {
    return ElMessage.warning('标题不能为空')
  }
  saving.value = true
  try {
    if (editingId.value) {
      await updateGuide(editingId.value, form.value)
    } else {
      await createGuide(form.value)
    }
    showForm.value = false
    loadData(editingId.value ? page.value : 1)
  } catch (e) {
    console.error(e)
  } finally {
    saving.value = false
  }
}

async function onDelete(id) {
  try {
    await deleteGuide(id)
    ElMessage.success('删除成功')
    loadData(page.value)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadData()
  loadAttractions()
})
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
  flex-wrap: wrap;
}
.content-cell {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.cover-upload {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
