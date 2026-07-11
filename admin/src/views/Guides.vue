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
            <div v-if="row.cover_image" style="position:relative;display:inline-block">
              <el-image :src="resolveUrl(row.cover_image)" style="width:60px;height:60px;border-radius:6px" fit="cover" />
              <span v-if="row.images?.length > 1" style="position:absolute;bottom:2px;right:2px;background:rgba(0,0,0,0.6);color:#fff;font-size:10px;padding:1px 5px;border-radius:4px">{{ row.images.length }}</span>
            </div>
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

            <el-form-item :label="$t('guides.images')">
              <div class="image-upload-area">
                <div
                  v-for="(file, idx) in fileList"
                  :key="file.uid || idx"
                  class="image-item"
                  draggable="true"
                  @dragstart="onDragStart($event, idx)"
                  @dragover.prevent
                  @drop="onDrop($event, idx)"
                >
                  <el-image :src="file.url" fit="cover" class="preview-img" />
                  <div class="image-remove-btn" @click="handleRemove(idx)">✕</div>
                  <div class="drag-handle">⋮⋮</div>
                  <div v-if="idx === 0" class="cover-badge">{{ $t('guides.coverLabel') }}</div>
                </div>
                <el-upload
                  :file-list="[]"
                  :http-request="handleUpload"
                  :show-file-list="false"
                  accept="image/*"
                  multiple
                  class="upload-trigger"
                >
                  <div class="upload-box">
                    <el-icon><Plus /></el-icon>
                  </div>
                </el-upload>
              </div>
              <div class="upload-tip">{{ $t('guides.dragToReorder') }}</div>
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
          <div class="insert-ticket-bar">
            <div class="insert-row">
              <span class="insert-label">{{ $t('guides.insertTarget') }}</span>
              <el-select v-model="insertTargetField" style="width:130px" size="small">
                <el-option label="中文" value="content_zh" />
                <el-option label="English" value="content_en" />
                <el-option label="Русский" value="content_ru" />
                <el-option label="Español" value="content_es" />
              </el-select>
              <el-checkbox v-model="syncAllLangs" size="small">{{ $t('guides.syncAllLangs') }}</el-checkbox>
            </div>
            <div class="insert-row">
              <span class="insert-label">{{ $t('guides.insertTicketLink') }}</span>
              <el-select
                v-model="insertAttractionId"
                :placeholder="$t('guides.selectAttraction')"
                filterable
                clearable
                size="small"
                style="width:220px"
              >
                <el-option v-for="a in attractions" :key="a.id" :label="a.name_zh || a.name_en" :value="a.id" />
              </el-select>
              <el-button type="primary" plain size="small" :disabled="!insertAttractionId" @click="onInsertTicketLink">
                {{ $t('guides.insertBtn') }}
              </el-button>
            </div>
            <div class="insert-row">
              <span class="insert-label">{{ $t('guides.insertMap') }}</span>
              <el-input v-model="insertMapName" :placeholder="$t('guides.mapNamePlaceholder')" size="small" style="width:220px" />
              <el-button type="primary" plain size="small" :disabled="!insertMapName.trim()" @click="onInsertMap">
                {{ $t('guides.insertBtn') }}
              </el-button>
            </div>
            <div class="insert-row">
              <span class="insert-label">{{ $t('guides.insertMedia') }}</span>
              <el-upload :show-file-list="false" :http-request="handleContentImageUpload" accept="image/*">
                <el-button type="primary" plain size="small" :loading="mediaUploading">📷 {{ $t('guides.insertImage') }}</el-button>
              </el-upload>
              <el-upload :show-file-list="false" :http-request="handleContentVideoUpload" accept="video/mp4,video/quicktime,video/webm">
                <el-button type="primary" plain size="small" :loading="mediaUploading">🎬 {{ $t('guides.insertVideo') }}</el-button>
              </el-upload>
              <span class="insert-tip">{{ $t('guides.videoTip') }}</span>
            </div>
          </div>
          <el-form :model="form" label-width="140px">
            <el-form-item :label="$t('guides.contentZh')">
              <el-input ref="contentZhRef" v-model="form.content_zh" type="textarea" :rows="12" placeholder="支持 HTML 格式" />
            </el-form-item>
            <el-form-item :label="$t('guides.contentEn')">
              <el-input ref="contentEnRef" v-model="form.content_en" type="textarea" :rows="12" placeholder="Supports HTML format" />
            </el-form-item>
            <el-form-item :label="$t('guides.contentRu')">
              <el-input ref="contentRuRef" v-model="form.content_ru" type="textarea" :rows="8" />
            </el-form-item>
            <el-form-item :label="$t('guides.contentEs')">
              <el-input ref="contentEsRef" v-model="form.content_es" type="textarea" :rows="8" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="showForm = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving || uploadingCount > 0" :disabled="uploadingCount > 0" @click="onSave">{{ uploadingCount > 0 ? '图片上传中...' : $t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, Delete } from '@element-plus/icons-vue'
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
const fileList = ref([])
const uploadedImages = ref([])
const draggedIndex = ref(null)
const uploadingCount = ref(0)
const insertAttractionId = ref(null)
const insertTargetField = ref('content_zh')
const syncAllLangs = ref(true)
const insertMapName = ref('')
const mediaUploading = ref(false)
const contentFields = ['content_zh', 'content_en', 'content_ru', 'content_es']
const contentZhRef = ref(null)
const contentEnRef = ref(null)
const contentRuRef = ref(null)
const contentEsRef = ref(null)
const contentRefMap = { content_zh: contentZhRef, content_en: contentEnRef, content_ru: contentRuRef, content_es: contentEsRef }

const defaultForm = () => ({
  title_zh: '', title_en: '', title_ru: '', title_es: '',
  summary_zh: '', summary_en: '', summary_ru: '', summary_es: '',
  content_zh: '', content_en: '', content_ru: '', content_es: '',
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
  fileList.value = []
  uploadedImages.value = []
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
      category: row.category || '',
      attraction_id: row.attraction_id || null,
      sort_order: row.sort_order || 0,
      status: row.status ?? 1,
    }
    const images = row.images || (row.cover_image ? [row.cover_image] : [])
    uploadedImages.value = [...images]
    fileList.value = images.map((url, idx) => ({
      name: `image-${idx}`,
      url: resolveUrl(url)
    }))
  } else {
    editingId.value = null
    form.value = defaultForm()
  }
  showForm.value = true
}

