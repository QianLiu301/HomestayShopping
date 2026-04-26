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
      return null
    }

    try {
      const res = await getAdminInfo()
      user.value = res.data
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
  }

  return { user, token, initialized, fetchUser, initAuth, setToken, logout }
})
