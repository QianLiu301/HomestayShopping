<template>
  <div class="page-container page-with-tabbar">
    <van-nav-bar :title="t('cart.title')">
      <template #right>
        <span v-if="hasAnyCartItems" class="manage-btn" @click="manageMode = !manageMode">
          {{ manageMode ? t('cart.complete') : t('cart.manage') }}
        </span>
      </template>
    </van-nav-bar>

    <div v-if="isTicketMode && !cart.ticketItems.length" class="empty-cart">
      <van-empty :description="t('cart.empty')">
        <div class="empty-actions">
          <van-button round plain size="small" @click="$router.push('/tickets')">
            {{ t('tickets.title') }}
          </van-button>
        </div>
      </van-empty>
    </div>

    <div v-else-if="!isTicketMode && !cart.items.length" class="empty-cart">
      <van-empty :description="t('cart.empty')">
        <div class="empty-actions">
          <van-button round type="primary" size="small" @click="$router.push('/shop')">
            {{ t('cart.goShop') }}
          </van-button>
          <van-button round plain size="small" @click="$router.push('/tickets')">
            {{ t('tickets.title') }}
          </van-button>
        </div>
      </van-empty>
    </div>

    <template v-else-if="isTicketMode">
      <div class="cart-toolbar">
        <van-checkbox :model-value="cart.isAllTicketsSelected" icon-size="18" @update:model-value="cart.toggleSelectAllTickets()">
          {{ t('cart.selectAll') }}
        </van-checkbox>
        <div class="toolbar-actions">
          <van-button size="small" plain type="danger" @click="cart.removeSelectedTickets()">
            {{ t('cart.clearSelected') }}
          </van-button>
          <van-button size="small" plain @click="cart.clearTicketCart()">
            {{ t('cart.clearCart') }}
          </van-button>
        </div>
      </div>

      <div class="ticket-cart-section">
        <div class="ticket-cart-section__head">
          <div class="ticket-cart-section__title">{{ t('tickets.title') }}</div>
        </div>
        <div v-for="item in cart.ticketItems" :key="item.key" class="ticket-cart-item">
          <div class="cart-check" @click.stop>
            <van-checkbox
              :model-value="cart.ticketSelectedKeys.includes(item.key)"
              icon-size="18"
              @update:model-value="cart.toggleTicketSelect(item.key)"
            />
          </div>
          <div class="ticket-cart-item__main" @click="goToTicketDetail(item)">
            <img v-if="item.attraction_image" :src="$resolveUrl(item.attraction_image)" class="cart-img" />
            <div v-else class="cart-img placeholder">{{ item.attraction_name?.charAt(0) || 'T' }}</div>
            <div class="cart-info">
              <div class="cart-name">{{ item.attraction_name }}</div>
              <div class="cart-spec">{{ item.visit_date }}</div>
              <div class="ticket-cart-packages">
                <div v-for="pkg in item.packages" :key="`${item.key}_${pkg.package_id}`" class="ticket-cart-package-row">
                  <span>{{ pkg.package_name }} × {{ pkg.quantity }}</span>
                  <span>¥{{ pkg.price }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="ticket-cart-side" @click.stop>
            <div class="ticket-cart-side__price">¥{{ item.total_price }}</div>
            <div class="ticket-cart-actions">
              <van-button size="small" plain @click="goToTicketCheckout(item)">
                {{ t('cart.checkout') }}
              </van-button>
              <van-button v-if="manageMode" size="small" plain type="danger" @click="cart.removeTicketItem(item.key)">
                {{ t('cart.delete') }}
              </van-button>
            </div>
          </div>
        </div>
      </div>

      <div class="cart-footer-space"></div>

      <van-submit-bar
        :price="cart.ticketSelectedPrice * 100"
        :button-text="t('cart.checkoutSelected')"
        :label="t('cart.total') + '：'"
        currency="¥"
        @submit="onTicketCheckout"
      >
        <template #tip>
          {{ t('cart.selected', { count: cart.ticketSelectedQuantity }) }}
        </template>
      </van-submit-bar>
    </template>

    <template v-else>
      <div class="cart-toolbar">
        <van-checkbox :model-value="cart.isAllSelected" icon-size="18" @update:model-value="cart.toggleSelectAll()">
          {{ t('cart.selectAll') }}
        </van-checkbox>
        <div class="toolbar-actions">
          <van-button size="small" plain type="danger" @click="cart.removeSelected()">
            {{ t('cart.clearSelected') }}
          </van-button>
          <van-button size="small" plain @click="cart.clear()">
            {{ t('cart.clearCart') }}
          </van-button>
        </div>
      </div>

      <van-swipe-cell v-for="item in cart.items" :key="item.key" :disabled="manageMode">
        <div class="cart-item">
          <div class="cart-check" @click.stop>
            <van-checkbox
              :model-value="cart.selectedKeys.includes(item.key)"
              icon-size="18"
              @update:model-value="cart.toggleSelect(item.key)"
            />
          </div>
          <div class="cart-content" @click="$router.push(`/product/${item.productId}`)">
            <img v-if="item.image" :src="$resolveUrl(item.image)" class="cart-img" />
            <div v-else class="cart-img placeholder">{{ item.name?.charAt(0) }}</div>
            <div class="cart-info">
              <div class="cart-name">{{ item.name }}</div>
              <div v-if="item.specName" class="cart-spec">{{ item.specName }}</div>
              <div class="cart-bottom">
                <span class="cart-price">¥{{ item.price }}</span>
                <div class="cart-actions" @click.stop>
                  <van-button v-if="manageMode" size="small" plain type="danger" @click="cart.removeItem(item.key)">
                    {{ t('cart.delete') }}
                  </van-button>
                  <van-stepper
                    v-else
                    :model-value="item.quantity"
                    min="1"
                    max="99"
                    theme="round"
                    @change="(v) => cart.updateQuantity(item.key, v)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <template #right>
          <van-button square type="danger" :text="t('cart.delete')" class="delete-btn" @click="cart.removeItem(item.key)" />
        </template>
      </van-swipe-cell>

      <div class="cart-footer-space"></div>

      <van-submit-bar
        :price="cart.selectedPrice * 100"
        :button-text="t('cart.checkoutSelected')"
        :label="t('cart.total') + '：'"
        currency="¥"
        @submit="onCheckout"
      >
        <template #tip>
          {{ t('cart.selectedItems', { count: cart.selectedCount }) }}
        </template>
      </van-submit-bar>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { showToast } from 'vant'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCartStore } from '../stores/cart'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const manageMode = ref(route.query.tab === 'ticket')