async function handleUpload(options) {
  uploadingCount.value++
  try {
    const res = await apiUploadFile(options.file)
    const url = res.data?.url
    if (url) {
      uploadedImages.value.push(url)
      fileList.value.push({
        name: options.file.name,
        url: resolveUrl(url),
        uid: options.file.uid
      })
      options.onSuccess?.(res)
    } else {
      options.onError?.(new Error('上传失败'))
    }
  } catch (err) {
    options.onError?.(err)
  } finally {
    uploadingCount.value = Math.max(0, uploadingCount.value - 1)
  }
}

function handleRemove(idx) {
  fileList.value.splice(idx, 1)
  uploadedImages.value.splice(idx, 1)
}

function onDragStart(event, index) {
  draggedIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
}

function onDrop(event, dropIndex) {
  event.preventDefault()
  const dragIndex = draggedIndex.value
  if (dragIndex === null || dragIndex === dropIndex) return

  const draggedFile = fileList.value[dragIndex]
  fileList.value.splice(dragIndex, 1)
  fileList.value.splice(dropIndex, 0, draggedFile)

  const draggedUrl = uploadedImages.value[dragIndex]
  uploadedImages.value.splice(dragIndex, 1)
  uploadedImages.value.splice(dropIndex, 0, draggedUrl)

  draggedIndex.value = null
}

