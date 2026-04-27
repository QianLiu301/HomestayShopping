<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input v-model="keyword" :placeholder="$t('products.searchPlaceholder')" clearable style="width:240px" @keyup.enter="loadData" />
        <el-select v-model="categoryFilter" :placeholder="$t('products.category')" clearable style="width:160px" @change="loadData">
          <el-option v-for="c in categories" :key="c.id" :label="c.name_en || c.name_zh" :value="c.id" />
        </el-select>
      </div>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> {{ $t('products.addProduct') }}
      </el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column :label="$t('common.image')" width="80">
          <template #default="{ row }">
            <el-image v-if="row.images?.length" :src="resolveUrl(row.images[0])" style="width:50px;height:50px;border-radius:8px" fit="cover" lazy loading="lazy">
              <template #error><div style="width:50px;height:50px;border-radius:8px;background:#f5efe6;display:flex;align-items:center;justify-content:center;color:#c8a97e;font-size:12px">!</div></template>
            </el-image>
            <div v-else style="width:50px;height:50px;border-radius:8px;background:#f5efe6;display:flex;align-items:center;justify-content:center;color:#c8a97e;font-weight:700">{{ (row.name_en || row.name_zh || '?').charAt(0) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="name_en" :label="$t('products.nameEn')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="name_zh" :label="$t('products.nameZh')" min-width="120" show-overflow-tooltip />
        <el-table-column :label="$t('products.category')" width="120">
          <template #default="{ row }">{{ getCategoryName(row.category_id) }}</template>
        </el-table-column>
        <el-table-column prop="price" :label="$t('products.price')" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column :label="$t('products.featured')" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_featured" type="warning" size="small">{{ $t('common.yes') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.status')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? $t('common.active') : $t('common.hidden') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">{{ $t('common.edit') }}</el-button>
            <el-popconfirm :title="$t('common.delete') + '?'" @confirm="onDelete(row.id)">
              <template #reference><el-button link type="danger">{{ $t('common.delete') }}</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? $t('products.editProduct') : $t('products.addProduct')" width="700px" destroy-on-close>
      <el-form :model="form" label-width="120px" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="$t('products.nameEn')" required>
              <el-input v-model="form.name_en" :maxlength="1000" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('products.nameZh')">
              <el-input v-model="form.name_zh" :maxlength="1000" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('products.nameRu')">
              <el-input v-model="form.name_ru" :maxlength="1000" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('products.nameEs')">
              <el-input v-model="form.name_es" :maxlength="1000" show-word-limit />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item :label="$t('products.category')" required>
          <el-select v-model="form.category_id" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name_en || c.name_zh" :value="c.id" />
          </el-select>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item :label="$t('products.price')" required>
              <el-input-number v-model="form.price" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('products.originalPrice')">
              <el-input-number v-model="form.original_price" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="$t('products.sortOrder')">
              <el-input-number v-model="form.sort_order" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="$t('products.descEn')">
              <el-input v-model="form.desc_en" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('products.descZh')">
              <el-input v-model="form.desc_zh" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('products.descRu')">
              <el-input v-model="form.desc_ru" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('products.descEs')">
              <el-input v-model="form.desc_es" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item :label="$t('products.productImages')">
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
              <div class="image-actions">
                <el-icon class="action-icon" @click="handleRemove(file)"><Delete /></el-icon>
              </div>
              <div class="drag-handle">⋮⋮</div>
            </div>
            <el-upload
              :file-list="[]"
              :http-request="handleUpload"
              :before-upload="beforeUpload"
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
          <div class="upload-tip">{{ $t('products.dragToReorder') }}</div>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item :label="$t('products.featured')">
              <el-switch v-model="form.is_featured" />
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
        <el-button type="primary" :loading="saving || uploadingCount > 0" :disabled="uploadingCount > 0" @click="onSave">{{ uploadingCount > 0 ? '图片上传中...' : $t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getProducts, createProduct, updateProduct, deleteProduct, getCategories, uploadFile, resolveUrl } from '../api'

const { t } = useI18n()
const list = ref([])
const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const uploadingCount = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const page = ref(1)
const pageSize = 15
const total = ref(0)
const keyword = ref('')
const categoryFilter = ref('')
const fileList = ref([])
const uploadedImages = ref([])
const draggedIndex = ref(null)

const defaultForm = () => ({
  name_en: '', name_zh: '', name_ru: '', name_es: '',
  desc_en: '', desc_zh: '', desc_ru: '', desc_es: '',
  category_id: null, price: 0, original_price: null,
  sort_order: 0, is_featured: false, status: 1
})
const form = reactive(defaultForm())

function getCategoryName(id) {
  const c = categories.value.find(x => x.id === id)
  return c ? (c.name_en || c.name_zh) : '-'
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize }
    if (keyword.value) params.keyword = keyword.value
    if (categoryFilter.value) params.category_id = categoryFilter.value
    const res = await getProducts(params)
    list.value = res.data?.list || res.data?.items || []
    total.value = res.data?.total || list.value.length
  } catch {}
  loading.value = false
}

async function loadCategories() {
  try {
    const res = await getCategories()
    categories.value = res.data || []
  } catch {}
}

function openDialog(row) {
  Object.assign(form, defaultForm())
  fileList.value = []
  uploadedImages.value = []

  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.keys(form).forEach(k => {
      if (row[k] !== undefined && row[k] !== null) form[k] = row[k]
    })
    const images = row.images || []
    uploadedImages.value = [...images]
    fileList.value = images.map((url, idx) => ({
      name: `image-${idx}`,
      url: resolveUrl(url)
    }))
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
  uploadingCount.value++
  try {
    const res = await uploadFile(options.file)
    const url = res.data?.url
    if (url) {
      uploadedImages.value.push(url)
      // 将返回的 URL 存入 file 对象，方便 handleRemove 匹配
      options.file._uploadedUrl = url
      // 同步更新 fileList 以便立即显示预览
      fileList.value.push({
        name: options.file.name,
        url: resolveUrl(url),
        uid: options.file.uid
      })
      options.onSuccess(res)
    } else {
      options.onError(new Error(t('common.uploadFailed')))
    }
  } catch (err) {
    options.onError(err)
  } finally {
    uploadingCount.value = Math.max(0, uploadingCount.value - 1)
  }
}

function handleRemove(file) {
  // 从 fileList 中移除
  const fileIdx = fileList.value.findIndex(f => f.uid === file.uid || f.url === file.url)
  if (fileIdx > -1) {
    fileList.value.splice(fileIdx, 1)
  }
  
  // 从 uploadedImages 中移除对应的 URL
  // 优先使用上传时存储的 URL，其次从 response 中��取
  const url = file.raw?._uploadedUrl || file.response?.data?.url || file.url
  if (url) {
    // 尝试直接匹配
    let idx = uploadedImages.value.indexOf(url)
    if (idx > -1) {
      uploadedImages.value.splice(idx, 1)
      return
    }
    
    // 对于编辑模式加载的已有图片，用 resolveUrl 反查
    if (url.startsWith('http')) {
      idx = uploadedImages.value.findIndex(u => resolveUrl(u) === url)
      if (idx > -1) {
        uploadedImages.value.splice(idx, 1)
        return
      }
    }
    
    // 最后尝试反向匹配：url 可能是 resolveUrl 后的结果
    idx = uploadedImages.value.findIndex(u => resolveUrl(u) === url)
    if (idx > -1) {
      uploadedImages.value.splice(idx, 1)
    }
  }
}

function onDragStart(event, index) {
  draggedIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
}

function onDrop(event, dropIndex) {
  event.preventDefault()
  const dragIndex = draggedIndex.value
  if (dragIndex === null || dragIndex === dropIndex) return

  // 交换 fileList
  const draggedFile = fileList.value[dragIndex]
  fileList.value.splice(dragIndex, 1)
  fileList.value.splice(dropIndex, 0, draggedFile)

  // 同步 uploadedImages
  const draggedUrl = uploadedImages.value[dragIndex]
  uploadedImages.value.splice(dragIndex, 1)
  uploadedImages.value.splice(dropIndex, 0, draggedUrl)

  draggedIndex.value = null
}

function validateNameLengths() {
  const nameFields = [
    ['name_en', t('products.nameEn')],
    ['name_zh', t('products.nameZh')],
    ['name_ru', t('products.nameRu')],
    ['name_es', t('products.nameEs')]
  ]

  for (const [field, label] of nameFields) {
    const value = form[field]
    if (value && value.length > 1000) {
      ElMessage.warning(t('products.nameTooLong', { field: label, max: 1000 }))
      return false
    }
  }

  return true
}

async function onSave() {
  if (!form.name_en && !form.name_zh) return ElMessage.warning(t('common.nameRequired'))
  if (!form.category_id) return ElMessage.warning(t('products.categoryRequired'))
  if (!form.price) return ElMessage.warning(t('products.priceRequired'))
  if (uploadingCount.value > 0) return ElMessage.warning('图片仍在上传中，请等待上传完成后再保存')
  if (!validateNameLengths()) return

  saving.value = true
  const data = { ...form, images: [...uploadedImages.value] }
  try {
    if (isEdit.value) {
      await updateProduct(editId.value, data)
      ElMessage.success(t('common.updated'))
    } else {
      await createProduct(data)
      ElMessage.success(t('common.created'))
    }
    dialogVisible.value = false
    loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try {
    await deleteProduct(id)
    ElMessage.success(t('common.deleted'))
    loadData()
  } catch {}
}

onMounted(() => { loadData(); loadCategories() })
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.header-filters { display: flex; gap: 12px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }

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

.image-actions {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-item:hover .image-actions {
  opacity: 1;
}

.action-icon {
  font-size: 20px;
  color: #fff;
  cursor: pointer;
  padding: 8px;
}

.action-icon:hover {
  color: #f56c6c;
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
</style>