const isTicketMode = computed(() => route.query.tab === 'ticket' || (!cart.items.length && cart.ticketItems.length > 0))
const hasAnyCartItems = computed(() => cart.items.length > 0 || cart.ticketItems.length > 0)

function goToTicketDetail(item) {
  router.push(`/tickets/${item.attraction_id}`)
}

function goToTicketCheckout(item) {
  router.push({
    path: '/ticket-checkout',
    query: {
      attraction_id: String(item.attraction_id),
      package_id: String(item.packages?.[0]?.package_id || ''),
      package_selections: JSON.stringify((item.packages || []).map(pkg => ({
        package_id: pkg.package_id,
        quantity: pkg.quantity
      }))),
      visit_date: item.visit_date,
      transport_price_id: item.transport_price_id ? String(item.transport_price_id) : ''
    }
  })
}

function onTicketCheckout() {
  if (!cart.ticketSelectedKeys.length) {
    showToast(t('cart.noSelected'))
    return
  }
  if (cart.selectedTicketItems.length > 1) {
    showToast(locale.value === 'en' ? 'Ticket checkout supports one selection at a time' : '门票购物车暂不支持多条同时结算，请只选择一项')
    return
  }
  goToTicketCheckout(cart.selectedTicketItems[0])
}

function onCheckout() {
  if (!cart.selectedKeys.length) {
    showToast(t('cart.noSelected'))
    return
  }
  router.push('/checkout')
}
</script>

<style scoped>
.empty-cart {
  padding-top: 80px;
}

.empty-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.manage-btn {
  font-size: 14px;
  color: var(--accent);
  cursor: pointer;
}

.cart-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--white);
  border-bottom: 1px solid var(--border);
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.ticket-cart-section {
  margin: 12px 16px 0;
  padding: 14px;
  border-radius: 16px;
  background: var(--white);
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.ticket-cart-section__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.ticket-cart-section__title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.ticket-cart-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px 0;
}

.ticket-cart-item + .ticket-cart-item {
  border-top: 1px solid var(--border);
}

.ticket-cart-item__main {
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.ticket-cart-side {
  min-width: 116px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}

.ticket-cart-side__price {
  font-size: 16px;
  font-weight: 700;
  color: var(--accent);
}

.cart-item {
  display: flex;
  padding: 12px 16px;
  background: var(--white);
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid var(--border);
}

.cart-check {
  flex-shrink: 0;
}

.cart-content {
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.cart-img {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.cart-img.placeholder {
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--text-light);
}

.cart-info {
  flex: 1;
  min-width: 0;
}

.cart-name {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cart-spec {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 4px;
  background: #f5f5f5;
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
}

.cart-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.ticket-cart-packages {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ticket-cart-package-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.cart-price {
  font-size: 16px;
  font-weight: 700;
  color: var(--accent);
}

.cart-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.ticket-cart-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cart-footer-space {
  height: 72px;
}

.delete-btn {
  height: 100%;
}

:deep(.van-submit-bar) {
  bottom: 50px;
}

@media (max-width: 768px) {
  .ticket-cart-item {
    flex-wrap: wrap;
  }

  .ticket-cart-item__main {
    flex: 1 1 calc(100% - 30px);
    align-items: flex-start;
  }

  .ticket-cart-side {
    margin-left: auto;
    min-width: 0;
    width: calc(100% - 30px);
    align-items: flex-end;
  }
}
</style>
