<template>
  <div class="page-container">
    <van-nav-bar :title="t('transfer.title')" left-arrow @click-left="$router.back()" />

    <div v-if="pageLoading" style="text-align: center; padding: 60px;">
      <van-loading size="24" />
    </div>

    <template v-else>
      <!-- Service type -->
      <div class="card">
        <div class="card-title">{{ t('transfer.title') }}</div>
        <van-radio-group v-model="form.service_type" direction="horizontal" class="service-radios">
          <van-radio name="pickup">{{ t('transfer.pickup') }}</van-radio>
          <van-radio name="dropoff">{{ t('transfer.dropoff') }}</van-radio>
          <van-radio name="combo">{{ t('transfer.combo') }}</van-radio>
        </van-radio-group>
        <div v-if="form.service_type === 'combo' && pricing" class="combo-tip">
          {{ t('transfer.comboDiscount', { discount: pricing.combo_discount }) }}
        </div>
      </div>

      <!-- Vehicle selection -->
      <div class="card">
        <div class="card-title">{{ t('transfer.selectVehicle') }} <span class="required">*</span></div>
        <div class="vehicle-list">
          <div
            v-for="v in vehicles"
            :key="v.id"
            class="vehicle-card"
            :class="{ active: form.vehicle_id === v.id }"
            @click="form.vehicle_id = v.id"
          >
            <div class="vehicle-icon">
              <van-icon name="logistics" size="28" :color="form.vehicle_id === v.id ? '#1a73e8' : '#999'" />
            </div>
            <div class="vehicle-info">
              <div class="vehicle-name">{{ v.name }}</div>
              <div class="vehicle-desc">
                {{ t('transfer.seats', { n: v.seats }) }} · {{ t('transfer.luggage', { n: v.luggage_capacity }) }}
              </div>
            </div>
            <div class="vehicle-price">
              {{ v.extra_price > 0 ? t('transfer.extraPrice', { price: v.extra_price }) : t('transfer.noExtra') }}
            </div>
          </div>
        </div>
      </div>

      <!-- ============ PICKUP SECTION ============ -->
      <div v-if="form.service_type === 'pickup' || form.service_type === 'combo'" class="card">
        <div class="card-title section-title pickup-title">
          <van-icon name="guide-o" size="18" />
          {{ t('transfer.pickupInfo') }}
        </div>

        <!-- Airport selection -->
        <div class="field-label">{{ t('transfer.selectAirport') }} <span class="required">*</span></div>
        <van-radio-group v-model="form.pickup_airport" direction="horizontal" class="airport-radios">
          <van-radio name="PVG">
            <div class="airport-label">{{ t('transfer.pudongAirport') }} <span class="airport-code">PVG</span></div>
          </van-radio>
          <van-radio name="SHA">
            <div class="airport-label">{{ t('transfer.hongqiaoAirport') }} <span class="airport-code">SHA</span></div>
          </van-radio>
        </van-radio-group>

        <!-- Flight info -->
        <van-field
          v-model="form.flight_no"
          :label="t('transfer.flightNo')"
          :placeholder="t('transfer.flightNoPlaceholder')"
          required
        />
        <van-field
          :label="t('transfer.flightTime')"
          :model-value="form.flight_time ? formatDate(form.flight_time) : ''"
          :placeholder="t('transfer.flightTime')"
          readonly
          is-link
          @click="activeDatePicker = 'pickup'; showDatePicker = true"
        />

        <!-- Route display -->
        <div class="route-display" v-if="form.pickup_airport">
          <div class="route-point from">
            <van-icon name="location-o" color="#1a73e8" />
            <span>{{ airportName(form.pickup_airport) }}</span>
          </div>
          <div class="route-arrow">→</div>
          <div class="route-point to">
            <van-icon name="wap-home-o" color="#8b6f47" />
            <span>{{ form.booking_no || t('transfer.bookingNo') }}</span>
          </div>
        </div>
      </div>

      <!-- ============ DROPOFF SECTION ============ -->
      <div v-if="form.service_type === 'dropoff' || form.service_type === 'combo'" class="card">
        <div class="card-title section-title dropoff-title">
          <van-icon name="logistics" size="18" />
          {{ t('transfer.dropoffInfo') }}
        </div>

        <!-- Airport selection -->
        <div class="field-label">{{ t('transfer.selectAirport') }} <span class="required">*</span></div>
        <van-radio-group v-model="dropoffAirport" direction="horizontal" class="airport-radios">
          <van-radio name="PVG">
            <div class="airport-label">{{ t('transfer.pudongAirport') }} <span class="airport-code">PVG</span></div>
          </van-radio>
          <van-radio name="SHA">
            <div class="airport-label">{{ t('transfer.hongqiaoAirport') }} <span class="airport-code">SHA</span></div>
          </van-radio>
        </van-radio-group>

        <!-- Flight info -->
        <van-field
          v-model="dropoffFlightNo"
          :label="t('transfer.flightNo')"
          :placeholder="t('transfer.flightNoPlaceholder')"
          required
        />
        <van-field
          :label="t('transfer.flightTime')"
          :model-value="dropoffFlightTime ? formatDate(dropoffFlightTime) : ''"
          :placeholder="t('transfer.flightTime')"
          readonly
          is-link
          @click="activeDatePicker = 'dropoff'; showDatePicker = true"
        />

        <!-- Route display -->
        <div class="route-display" v-if="dropoffAirport">
          <div class="route-point from">
            <van-icon name="wap-home-o" color="#8b6f47" />
            <span>{{ form.booking_no || t('transfer.bookingNo') }}</span>
          </div>
          <div class="route-arrow">→</div>
          <div class="route-point to">
            <van-icon name="location-o" color="#1a73e8" />
            <span>{{ airportName(dropoffAirport) }}</span>
          </div>
        </div>
      </div>

      <!-- ============ BOOKING NUMBER ============ -->
      <div class="card">
        <div class="card-title">{{ t('transfer.bookingNo') }} <span class="required">*</span></div>
        <van-field
          v-model="form.booking_no"
          :placeholder="t('transfer.bookingNoPlaceholder')"
        />
        <div class="booking-tip">{{ t('transfer.bookingNoTip') }}</div>
      </div>

      <!-- Contact info -->
      <div class="card">
        <div class="card-title">{{ t('transfer.contactInfo') }}</div>
        <van-field v-model="form.contact_name" :label="t('transfer.contactName')" :placeholder="t('transfer.contactName')" required />
        <van-field v-model="form.contact_phone" :label="t('transfer.contactPhone')" :placeholder="t('transfer.contactPhone')" type="tel">
          <template #label>
            <span>{{ t('transfer.contactPhone') }}</span>
            <span class="field-hint">{{ t('transfer.phoneOrEmailHint') }}</span>
          </template>
        </van-field>
        <van-field v-model="form.contact_email" :label="t('transfer.contactEmail')" :placeholder="t('transfer.contactEmail')" type="email">
          <template #label>
            <span>{{ t('transfer.contactEmail') }}</span>
            <span class="field-hint">{{ t('transfer.phoneOrEmailHint') }}</span>
          </template>
        </van-field>
        <van-field v-model="form.remark" :label="t('transfer.remark')" :placeholder="t('transfer.remarkPlaceholder')" type="textarea" rows="2" autosize />
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

      <!-- Price detail -->
      <div class="card">
        <div class="card-title">{{ t('transfer.priceDetail') }}</div>
        <div class="price-line">
          <span>{{ t('transfer.basePrice') }}</span>
          <span>¥{{ basePrice }}</span>
        </div>
        <div class="price-line">
          <span>{{ t('transfer.vehicleExtra') }}</span>
          <span>¥{{ vehicleExtra }}</span>
        </div>
        <div v-if="couponDiscount > 0" class="price-line discount">
          <span>{{ t('transfer.discount') }}</span>
          <span>-¥{{ couponDiscount }}</span>
        </div>
        <div class="price-line total">
          <span>{{ t('transfer.totalPrice') }}</span>
          <span class="total-amount">¥{{ totalPrice }}</span>
        </div>
      </div>

      <!-- Payment -->
      <div class="card">
        <div class="card-title">{{ t('checkout.payment') }} <span class="required">*</span></div>
        <van-radio-group v-model="form.payment_method">
          <van-cell-group :border="false">
            <van-cell :title="t('checkout.wechat')" clickable @click="form.payment_method = 'wechat'">
              <template #right-icon><van-radio name="wechat" /></template>
            </van-cell>
            <van-cell :title="t('checkout.alipay')" clickable @click="form.payment_method = 'alipay'">
              <template #right-icon><van-radio name="alipay" /></template>
            </van-cell>
            <van-cell :title="t('checkout.creditCard')" clickable @click="form.payment_method = 'credit_card'">
              <template #right-icon><van-radio name="credit_card" /></template>
            </van-cell>
          </van-cell-group>
        </van-radio-group>
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

      <!-- Submit -->
      <div style="padding: 16px;">
        <van-button round block type="primary" size="large" :loading="submitting" :disabled="!agreeTerms" @click="onSubmit">
          {{ t('transfer.submitOrder') }} ¥{{ totalPrice }}
        </van-button>
      </div>
      <div style="height: 20px;"></div>
    </template>

    <!-- Date picker popup -->
    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        v-model="datePickerValue"
        :title="t('transfer.flightTime')"
        :min-date="new Date()"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <!-- Payment QR popup -->
    <PaymentPopup
      v-model:show="showPaymentPopup"
      :method="form.payment_method"
      :amount="totalPrice"
      :order-no="pendingOrderNo"
      @paid="onPaymentConfirmed"
      @cancel="onPaymentCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getVehicles, getTransferPrice, createTransferOrder, verifyCoupon } from '../api'
