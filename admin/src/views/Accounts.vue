<template>
  <div>
    <div class="page-header">
      <div></div>
      <el-button type="primary" :icon="Plus" @click="openCreate">
        {{ $t('accounts.create') }}
      </el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column :label="$t('accounts.username')" prop="username" />
        <el-table-column :label="$t('accounts.name')" prop="name" />
        <el-table-column :label="$t('accounts.role')" width="140">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('accounts.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? $t('accounts.enabled') : $t('accounts.disabled') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('accounts.createdAt')" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">{{ $t('common.manage') }}</el-button>
            <el-button
              v-if="row.role !== 'owner' && row.id !== auth.user?.id"
              link
              type="danger"
              @click="onDelete(row)"
            >
              {{ $t('common.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? $t('accounts.editTitle') : $t('accounts.createTitle')"
      width="480px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item :label="$t('accounts.username')" required>
          <el-input
            v-model="form.username"
            :disabled="isEdit"
            placeholder="username"
            autocomplete="off"
          />
        </el-form-item>
        <el-form-item :label="$t('accounts.name')">
          <el-input v-model="form.name" autocomplete="off" />
        </el-form-item>
        <el-form-item :label="$t('accounts.role')" required>
          <el-select v-model="form.role" :disabled="isEdit && current?.role === 'owner'">
            <el-option
              v-for="r in availableRoles"
              :key="r.value"
              :label="r.label"
              :value="r.value"
              :disabled="r.value === 'owner'"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('accounts.password')" :required="!isEdit">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="$t('accounts.passwordPlaceholder')"
            autocomplete="new-password"
          />
        </el-form-item>
        <el-form-item :label="$t('accounts.status')" v-if="isEdit && current?.role !== 'owner'">
          <el-switch
            v-model="form.status"
            :active-value="1"
            :inactive-value="0"
            :active-text="$t('accounts.enabled')"
            :inactive-text="$t('accounts.disabled')"
          />
        </el-form-item>
        <el-alert
          v-if="isEdit && current?.role === 'owner'"
          :title="$t('accounts.cantEditOwner')"
          type="warning"
          show-icon
          :closable="false"
          style="margin-top:8px"
        />
        <el-alert
          v-else
          :title="$t('accounts.roleHint')"
          type="info"
          show-icon
          :closable="false"
          style="margin-top:8px"
        />
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('accounts.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">{{ $t('accounts.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { getAccounts, createAccount, updateAccount, deleteAccount } from '../api'
import { useAuthStore } from '../stores/auth'

const { t } = useI18n()
const auth = useAuthStore()

const list = ref([])
const availableRoles = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const current = ref(null)

const form = ref({
  username: '',
  name: '',
  role: 'cs',
  password: '',
  status: 1,
})

function roleLabel(role) {
  const found = availableRoles.value.find(r => r.value === role)
  return found?.label || role
}
function roleTagType(role) {
  return {
    owner: 'danger',
    admin: 'warning',
    finance: 'success',
    cs: 'primary',
    transfer_ops: 'info',
  }[role] || ''
}
function formatDateTime(s) {
  if (!s) return '-'
  const d = new Date(s)
  if (isNaN(d.getTime())) return s
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadData() {
  loading.value = true
  try {
    const res = await getAccounts({ page: 1, per_page: 100 })
    list.value = res.data?.list || []
    availableRoles.value = res.data?.available_roles || []
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Load failed')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = { username: '', name: '', role: 'cs', password: '', status: 1 }
}

function openCreate() {
  isEdit.value = false
  current.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  current.value = row
  form.value = {
    username: row.username,
    name: row.name || '',
    role: row.role,
    password: '',
    status: row.status,
  }
  dialogVisible.value = true
}

async function onSave() {
  saving.value = true
  try {
    if (isEdit.value) {
      const payload = {
        name: form.value.name,
      }
      // Owner 账号只能改 name
      if (current.value?.role !== 'owner') {
        payload.role = form.value.role
        payload.status = form.value.status
        if (form.value.password) payload.password = form.value.password
      }
      await updateAccount(current.value.id, payload)
    } else {
      if (!form.value.username || !form.value.password) {
        ElMessage.warning('Username and password are required')
        saving.value = false
        return
      }
      await createAccount({
        username: form.value.username,
        password: form.value.password,
        name: form.value.name,
        role: form.value.role,
      })
    }
    ElMessage.success(t('accounts.saved'))
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Save failed')
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(t('accounts.deleteConfirm'), '', {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    })
  } catch { return }
  try {
    await deleteAccount(row.id)
    ElMessage.success(t('accounts.deleted'))
    await loadData()
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || 'Failed')
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
