import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

function parseStorage(key) {
  try {
    return JSON.parse(localStorage.getItem(key) || '[]')
  } catch {
    return []
  }
}

function normalizeTicketPackages(packages = []) {
  return packages
    .map(pkg => ({
      package_id: Number(pkg.package_id),
      package_name: pkg.package_name || '',
      quantity: Number(pkg.quantity || 0),
      ticket_type: pkg.ticket_type || '',
      price: Number(pkg.price || 0)
    }))
    .filter(pkg => pkg.package_id && pkg.quantity > 0)
    .sort((a, b) => a.package_id - b.package_id)
}

export const useCartStore = defineStore('cart', () => {
  const items = ref(parseStorage('cart'))
  const selectedKeys = ref(parseStorage('cart_selected_keys'))
  const ticketItems = ref(parseStorage('ticket_cart'))
  const ticketSelectedKeys = ref(parseStorage('ticket_cart_selected_keys'))

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

  const normalizedTicketSelectedKeys = computed(() =>
    ticketSelectedKeys.value.filter(key => ticketItems.value.some(item => item.key === key))
  )

  const selectedTicketItems = computed(() =>
    ticketItems.value.filter(item => normalizedTicketSelectedKeys.value.includes(item.key))
  )

  const ticketItemCount = computed(() => ticketItems.value.length)
  const ticketTotalQuantity = computed(() => ticketItems.value.reduce((sum, item) => sum + Number(item.total_quantity || 0), 0))
  const ticketSelectedCount = computed(() => selectedTicketItems.value.length)
  const ticketSelectedQuantity = computed(() => selectedTicketItems.value.reduce((sum, item) => sum + Number(item.total_quantity || 0), 0))
  const ticketSelectedPrice = computed(() => selectedTicketItems.value.reduce((sum, item) => sum + Number(item.total_price || 0), 0))
  const isAllTicketsSelected = computed(() => ticketItems.value.length > 0 && normalizedTicketSelectedKeys.value.length === ticketItems.value.length)

  function save() {
    localStorage.setItem('cart', JSON.stringify(items.value))
    localStorage.setItem('cart_selected_keys', JSON.stringify(normalizedSelectedKeys.value))
  }

  function saveTicket() {
    localStorage.setItem('ticket_cart', JSON.stringify(ticketItems.value))
    localStorage.setItem('ticket_cart_selected_keys', JSON.stringify(normalizedTicketSelectedKeys.value))
  }

  function ensureSelected(key) {
    if (!selectedKeys.value.includes(key)) {
      selectedKeys.value.push(key)
    }
  }

  function ensureTicketSelected(key) {
    if (!ticketSelectedKeys.value.includes(key)) {
      ticketSelectedKeys.value.push(key)
    }
  }

  function buildTicketItemKey(payload) {
    return `ticket_${payload.attraction_id}_${payload.visit_date}_${payload.transport_price_id || ''}`
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

  function addTicketItem(payload) {
    const packages = normalizeTicketPackages(payload.packages)
    if (!packages.length) return

    const totalQuantity = packages.reduce((sum, item) => sum + item.quantity, 0)
    const totalPrice = packages.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    const key = buildTicketItemKey(payload)
    const nextItem = {
      key,
      attraction_id: payload.attraction_id,
      attraction_name: payload.attraction_name,
      attraction_image: payload.attraction_image || '',
      visit_date: payload.visit_date,
      transport_price_id: payload.transport_price_id || '',
      packages,
      total_quantity: totalQuantity,
      total_price: Number(totalPrice.toFixed(2)),
      created_at: Date.now()
    }

    const index = ticketItems.value.findIndex(item => item.key === key)
    if (index > -1) {
      ticketItems.value.splice(index, 1, nextItem)
    } else {
      ticketItems.value.push(nextItem)
    }
    ensureTicketSelected(key)
    saveTicket()
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

  function toggleTicketSelect(key) {
    if (ticketSelectedKeys.value.includes(key)) {
      ticketSelectedKeys.value = ticketSelectedKeys.value.filter(itemKey => itemKey !== key)
    } else {
      ticketSelectedKeys.value.push(key)
    }
    saveTicket()
  }

  function selectAll() {
    selectedKeys.value = items.value.map(item => item.key)
    save()
  }

  function selectAllTickets() {
    ticketSelectedKeys.value = ticketItems.value.map(item => item.key)
    saveTicket()
  }

  function clearSelection() {
    selectedKeys.value = []
    save()
  }

  function clearTicketSelection() {
    ticketSelectedKeys.value = []
    saveTicket()
  }

  function toggleSelectAll() {
    if (isAllSelected.value) {
      clearSelection()
    } else {
      selectAll()
    }
  }

  function toggleSelectAllTickets() {
    if (isAllTicketsSelected.value) {
      clearTicketSelection()
    } else {
      selectAllTickets()
    }
  }

  function removeItem(key) {
    items.value = items.value.filter(i => i.key !== key)
    selectedKeys.value = selectedKeys.value.filter(itemKey => itemKey !== key)
    save()
  }

  function removeTicketItem(key) {
    ticketItems.value = ticketItems.value.filter(item => item.key !== key)
    ticketSelectedKeys.value = ticketSelectedKeys.value.filter(itemKey => itemKey !== key)
    saveTicket()
  }

  function removeSelected() {
    if (!normalizedSelectedKeys.value.length) return
    items.value = items.value.filter(item => !normalizedSelectedKeys.value.includes(item.key))
    selectedKeys.value = []
    save()
  }

  function removeSelectedTickets() {
    if (!normalizedTicketSelectedKeys.value.length) return
    ticketItems.value = ticketItems.value.filter(item => !normalizedTicketSelectedKeys.value.includes(item.key))
    ticketSelectedKeys.value = []
    saveTicket()
  }

  function clear() {
    items.value = []
    selectedKeys.value = []
    save()
  }

  function clearTicketCart() {
    ticketItems.value = []
    ticketSelectedKeys.value = []
    saveTicket()
  }

  watch(items, () => {
    const validKeys = items.value.map(item => item.key)
    selectedKeys.value = selectedKeys.value.filter(key => validKeys.includes(key))
    localStorage.setItem('cart_selected_keys', JSON.stringify(selectedKeys.value))
  }, { deep: true })

  watch(ticketItems, () => {
    const validKeys = ticketItems.value.map(item => item.key)
    ticketSelectedKeys.value = ticketSelectedKeys.value.filter(key => validKeys.includes(key))
    localStorage.setItem('ticket_cart_selected_keys', JSON.stringify(ticketSelectedKeys.value))
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
    ticketItems,
    ticketSelectedKeys,
    selectedTicketItems,
    ticketItemCount,
    ticketTotalQuantity,
    ticketSelectedCount,
    ticketSelectedQuantity,
    ticketSelectedPrice,
    isAllTicketsSelected,
    addTicketItem,
    toggleTicketSelect,
    selectAllTickets,
    clearTicketSelection,
    toggleSelectAllTickets,
    removeTicketItem,
    removeSelectedTickets,
    clearTicketCart
  }
})