import PaymentPopup from '../components/PaymentPopup.vue'

const { t } = useI18n()
const router = useRouter()

const pageLoading = ref(true)
const submitting = ref(false)
const vehicles = ref([])
const pricing = ref(null)

const form = reactive({
  service_type: 'pickup',
  vehicle_id: null,
  pickup_airport: 'PVG',
  flight_no: '',
  flight_time: null,
  booking_no: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  remark: '',
  payment_method: 'wechat'
})

// Dropoff fields (separate for combo, shared for single dropoff)
const dropoffAirport = ref('PVG')
const dropoffFlightNo = ref('')
const dropoffFlightTime = ref(null)

const couponCode = ref('')
const couponDiscount = ref(0)
const couponLoading = ref(false)

const showDatePicker = ref(false)
const activeDatePicker = ref('pickup') // 'pickup' or 'dropoff'
const showPaymentPopup = ref(false)
const pendingOrderNo = ref('')
const pendingAmount = ref('')
const agreeTerms = ref(false)

const now = new Date()
const datePickerValue = ref([
  String(now.getFullYear()),
  String(now.getMonth() + 1).padStart(2, '0'),
  String(now.getDate()).padStart(2, '0')
])

const selectedVehicle = computed(() => vehicles.value.find(v => v.id === form.vehicle_id))