function insertTag(tag, successMsg) {
  const field = insertTargetField.value
  const elInputRef = contentRefMap[field]
  const textarea = elInputRef?.value?.$el?.querySelector('textarea')
  const text = form.value[field] || ''
  if (textarea) {
    const start = textarea.selectionStart ?? text.length
    const end = textarea.selectionEnd ?? start
    form.value[field] = text.slice(0, start) + tag + text.slice(end)
    nextTick(() => {
      const pos = start + tag.length
      textarea.focus()
      textarea.setSelectionRange(pos, pos)
    })
  } else {
    form.value[field] = text + '\n' + tag
  }
  // 同步追加到其它三种语言的内容末尾
  if (syncAllLangs.value) {
    for (const f of contentFields) {
      if (f === field) continue
      form.value[f] = (form.value[f] || '') + '\n' + tag
    }
  }
  ElMessage.success(successMsg + (syncAllLangs.value ? '（已同步四种语言）' : ''))
}

function onInsertTicketLink() {
  const aid = insertAttractionId.value
  if (!aid) return
  const att = attractions.value.find(a => a.id === aid)
  if (!att) return
  const name = att.name_zh || att.name_en || ''
  insertTag(`{{ticket:${aid}:${name}}}`, `已插入「${name}」的门票链接`)
  insertAttractionId.value = null
}

function onInsertMap() {
  const name = insertMapName.value.trim()
  if (!name) return
  insertTag(`{{map:${name}}}`, `已插入「${name}」的位置卡片`)
  insertMapName.value = ''
}

async function handleContentImageUpload(options) {
  mediaUploading.value = true
  try {
    const res = await apiUploadFile(options.file)
    const url = res.data?.url
    if (url) {
      insertTag(`{{img:${url}}}`, '已插入图片')
      options.onSuccess?.(res)
    }
  } catch (e) {
    options.onError?.(e)
    ElMessage.error('图片上传失败')
  } finally {
    mediaUploading.value = false
  }
}

async function handleContentVideoUpload(options) {
  if (options.file.size > 100 * 1024 * 1024) {
    ElMessage.error('视频不能超过 100MB')
    options.onError?.(new Error('too large'))
    return
  }
  mediaUploading.value = true
  try {
    const res = await apiUploadFile(options.file)
    const url = res.data?.url
    if (url) {
      insertTag(`{{video:${url}}}`, '已插入视频')
      options.onSuccess?.(res)
    }
  } catch (e) {
    options.onError?.(e)
    ElMessage.error('视频上传失败')
  } finally {
    mediaUploading.value = false
  }
}

async function onSave() {
  if (!form.value.title_zh && !form.value.title_en) {
    return ElMessage.warning('标题不能为空')
  }
  saving.value = true
  try {
    const data = { ...form.value, images: [...uploadedImages.value] }
    if (editingId.value) {
      await updateGuide(editingId.value, data)
    } else {
      await createGuide(data)
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

.image-upload-area {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.image-item {
  position: relative;
  width: 120px;
  height: 120px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  cursor: move;
  transition: all 0.2s;
}

.image-item:hover {
  border-color: #c8a97e;
  box-shadow: 0 2px 8px rgba(200, 169, 126, 0.2);
}

.preview-img {
  width: 100%;
  height: 100%;
}

.image-remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  background: rgba(245, 108, 108, 0.85);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  cursor: pointer;
  z-index: 10;
  line-height: 1;
}

.image-remove-btn:hover {
  background: #f56c6c;
}

.drag-handle {
  position: absolute;
  top: 4px;
  left: 4px;
  padding: 2px 6px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 14px;
  border-radius: 4px;
  pointer-events: none;
}

.cover-badge {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  padding: 2px 0;
  background: rgba(200, 169, 126, 0.85);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  pointer-events: none;
}

.upload-trigger {
  display: inline-block;
}

.upload-box {
  width: 120px;
  height: 120px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 28px;
  color: #8c939d;
}

.upload-box:hover {
  border-color: #c8a97e;
  color: #c8a97e;
}

.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.insert-ticket-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  background: #fdf8f0;
  border: 1px solid #ebe5df;
  border-radius: 8px;
}

.insert-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.insert-label {
  font-size: 13px;
  font-weight: 600;
  color: #4a3728;
  white-space: nowrap;
  min-width: 110px;
}

.insert-tip {
  font-size: 12px;
  color: #909399;
}
</style>
