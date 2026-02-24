<template>
  <div>
    <div class="page-header">
      <div class="header-filters">
        <el-input v-model="keyword" placeholder="Search products..." clearable style="width:240px" @keyup.enter="loadData" />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width:160px" @change="loadData">
          <el-option v-for="c in categories" :key="c.id" :label="c.name_en || c.name_zh" :value="c.id" />
        </el-select>
      </div>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> Add Product
      </el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="Image" width="80">
          <template #default="{ row }">
            <el-image v-if="row.images?.length" :src="row.images[0]" style="width:50px;height:50px;border-radius:8px" fit="cover" />
            <div v-else style="width:50px;height:50px;border-radius:8px;background:#f5efe6;display:flex;align-items:center;justify-content:center;color:#c8a97e;font-weight:700">{{ (row.name_en || row.name_zh || '?').charAt(0) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="name_en" label="Name (EN)" min-width="160" show-overflow-tooltip />
        <el-table-column prop="name_zh" label="Name (ZH)" min-width="120" show-overflow-tooltip />
        <el-table-column label="Category" width="120">
          <template #default="{ row }">{{ getCategoryName(row.category_id) }}</template>
        </el-table-column>
        <el-table-column prop="price" label="Price" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column label="Featured" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_featured" type="warning" size="small">Yes</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? 'Active' : 'Hidden' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">Edit</el-button>
            <el-popconfirm title="Delete this product?" @confirm="onDelete(row.id)">
              <template #reference><el-button link type="danger">Delete</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Edit Product' : 'Add Product'" width="700px" destroy-on-close>
      <el-form :model="form" label-width="120px" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Name (EN)" required>
              <el-input v-model="form.name_en" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Name (ZH)">
              <el-input v-model="form.name_zh" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Name (RU)">
              <el-input v-model="form.name_ru" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Name (ES)">
              <el-input v-model="form.name_es" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Category" required>
          <el-select v-model="form.category_id" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name_en || c.name_zh" :value="c.id" />
          </el-select>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Price" required>
              <el-input-number v-model="form.price" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Original Price">
              <el-input-number v-model="form.original_price" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Sort Order">
              <el-input-number v-model="form.sort_order" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Description (EN)">
              <el-input v-model="form.desc_en" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Description (ZH)">
              <el-input v-model="form.desc_zh" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Image URLs (one per line)">
          <el-input v-model="imagesText" type="textarea" :rows="3" placeholder="https://example.com/image1.jpg&#10;https://example.com/image2.jpg" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Featured">
              <el-switch v-model="form.is_featured" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status">
              <el-radio-group v-model="form.status">
                <el-radio :value="1">Active</el-radio>
                <el-radio :value="0">Hidden</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getProducts, createProduct, updateProduct, deleteProduct, getCategories } from '../api'

const list = ref([])
const categories = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const page = ref(1)
const pageSize = 15
const total = ref(0)
const keyword = ref('')
const categoryFilter = ref('')

const defaultForm = () => ({
  name_en: '', name_zh: '', name_ru: '', name_es: '',
  desc_en: '', desc_zh: '',
  category_id: null, price: 0, original_price: null,
  sort_order: 0, is_featured: false, status: 1
})
const form = reactive(defaultForm())
const imagesText = ref('')

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
    list.value = res.data?.items || res.data || []
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
  imagesText.value = ''
  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.keys(form).forEach(k => { if (row[k] !== undefined) form[k] = row[k] })
    imagesText.value = (row.images || []).join('\n')
  } else {
    isEdit.value = false
    editId.value = null
  }
  dialogVisible.value = true
}

async function onSave() {
  if (!form.name_en && !form.name_zh) return ElMessage.warning('Name is required')
  if (!form.category_id) return ElMessage.warning('Category is required')
  if (!form.price) return ElMessage.warning('Price is required')

  saving.value = true
  const data = { ...form }
  data.images = imagesText.value.split('\n').map(s => s.trim()).filter(Boolean)
  try {
    if (isEdit.value) {
      await updateProduct(editId.value, data)
      ElMessage.success('Product updated')
    } else {
      await createProduct(data)
      ElMessage.success('Product created')
    }
    dialogVisible.value = false
    loadData()
  } catch {}
  saving.value = false
}

async function onDelete(id) {
  try {
    await deleteProduct(id)
    ElMessage.success('Deleted')
    loadData()
  } catch {}
}

onMounted(() => { loadData(); loadCategories() })
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.header-filters { display: flex; gap: 12px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
