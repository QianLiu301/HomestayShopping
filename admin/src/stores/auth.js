import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAdminInfo } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('admin_token') || '')

  async function fetchUser() {
    if (!token.value) return
    try {
      const res = await getAdminInfo()
      user.value = res.data
    } catch { user.value = null }
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

  return { user, token, fetchUser, setToken, logout }
})
