import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAdminInfo } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('admin_token') || '')
  const initialized = ref(false)

  async function fetchUser() {
    if (!token.value) {
      user.value = null
      sessionStorage.removeItem('admin_role')
      return null
    }

    try {
      const res = await getAdminInfo()
      user.value = res.data
      // 缓存角色到 sessionStorage 让 router redirect 函数也能拿到
      if (user.value?.role) {
        sessionStorage.setItem('admin_role', user.value.role)
      }
      return user.value
    } catch {
      logout()
      return null
    }
  }

  async function initAuth() {
    if (initialized.value) return user.value
    initialized.value = true
    return fetchUser()
  }

  function setToken(t) {
    token.value = t
    localStorage.setItem('admin_token', t)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('admin_token')
    sessionStorage.removeItem('admin_role')
  }

  return { user, token, initialized, fetchUser, initAuth, setToken, logout }
})
