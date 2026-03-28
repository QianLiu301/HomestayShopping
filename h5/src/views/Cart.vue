<template>
  <div class="page-container page-with-tabbar">
    <van-nav-bar :title="t('cart.title')">
      <template #right>
        <span v-if="cart.items.length" class="manage-btn" @click="manageMode = !manageMode">
          {{ manageMode ? t('cart.complete') : t('cart.manage') }}
        </span>
      </template>
    </van-nav-bar>

    <div v-if="!cart.items.length" class="empty-cart">
      <van-empty :description="t('cart.empty')">
        <van-button round type="primary" size="small" @click="$router.push('/shop')">
          {{ t('cart.goShop') }}
        </van-button>
      </van-empty>
    </div>

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

      <div style="height: 110px;"></div>

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
import { ref } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCartStore } from '../stores/cart'

const { t } = useI18n()
const router = useRouter()
const cart = useCartStore()
const manageMode = ref(false)

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

.delete-btn {
  height: 100%;
}

:deep(.van-submit-bar) {
  bottom: 50px;
}
</style>
