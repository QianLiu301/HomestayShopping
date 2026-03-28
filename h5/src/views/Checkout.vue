<template>
  <div class="page-container">
    <van-nav-bar :title="t('checkout.title')" left-arrow @click-left="$router.back()" />

    <div v-if="pageLoading" style="text-align: center; padding: 60px;">
      <van-loading size="24" />
    </div>

    <template v-else>
      <!-- Order items summary -->
      <div class="card">
        <div class="card-title">{{ t('checkout.orderItems') }} ({{ cart.selectedCount }})</div>
        <div class="order-items">
          <div v-for="item in cart.selectedItems" :key="item.key" class="checkout-item">
            <img v-if="item.image" :src="$resolveUrl(item.image)" class="item-img" />
            <div v-else class="item-img placeholder">{{ item.name?.charAt(0) }}</div>
            <div class="item-info">
              <div class="item-name">{{ item.name }}</div>
              <div v-if="item.specName" class="item-spec">{{ item.specName }}</div>
              <div class="item-bottom">
                <span class="item-price">¥{{ item.price }}</span>
                <span class="item-qty">x{{ item.quantity }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Booking info -->
      <div class="card">
        <div class="card-title">{{ t('checkout.deliveryInfo') }}</div>
        <van-field
          v-model="form.booking_no"
          :label="t('checkout.bookingNo')"
          :placeholder="t('checkout.bookingNoPlaceholder')"
          required
        />
        <div class="booking-tip">{{ t('checkout.bookingNoTip') }}</div>
      </div>

      <!-- Expected delivery -->
      <div class="card">
        <div class="card-title">{{ t('checkout.expectedDelivery') }}</div>
        <van-field
          v-model="form.expected_delivery_date"
          :label="t('checkout.expectedDate')"
          :placeholder="t('checkout.expectedDatePlaceholder')"
          readonly
          is-link
          @click="showDatePicker = true"
        />
        <van-popup v-model:show="showDatePicker" position="bottom" round>
          <van-date-picker
            v-model="datePickerValue"
            :title="t('checkout.expectedDate')"
            :min-date="minDate"
            @confirm="onDateConfirm"
            @cancel="showDatePicker = false"
          />
        </van-popup>
        <van-field :label="t('checkout.expectedTime')" v-if="form.expected_delivery_date">
          <template #input>
            <van-radio-group v-model="form.expected_delivery_time" direction="horizontal">
              <van-radio name="morning">{{ t('checkout.morning') }}</van-radio>
              <van-radio name="afternoon">{{ t('checkout.afternoon') }}</van-radio>
              <van-radio name="evening">{{ t('checkout.evening') }}</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        <div class="delivery-tip">
          {{ form.expected_delivery_date ? '' : t('checkout.defaultDeliveryTip') }}
        </div>
      </div>

      <!-- Contact -->
      <div class="card">
        <div class="card-title">{{ t('checkout.contact') }}</div>
        <van-field v-model="form.contact_name" :label="t('checkout.contactName')" :placeholder="t('checkout.contactNamePlaceholder')" required />
        <van-field v-model="form.contact_phone" :label="t('checkout.contactPhone')" :placeholder="t('checkout.contactPhonePlaceholder')" type="tel" />
        <van-field v-model="form.contact_email" :label="t('checkout.contactEmail')" :placeholder="t('checkout.contactEmailPlaceholder')" type="email" />
        <van-field v-model="form.remark" :label="t('checkout.remark')" :placeholder="t('checkout.remarkPlaceholder')" type="textarea" rows="2" autosize />
      </div>

      <!-- Coupon -->
      <div class="card">
        <div class="card-title">{{ t('checkout.coupon') }}</div>
        <div class="coupon-row">
          <van-field v-model="couponCode" :placeholder="t('checkout.couponPlaceholder')" style="flex:1" />
          <van-button size="small" type="primary" :loading="couponLoading" @click="onVerifyCoupon">{{ t('checkout.verify') }}</van-button>
        </div>
        <div v-if="couponDiscount > 0" class="coupon-msg success">
          {{ t('checkout.couponValid', { amount: couponDiscount }) }}
        </div>
      </div>

      <!-- Price summary -->
      <div class="card">
        <div class="price-line">
          <span>{{ t('checkout.subtotal') }}</span>
          <span>¥{{ cart.selectedPrice.toFixed(2) }}</span>
        </div>
        <div v-if="couponDiscount > 0" class="price-line discount">
          <span>{{ t('checkout.discount') }}</span>
          <span>-¥{{ couponDiscount }}</span>
        </div>
        <div class="price-line total">
          <span>{{ t('checkout.totalPrice') }}</span>
          <span class="total-amount">¥{{ finalPrice }}</span>
        </div>
      </div>

      <!-- Agree to terms -->
      <div class="card agree-card">
        <van-checkbox v-model="agreeTerms" icon-size="16">
          <span class="agree-text">
            {{ t('legal.agreePrefix') }}
            <router-link to="/privacy" class="agree-link">{{ t('legal.privacyPolicy') }}</router-link>
            {{ t('legal.agreeAnd') }}
            <router-link to="/terms" class="agree-link">{{ t('legal.termsOfService') }}</router-link>
          </span>
        </van-checkbox>
      </div>

      <!-- Validation error banner -->
      <div v-if="errorMsg" class="error-banner">
        <van-icon name="warning-o" size="18" />
        <span>{{ errorMsg }}</span>
      </div>

      <!-- Submit -->
      <div style="padding: 16px;">
        <van-button round block type="primary" size="large" :loading="submitting" @click="onSubmit">
          {{ t('checkout.placeOrder') }} ¥{{ finalPrice }}
        </van-button>
      </div>
      <div style="height: 20px;"></div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { createShopOrder, verifyCoupon } from '../api'
import { useCartStore } from '../stores/cart'

const { t } = useI18n()
const router = useRouter()
const cart = useCartStore()

const pageLoading = ref(false)
const submitting = ref(false)
const errorMsg = ref('')

const form = reactive({
  booking_no: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  remark: '',
  expected_delivery_date: '',
  expected_delivery_time: ''
})

const showDatePicker = ref(false)
const now = new Date()
const minDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
const datePickerValue = ref([String(now.getFullYear()), String(now.getMonth() + 1).padStart(2, '0'), String(now.getDate()).padStart(2, '0')])

function onDateConfirm({ selectedValues }) {
  form.expected_delivery_date = selectedValues.join('-')
  if (!form.expected_delivery_time) form.expected_delivery_time = 'morning'
  showDatePicker.value = false
}

const couponCode = ref('')
const couponDiscount = ref(0)
const couponLoading = ref(false)

const pendingOrderNo = ref('')
const pendingAmount = ref('')
const agreeTerms = ref(false)

const finalPrice = computed(() =>
  Math.max(0, cart.selectedPrice - couponDiscount.value).toFixed(2)
)

async function onVerifyCoupon() {
  if (!couponCode.value) return
  couponLoading.value = true
  try {
    const res = await verifyCoupon({
      code: couponCode.value,
      amount: cart.selectedPrice,
      apply_to: 'shop'
    })
    couponDiscount.value = res.data?.discount_amount || 0
  } catch (e) {
    couponDiscount.value = 0
    showToast(t('checkout.couponInvalid'))
  } finally {
    couponLoading.value = false
  }
}

function validationFail(msg) {
  errorMsg.value = msg
  setTimeout(() => {
    const banner = document.querySelector('.error-banner')
    if (banner) banner.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 50)
  setTimeout(() => { errorMsg.value = '' }, 5000)
}

async function onSubmit() {
  try {
    // Validate booking number
    if (!form.booking_no.trim()) { validationFail(t('checkout.bookingNoRequired')); return }

    // Validate contact info
    if (!form.contact_name.trim()) { validationFail(t('checkout.contactNameRequired')); return }
    if (!form.contact_phone.trim() && !form.contact_email.trim()) { validationFail(t('checkout.phoneOrEmail')); return }

    // Terms
    if (!agreeTerms.value) { validationFail(t('transfer.agreeRequired')); return }

    errorMsg.value = ''

    const data = {
      booking_no: form.booking_no,
      contact_name: form.contact_name,
      contact_phone: form.contact_phone,
      contact_email: form.contact_email,
      remark: form.remark,
      items: cart.selectedItems.map(item => ({
        product_id: item.productId,
        quantity: item.quantity,
        spec_name: item.specName || undefined
      }))
    }

    if (form.expected_delivery_date) {
      data.expected_delivery_date = form.expected_delivery_date
      if (form.expected_delivery_time) data.expected_delivery_time = form.expected_delivery_time
    }

    if (couponCode.value && couponDiscount.value > 0) {
      data.coupon_code = couponCode.value
    }

    submitting.value = true
    const res = await createShopOrder(data)
    cart.removeSelected()
    pendingOrderNo.value = res.data?.order_no || res.order_no || ''
    pendingAmount.value = res.data?.total_price || res.total_price || ''
    goToResult()
  } catch (e) {
    console.error('Submit order error:', e)
    errorMsg.value = e.message || String(e)
  } finally {
    submitting.value = false
  }
}

function goToResult() {
  router.replace({
    path: '/order-result',
    query: {
      orderNo: pendingOrderNo.value,
      amount: pendingAmount.value,
      type: 'shop'
    }
  })
}

onMounted(() => {
  if (!cart.items.length || !cart.selectedItems.length) {
    router.replace('/cart')
  }
})
</script>

<style scoped>
.order-items {
  max-height: 200px;
  overflow-y: auto;
}

.checkout-item {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.checkout-item:last-child {
  border-bottom: none;
}

.item-img {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.item-img.placeholder {
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: var(--text-light);
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 13px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-spec {
  font-size: 11px;
  color: var(--text-light);
  margin-top: 2px;
}

.item-bottom {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
}

.item-price {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent);
}

.item-qty {
  font-size: 13px;
  color: var(--text-light);
}

.delivery-tip {
  padding: 8px 16px;
  font-size: 12px;
  color: #e6a23c;
  line-height: 1.5;
  min-height: 20px;
}

.booking-tip {
  padding: 8px 16px;
  font-size: 12px;
  color: var(--text-light);
  line-height: 1.5;
}

.coupon-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.coupon-msg.success {
  margin-top: 8px;
  font-size: 13px;
  color: var(--success);
}

.price-line {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.price-line.discount {
  color: var(--success);
}

.price-line.total {
  border-top: 1px solid var(--border);
  margin-top: 4px;
  padding-top: 12px;
  font-weight: 600;
  color: var(--text);
}

.total-amount {
  font-size: 20px;
  color: var(--accent);
}

.agree-card { padding: 12px 16px; }
.agree-text { font-size: 12px; color: var(--text-secondary); line-height: 1.6; }
.agree-link { color: var(--accent); text-decoration: underline; }

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 16px;
  padding: 12px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  color: #ff4d4f;
  font-size: 14px;
  font-weight: 500;
  animation: shake 0.4s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-6px); }
  75% { transform: translateX(6px); }
}
</style>
