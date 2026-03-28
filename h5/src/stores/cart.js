import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref(JSON.parse(localStorage.getItem('cart') || '[]'))
  const selectedKeys = ref(JSON.parse(localStorage.getItem('cart_selected_keys') || '[]'))

  const normalizedSelectedKeys = computed(() =>
    selectedKeys.value.filter(key => items.value.some(item => item.key === key))
  )

  const selectedItems = computed(() =>
    items.value.filter(item => normalizedSelectedKeys.value.includes(item.key))
  )

  const totalCount = computed(() => items.value.reduce((sum, item) => sum + item.quantity, 0))
  const totalPrice = computed(() => items.value.reduce((sum, item) => sum + item.price * item.quantity, 0))
  const selectedCount = computed(() => selectedItems.value.reduce((sum, item) => sum + item.quantity, 0))
  const selectedPrice = computed(() => selectedItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0))
  const isAllSelected = computed(() => items.value.length > 0 && normalizedSelectedKeys.value.length === items.value.length)

  function save() {
    localStorage.setItem('cart', JSON.stringify(items.value))
    localStorage.setItem('cart_selected_keys', JSON.stringify(normalizedSelectedKeys.value))
  }

  function ensureSelected(key) {
    if (!selectedKeys.value.includes(key)) {
      selectedKeys.value.push(key)
    }
  }

  function addItem(product, spec = null) {
    const key = `${product.id}_${spec?.name || ''}`
    const existing = items.value.find(i => i.key === key)

    if (existing) {
      existing.quantity++
      ensureSelected(existing.key)
    } else {
      items.value.push({
        key,
        productId: product.id,
        name: product.name,
        image: product.images?.[0] || '',
        price: spec?.price ?? product.price,
        specName: spec?.name || null,
        quantity: 1
      })
      ensureSelected(key)
    }
    save()
  }

  function updateQuantity(key, quantity) {
    const item = items.value.find(i => i.key === key)
    if (item) {
      if (quantity <= 0) {
        removeItem(key)
        return
      }
      item.quantity = quantity
      save()
    }
  }

  function toggleSelect(key) {
    if (selectedKeys.value.includes(key)) {
      selectedKeys.value = selectedKeys.value.filter(itemKey => itemKey !== key)
    } else {
      selectedKeys.value.push(key)
    }
    save()
  }

  function selectAll() {
    selectedKeys.value = items.value.map(item => item.key)
    save()
  }

  function clearSelection() {
    selectedKeys.value = []
    save()
  }

  function toggleSelectAll() {
    if (isAllSelected.value) {
      clearSelection()
    } else {
      selectAll()
    }
  }

  function removeItem(key) {
    items.value = items.value.filter(i => i.key !== key)
    selectedKeys.value = selectedKeys.value.filter(itemKey => itemKey !== key)
    save()
  }

  function removeSelected() {
    if (!normalizedSelectedKeys.value.length) return
    items.value = items.value.filter(item => !normalizedSelectedKeys.value.includes(item.key))
    selectedKeys.value = []
    save()
  }

  function clear() {
    items.value = []
    selectedKeys.value = []
    save()
  }

  watch(items, () => {
    const validKeys = items.value.map(item => item.key)
    selectedKeys.value = selectedKeys.value.filter(key => validKeys.includes(key))
    localStorage.setItem('cart_selected_keys', JSON.stringify(selectedKeys.value))
  }, { deep: true })

  return {
    items,
    selectedKeys,
    selectedItems,
    totalCount,
    totalPrice,
    selectedCount,
    selectedPrice,
    isAllSelected,
    addItem,
    updateQuantity,
    toggleSelect,
    selectAll,
    clearSelection,
    toggleSelectAll,
    removeItem,
    removeSelected,
    clear,
  }
})