const basePrice = computed(() => {
  if (!pricing.value) return 0
  if (form.service_type === 'pickup') return pricing.value.pickup_price
  if (form.service_type === 'dropoff') return pricing.value.dropoff_price
  return pricing.value.combo_price
})

const vehicleExtra = computed(() => selectedVehicle.value?.extra_price || 0)

const totalPrice = computed(() =>
  Math.max(0, basePrice.value + vehicleExtra.value - couponDiscount.value)
)

function airportName(code) {
  if (code === 'PVG') return t('transfer.pudongAirport') + ' (PVG)'
  if (code === 'SHA') return t('transfer.hongqiaoAirport') + ' (SHA)'
  return code
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function onDateConfirm({ selectedValues }) {
  const [y, m, d] = selectedValues
  const val = `${y}-${m}-${d}T00:00:00`
  if (activeDatePicker.value === 'dropoff') {
    dropoffFlightTime.value = val
  } else {
    form.flight_time = val
  }
  showDatePicker.value = false
}

async function onVerifyCoupon() {
  if (!couponCode.value) return
  couponLoading.value = true
  try {
    const res = await verifyCoupon({
      code: couponCode.value,
      amount: basePrice.value + vehicleExtra.value,
      apply_to: 'transfer'
    })
    couponDiscount.value = res.data?.discount_amount || 0
  } catch (e) {
    couponDiscount.value = 0
    showToast(t('checkout.couponInvalid'))
  } finally {
    couponLoading.value = false
  }
}

async function onSubmit() {
  const st = form.service_type

  // Vehicle
  if (!form.vehicle_id) return showToast(t('transfer.selectVehicle'))

  // Pickup validation
  if (st === 'pickup' || st === 'combo') {
    if (!form.pickup_airport) return showToast(t('transfer.selectAirportTip'))
    if (!form.flight_no.trim()) return showToast(t('transfer.flightNoRequired'))
  }

  // Dropoff validation
  if (st === 'dropoff') {
    if (!dropoffAirport.value) return showToast(t('transfer.selectAirportTip'))
    if (!dropoffFlightNo.value.trim()) return showToast(t('transfer.flightNoRequired'))
  }
  if (st === 'combo') {
    if (!dropoffAirport.value) return showToast(t('transfer.selectAirportTip'))
    if (!dropoffFlightNo.value.trim()) return showToast(t('transfer.flightNoRequired'))
  }

  // Booking number
  if (!form.booking_no.trim()) return showToast(t('transfer.bookingNoRequired'))

  // Contact
  if (!form.contact_name.trim()) return showToast(t('transfer.contactNameRequired'))
  if (!form.contact_phone.trim() && !form.contact_email.trim()) return showToast(t('checkout.phoneOrEmail'))

  // Build payload
  const data = {
    service_type: st,
    vehicle_id: form.vehicle_id,
    booking_no: form.booking_no,
    contact_name: form.contact_name,
    contact_phone: form.contact_phone,
    contact_email: form.contact_email,
    payment_method: form.payment_method,
    remark: form.remark
  }

  // Flight info per service type
  if (st === 'pickup') {
    data.pickup_airport = form.pickup_airport
    data.flight_no = form.flight_no
    data.flight_time = form.flight_time
  } else if (st === 'dropoff') {
    data.dropoff_airport = dropoffAirport.value
    data.flight_no = dropoffFlightNo.value
    data.flight_time = dropoffFlightTime.value
  } else {
    // combo
    data.pickup_airport = form.pickup_airport
    data.flight_no = form.flight_no
    data.flight_time = form.flight_time
    data.dropoff_airport = dropoffAirport.value
    data.dropoff_flight_no = dropoffFlightNo.value
    data.dropoff_flight_time = dropoffFlightTime.value
  }

  // Coupon
  if (couponCode.value && couponDiscount.value > 0) {
    data.coupon_code = couponCode.value
  }

  submitting.value = true
  try {
    const res = await createTransferOrder(data)
    pendingOrderNo.value = res.data.order_no
    pendingAmount.value = res.data.total_price

    if (form.payment_method === 'wechat' || form.payment_method === 'alipay') {
      showPaymentPopup.value = true
    } else {
      goToResult()
    }
  } catch (e) {
    showToast(e.message)
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
      type: 'transfer'
    }
  })
}

function onPaymentConfirmed() {
  showToast(t('payment.paymentSubmitted'))
  goToResult()
}

function onPaymentCancel() {
  goToResult()
}

onMounted(async () => {
  try {
    const [vRes, pRes] = await Promise.all([
      getVehicles(),
      getTransferPrice()
    ])
    vehicles.value = vRes.data || []
    pricing.value = pRes.data

    if (vehicles.value.length) {
      form.vehicle_id = vehicles.value[0].id
    }
  } catch (e) {
    console.error(e)
  } finally {
    pageLoading.value = false
  }
})
</script>

<style scoped>
.required {
  color: #ee0a24;
  font-weight: bold;
}

.field-hint {
  font-size: 11px;
  color: #999;
  margin-left: 4px;
}

.field-label {
  font-size: 14px;
  color: #333;
  padding: 8px 0 6px;
  font-weight: 500;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pickup-title {
  color: #1a73e8;
}

.dropoff-title {
  color: #e6a23c;
}

.airport-radios {
  display: flex;
  gap: 12px;
  padding: 4px 0 12px;
}

.airport-label {
  font-size: 14px;
}

.airport-code {
  display: inline-block;
  background: #f0f0f0;
  color: #666;
  font-size: 11px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 3px;
  margin-left: 2px;
  font-family: monospace;
}

.route-display {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8f7f5;
  border-radius: 10px;
  padding: 12px;
  margin-top: 12px;
}

.route-point {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #333;
  flex: 1;
  min-width: 0;
}

.route-point span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.route-arrow {
  font-size: 18px;
  color: #bbb;
  flex-shrink: 0;
}

.service-radios {
  gap: 12px;
}

.combo-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--accent);
  background: #fff7f0;
  padding: 6px 12px;
  border-radius: 6px;
}

.vehicle-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vehicle-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.vehicle-card.active {
  border-color: var(--primary);
  background: var(--primary-light);
}

.vehicle-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.vehicle-card.active .vehicle-icon {
  background: rgba(26, 115, 232, 0.1);
}

.vehicle-info {
  flex: 1;
}

.vehicle-name {
  font-size: 15px;
  font-weight: 600;
}

.vehicle-desc {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 2px;
}

.vehicle-price {
  font-size: 13px;
  color: var(--accent);
  font-weight: 500;
}

.booking-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
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
</style>
