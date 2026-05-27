<template>
  <div class="page-container ticket-checkout-page">
    <van-nav-bar :title="t('tickets.checkoutTitle')" left-arrow @click-left="$router.back()">
      <template #right>
        <LangSwitch />
      </template>
    </van-nav-bar>

    <div v-if="pageLoading" class="loading-wrap">
      <van-loading size="24" />
    </div>

    <template v-else>
      <div class="card checkout-hero-card">
        <div class="checkout-hero__title">{{ t('tickets.checkoutTitle') }}</div>
        <div class="checkout-hero__content">
          <div class="checkout-hero__media">
            <img v-if="attractionImage" :src="resolveUrl(attractionImage)" class="checkout-hero__image" />
            <div v-else class="checkout-hero__image checkout-hero__image--placeholder">{{ attraction?.name?.charAt(0) || 'T' }}</div>
          </div>
          <div class="checkout-hero__info">
            <div class="checkout-hero__date">{{ selectedVisitDateText }}</div>
            <div class="checkout-hero__name">{{ attraction?.name || '-' }}</div>
            <div class="checkout-hero__sub">{{ summaryPackageText }}</div>
            <div class="checkout-hero__note">{{ bookingWindowText }}</div>
            <div class="selected-package-list selected-package-list--compact">
              <div v-for="item in selectedPackages" :key="item.id" class="selected-package-item selected-package-item--compact">
                <div>
                  <div class="selected-package-name">{{ item.package_name }}</div>
                  <div class="selected-package-type">{{ ticketTypeLabel(item.ticket_type) }}</div>
                </div>
                <div class="selected-package-right">
                  <van-stepper v-model="item.quantity" min="0" integer @change="onPackageQuantityChange(item.id, $event)" />
                  <div class="selected-package-price">¥{{ getPackagePriceForDate(item, form.visit_date) }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="checkout-hero__price-wrap">
            <div class="checkout-hero__unit">{{ locale === 'en' ? 'Unit / Total' : '合计' }}</div>
            <div class="checkout-hero__price">¥{{ totalSelectedDayPrice }}</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">{{ t('tickets.contactInfo') }}</div>
        <div class="contact-soft-tip">{{ t('tickets.phoneOrEmailRequired') }}</div>
        <van-field v-model="form.contact_name" :label="t('tickets.contactName')" :placeholder="t('tickets.contactNamePlaceholder')" required />
        <van-field v-model="form.contact_phone" :label="t('tickets.contactPhone')" :placeholder="t('tickets.contactPhonePlaceholder')" type="tel" />
        <van-field v-model="form.contact_email" :label="t('tickets.contactEmail')" :placeholder="t('tickets.contactEmailPlaceholder')" type="email" />
        <van-field v-model="form.booking_no" :label="t('tickets.bookingNo')" :placeholder="t('tickets.bookingNoPlaceholder')" required />
        <van-field v-model="form.remark" :label="t('tickets.remark')" :placeholder="t('tickets.remarkPlaceholder')" type="textarea" rows="2" autosize />
      </div>

      <div class="card">
        <div class="card-title">{{ t('tickets.travelerInfo') }}</div>
        <div class="traveler-tip">{{ travelerTip }}</div>
        <div v-for="(traveler, index) in travelers" :key="index" class="traveler-card">
          <div class="traveler-card__title">{{ t('tickets.traveler') }} {{ index + 1 }}</div>
          <van-field v-model="traveler.full_name" :label="t('tickets.fullName')" :placeholder="t('tickets.fullNamePlaceholder')" :required="needRealName" />
          <van-field :label="t('tickets.travelerType')">
            <template #input>
              <van-radio-group v-model="traveler.traveler_type" direction="horizontal">
                <van-radio name="adult">{{ t('tickets.adult') }}</van-radio>
                <van-radio name="child">{{ t('tickets.child') }}</van-radio>
                <van-radio name="senior">{{ t('tickets.senior') }}</van-radio>
              </van-radio-group>
            </template>
          </van-field>
          <van-field v-model="traveler.nationality" :label="t('tickets.nationality')" :placeholder="t('tickets.nationalityPlaceholder')" />
          <van-field :label="t('tickets.documentType')">
            <template #input>
              <van-radio-group v-model="traveler.document_type" direction="horizontal">
                <van-radio name="passport">{{ t('tickets.passport') }}</van-radio>
                <van-radio name="id_card">{{ t('tickets.idCard') }}</van-radio>
              </van-radio-group>
            </template>
          </van-field>
          <van-field v-model="traveler.document_no" :label="t('tickets.documentNo')" :placeholder="t('tickets.documentNoPlaceholder')" :required="needPassport" />
          <van-field
            v-model="traveler.date_of_birth"
            :label="t('tickets.dateOfBirth')"
            :placeholder="birthDatePlaceholder"
          />
          <van-field :label="t('tickets.gender')">
            <template #input>
              <van-radio-group v-model="traveler.gender" direction="horizontal">
                <van-radio name="male">{{ t('tickets.male') }}</van-radio>
                <van-radio name="female">{{ t('tickets.female') }}</van-radio>
              </van-radio-group>
            </template>
          </van-field>
        </div>
      </div>

      <div v-if="selectedTransport" class="card">
        <div class="card-title">{{ t('tickets.transferInfo') }}</div>
        <div class="transfer-soft-tip">{{ t('tickets.transferBookingTip') }}</div>
        <div class="price-row">
          <span>{{ selectedTransport.vehicle?.name || selectedTransport.vehicle?.name_zh || '-' }}</span>
          <span>{{ transferServiceLabel(selectedTransport.service_type) }}</span>
        </div>
        <div class="price-row">
          <span>{{ t('tickets.transferPrice') }}</span>
          <span>¥{{ selectedTransport.price }}</span>
        </div>
        <van-field
          v-model="form.transfer_pickup_time"
          :label="primaryTransferTimeLabel"
          :placeholder="t('tickets.transferTimePlaceholder')"
          type="datetime-local"
          required
        />
        <van-field
          v-if="showTransferReturnTime"
          v-model="form.transfer_return_time"
          :label="t('tickets.transferReturnTime')"
          :placeholder="t('tickets.transferTimePlaceholder')"
          type="datetime-local"
          required
        />
        <van-field
          v-model="form.transfer_user_note"
          :label="t('tickets.transferUserNote')"
          :placeholder="t('tickets.transferUserNotePlaceholder')"
          type="textarea"
          rows="2"
          autosize
        />
      </div>

      <div class="card">
        <div class="card-title">{{ t('tickets.priceSummary') }}</div>
        <div class="price-row">
          <span>{{ t('tickets.ticketSubtotal') }}</span>
          <span>¥{{ ticketSubtotal }}</span>
        </div>
        <div v-if="selectedTransport" class="price-row">
          <span>{{ t('tickets.transferPrice') }}</span>
          <span>¥{{ selectedTransport.price }}</span>
        </div>
        <div class="price-row total-row">
          <span>{{ t('tickets.totalPrice') }}</span>
          <span>¥{{ totalPrice }}</span>
        </div>
      </div>

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

      <div v-if="errorMsg" class="error-banner">
        <van-icon name="warning-o" size="18" />
        <span>{{ errorMsg }}</span>
      </div>

      <div class="submit-wrap">
        <van-button round block type="primary" size="large" :loading="submitting" @click="onSubmit">
          {{ t('tickets.submitOrder') }} ¥{{ totalPrice }}
        </van-button>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getTicketAttraction, getTicketTransportOptions, createTicketOrder } from '../api/tickets'
import { resolveUrl } from '../api'
import LangSwitch from '../components/LangSwitch.vue'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

const pageLoading = ref(true)
const submitting = ref(false)
const errorMsg = ref('')
const attraction = ref(null)
const transportOptions = ref([])
const selectedPackage = ref(null)
const selectedPackages = ref([])
const selectedTransport = ref(null)
const agreeTerms = ref(false)

const form = reactive({
  visit_date: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  booking_no: '',
  remark: '',
  transfer_pickup_time: '',
  transfer_return_time: '',
  transfer_user_note: ''
})

const travelers = ref([])

const now = new Date()
const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
const bookingEndDate = new Date(today)
bookingEndDate.setMonth(bookingEndDate.getMonth() + 1)

const weekDaysMap = {
  zh: ['日', '一', '二', '三', '四', '五', '六'],
  en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  ru: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
  es: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa']
}
const weekDays = computed(() => weekDaysMap[locale.value] || weekDaysMap.zh)
const currentMonth = ref(getMonthStart(new Date()))
const currentMonthLabel = computed(() => {
  const y = currentMonth.value.getFullYear()
  const m = currentMonth.value.getMonth() + 1
  return locale.value === 'en' ? `${y}-${String(m).padStart(2, '0')}` : `${y}年${m}月`
})
const minBookingMonth = computed(() => getMonthStart(today))
const maxBookingMonth = computed(() => getMonthStart(bookingEndDate))
const canGoPrevMonth = computed(() => currentMonth.value.getTime() > minBookingMonth.value.getTime())
const canGoNextMonth = computed(() => currentMonth.value.getTime() < maxBookingMonth.value.getTime())

const needRealName = computed(() => !!attraction.value?.real_name_required)
const needPassport = computed(() => !!attraction.value?.passport_required)

const travelerTip = computed(() => {
  if (needPassport.value) return t('tickets.passportTravelerTip')
  if (needRealName.value) return t('tickets.realNameTravelerTip')
  return t('tickets.optionalTravelerTip')
})

const ruleMap = computed(() => getRuleMapForPackage(selectedPackage.value))

const bookingWindowText = computed(() => {
  if (locale.value === 'en') return `Bookable: ${formatDate(today)} ~ ${formatDate(bookingEndDate)}`
  return `可预订日期：${formatDate(today)} - ${formatDate(bookingEndDate)}`
})
const selectedVisitDateText = computed(() => formatDisplayDate(form.visit_date))
const attractionImage = computed(() => attraction.value?.cover_image || attraction.value?.images?.[0] || '')
const birthDatePlaceholder = computed(() => locale.value === 'en' ? 'DD/MM/YYYY' : 'DD/MM/YYYY')
const summaryPackageText = computed(() => {
  if (!selectedPackages.value.length) return t('tickets.selectPackageFirst')
  return selectedPackages.value.map(item => `${item.package_name} x${item.quantity}`).join(' / ')
})
const totalSelectedQuantity = computed(() => selectedPackages.value.reduce((sum, item) => sum + Number(item.quantity || 0), 0))
const totalSelectedDayPrice = computed(() => ticketSubtotal.value)

const ticketSubtotal = computed(() => {
  return selectedPackages.value.reduce((sum, item) => {
    return sum + (Number(getPackagePriceForDate(item, form.visit_date)) * Number(item.quantity || 0))
  }, 0).toFixed(2)
})

const totalPrice = computed(() => {
  const transportPrice = Number(selectedTransport.value?.price || 0)
  return (Number(ticketSubtotal.value) + transportPrice).toFixed(2)
})
const showTransferReturnTime = computed(() => selectedTransport.value?.service_type === 'round_trip')
const primaryTransferTimeLabel = computed(() => selectedTransport.value?.service_type === 'dropoff_only'
  ? t('tickets.transferReturnTime')
  : t('tickets.transferPickupTime'))

watch(totalSelectedQuantity, value => {
  const count = Number(value || 0)
  while (travelers.value.length < count) {
    travelers.value.push(createEmptyTraveler())
  }
  if (travelers.value.length > count) {
    travelers.value.splice(count)
  }
})

function createEmptyTraveler() {
  return {
    traveler_type: 'adult',
    full_name: '',
    nationality: '',
    document_type: 'passport',
    document_no: '',
    date_of_birth: '',
    gender: 'male'
  }
}

function getMonthStart(date) {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function formatDisplayDate(isoDate) {
  if (!isoDate) return t('tickets.visitDatePlaceholder')
  const date = new Date(`${isoDate}T00:00:00`)
  const day = date.getDay()

  if (locale.value === 'zh') return `${isoDate} 星期${weekDaysMap.zh[day]}`
  return `${isoDate} ${weekDays.value[day]}`
}

function isDateWithinBookingWindow(date) {
  return date >= today && date <= bookingEndDate
}

function clampMonth(date) {
  const monthStart = getMonthStart(date)
  if (monthStart < minBookingMonth.value) return new Date(minBookingMonth.value)
  if (monthStart > maxBookingMonth.value) return new Date(maxBookingMonth.value)
  return monthStart
}

function getRuleMapForPackage(pkg) {
  const map = new Map()
  if (Array.isArray(pkg?.date_rules)) {
    pkg.date_rules.forEach(rule => {
      if (rule?.date) map.set(rule.date, rule)
    })
  }
  return map
}

function getPackagePriceForDate(pkg, isoDate) {
  if (!pkg) return 0
  const currentRuleMap = getRuleMapForPackage(pkg)
  if (isoDate && currentRuleMap.has(isoDate)) {
    const rule = currentRuleMap.get(isoDate)
    if (rule?.enabled === false) return 0
    return Number((rule.price ?? pkg.sale_price) || 0)
  }
  return Number(pkg.sale_price || 0)
}

function getSelectedDayPrice() {
  return selectedPackages.value.reduce((sum, item) => {
    return sum + (Number(getPackagePriceForDate(item, form.visit_date)) * Number(item.quantity || 0))
  }, 0)
}

function ticketTypeLabel(type) {
  const map = {
    adult: t('tickets.adultTicket'),
    child: t('tickets.childTicket'),
    senior: t('tickets.seniorTicket'),
    family: t('tickets.familyTicket'),
    combo: t('tickets.comboTicket')
  }
  return map[type] || type || '-'
}

function ensureSelectedVisitDateValid() {
  if (form.visit_date && !isSelectableDate(form.visit_date)) {
    form.visit_date = ''
  }
  if (!form.visit_date) {
    form.visit_date = getFirstSelectableDate()
  }
  if (form.visit_date) {
    currentMonth.value = clampMonth(new Date(`${form.visit_date}T00:00:00`))
  }
}

function onPackageQuantityChange(packageId, value) {
  selectedPackages.value = selectedPackages.value
    .map(item => item.id === packageId ? { ...item, quantity: Number(value || 0) } : item)
    .filter(item => Number(item.quantity || 0) > 0)

  if (!selectedPackages.value.length && selectedPackage.value) {
    selectedPackages.value = [{ ...selectedPackage.value, quantity: 1 }]
  }

  const current = selectedPackages.value.find(item => item.id === packageId)
  if (current) {
    selectedPackage.value = current
  } else if (selectedPackages.value.length) {
    selectedPackage.value = selectedPackages.value[0]
  }

  ensureSelectedVisitDateValid()
}

function isSelectableDateForPackage(pkg, isoDate) {
  if (!pkg) return false
  const current = new Date(`${isoDate}T00:00:00`)
  if (!isDateWithinBookingWindow(current)) return false

  const currentRuleMap = getRuleMapForPackage(pkg)
  const rule = currentRuleMap.get(isoDate)
  if (rule) {
    return rule.enabled !== false
  }
  if (!currentRuleMap.size && Array.isArray(pkg?.available_days) && pkg.available_days.length) {
    return pkg.available_days.includes(isoDate)
  }
  return true
}

function isSelectableDate(isoDate) {
  if (!selectedPackages.value.length) return false
  return selectedPackages.value.every(pkg => isSelectableDateForPackage(pkg, isoDate))
}

function getCalendarPriceForDate(isoDate) {
  if (!selectedPackages.value.length) return null
  return selectedPackages.value.reduce((sum, item) => {
    return sum + (Number(getPackagePriceForDate(item, isoDate)) * Number(item.quantity || 0))
  }, 0)
}

function getFirstSelectableDate() {
  const cursor = new Date(today)
  while (cursor <= bookingEndDate) {
    const iso = formatDate(cursor)
    if (isSelectableDate(iso)) return iso
    cursor.setDate(cursor.getDate() + 1)
  }
  return ''
}

const calendarCells = computed(() => {
  const result = []
  const viewDate = currentMonth.value
  const firstDay = new Date(viewDate.getFullYear(), viewDate.getMonth(), 1)
  const firstWeekDay = firstDay.getDay()
  const daysInMonth = new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 0).getDate()
  const todayIso = formatDate(new Date())

  for (let i = 0; i < firstWeekDay; i += 1) {
    result.push({ key: `empty-${i}`, date: null })
  }

  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(viewDate.getFullYear(), viewDate.getMonth(), day)
    const iso = formatDate(date)
    const selectable = isSelectableDate(iso)
    const price = selectable ? getCalendarPriceForDate(iso) : null
    result.push({
      key: iso,
      date,
      iso,
      dayNumber: day,
      selectable,
      rule: ruleMap.value.get(iso),
      isToday: iso === todayIso,
      priceText: selectable && price !== null && price !== undefined ? `¥${price}` : ''
    })
  }

  while (result.length % 7 !== 0) {
    result.push({ key: `tail-${result.length}`, date: null })
  }

  return result
})

function changeMonth(step) {
  currentMonth.value = clampMonth(new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + step, 1))
}

function selectVisitDate(day) {
  if (!day?.iso || !day.selectable) return
  form.visit_date = day.iso
  currentMonth.value = clampMonth(day.date)
}

function isValidBirthDateInput(value) {
  if (!value) return true
  return /^\d{2}\/\d{2}\/\d{4}$/.test(value.trim())
}

function transferServiceLabel(type) {
  const map = {
    pickup_only: t('tickets.pickupOnly'),
    dropoff_only: t('tickets.dropoffOnly'),
    round_trip: t('tickets.roundTrip'),
    charter: t('tickets.charter')
  }
  return map[type] || type || '-'
}

function isValidTransferTimeInput(value) {
  if (!value) return false
  return /^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}$/.test(String(value).trim())
}

function formatTransferTimeForSubmit(value) {
  if (!value) return ''
  return String(value).trim().replace('T', ' ')
}

function validate() {
  if (!selectedPackages.value.length || totalSelectedQuantity.value < 1) return t('tickets.selectPackageFirst')
  if (!form.visit_date) return t('tickets.visitDateRequired')
  if (!form.contact_name.trim()) return t('tickets.contactNameRequired')
  if (!form.contact_phone.trim() && !form.contact_email.trim()) return t('tickets.phoneOrEmailRequired')
  if (!form.booking_no.trim()) return t('tickets.bookingNoRequired')
  if (selectedTransport.value) {
    if (!form.transfer_pickup_time) return t('tickets.transferPickupTimeRequired')
    if (!isValidTransferTimeInput(form.transfer_pickup_time)) return t('tickets.transferTimeFormatError')
    if (showTransferReturnTime.value) {
      if (!form.transfer_return_time) return t('tickets.transferReturnTimeRequired')
      if (!isValidTransferTimeInput(form.transfer_return_time)) return t('tickets.transferTimeFormatError')
    }
  }
  if (!agreeTerms.value) return t('transfer.agreeRequired')

  if (needRealName.value) {
    for (const traveler of travelers.value) {
      if (!traveler.full_name.trim()) return t('tickets.fullNameRequired')
      if (needPassport.value && !traveler.document_no.trim()) return t('tickets.documentNoRequired')
      if (traveler.date_of_birth && !isValidBirthDateInput(traveler.date_of_birth)) return '出生日期格式错误，请使用 DD/MM/YYYY'
    }
  }
  return ''
}

async function loadData() {
  pageLoading.value = true
  try {
    const attractionId = route.query.attraction_id
    const packageId = Number(route.query.package_id)
    const packageSelections = route.query.package_selections ? JSON.parse(String(route.query.package_selections)) : []
    const transportPriceId = route.query.transport_price_id ? Number(route.query.transport_price_id) : null

    if (!attractionId || (!packageId && !packageSelections.length)) {
      router.replace('/tickets')
      return
    }

    const [detailRes, transportRes] = await Promise.all([
      getTicketAttraction(attractionId),
      getTicketTransportOptions({ attraction_id: attractionId }).catch(() => ({ data: [] }))
    ])

    attraction.value = detailRes.data
    const allPackages = detailRes.data?.packages || []
    selectedPackage.value = allPackages.find(item => item.id === packageId) || allPackages[0] || null
    selectedPackages.value = packageSelections.length
      ? packageSelections
          .map(selection => {
            const pkg = allPackages.find(item => item.id === Number(selection.package_id))
            return pkg ? { ...pkg, quantity: Number(selection.quantity || 0) } : null
          })
          .filter(Boolean)
      : (selectedPackage.value ? [{ ...selectedPackage.value, quantity: 1 }] : [])
    transportOptions.value = transportRes.data || []
    selectedTransport.value = transportOptions.value.find(item => item.id === transportPriceId) || null
    form.visit_date = route.query.visit_date ? String(route.query.visit_date) : ''
    if (form.visit_date) currentMonth.value = clampMonth(new Date(`${form.visit_date}T00:00:00`))

    if (!selectedPackage.value && !selectedPackages.value.length) {
      showToast(t('common.noData'))
      router.replace(`/tickets/${attractionId}`)
      return
    }

    travelers.value = []
    if (!selectedPackages.value.length && selectedPackage.value) {
      selectedPackages.value = [{ ...selectedPackage.value, quantity: 1 }]
    }
    ensureSelectedVisitDateValid()
  } catch (error) {
    showToast(error.message || t('common.noData'))
  } finally {
    pageLoading.value = false
  }
}

async function onSubmit() {
  const msg = validate()
  if (msg) {
    errorMsg.value = msg
    return
  }

  errorMsg.value = ''
  submitting.value = true
  try {
    const payload = {
      attraction_id: attraction.value.id,
      visit_date: form.visit_date,
      lang: locale.value,
      contact_name: form.contact_name,
      contact_phone: form.contact_phone,
      contact_email: form.contact_email,
      booking_no: form.booking_no,
      remark: form.remark,
      need_transfer: !!selectedTransport.value,
      transport_price_id: selectedTransport.value?.id,
      transfer_pickup_time: selectedTransport.value ? formatTransferTimeForSubmit(form.transfer_pickup_time) : '',
      transfer_return_time: selectedTransport.value && showTransferReturnTime.value ? formatTransferTimeForSubmit(form.transfer_return_time) : '',
      transfer_user_note: form.transfer_user_note,
      packages: selectedPackages.value
        .filter(item => Number(item.quantity || 0) > 0)
        .map(item => ({
          package_id: item.id,
          quantity: Number(item.quantity || 0)
        })),
      travelers: travelers.value.map(item => ({
        traveler_type: item.traveler_type,
        full_name: item.full_name,
        nationality: item.nationality,
        document_type: item.document_type,
        document_no: item.document_no,
        date_of_birth: item.date_of_birth,
        gender: item.gender
      }))
    }

    const res = await createTicketOrder(payload)
    router.replace({
      path: '/ticket-order-result',
      query: {
        orderNo: res.data?.order_no || '',
        amount: res.data?.total_price || totalPrice.value,
        attractionName: attraction.value?.name || '',
        type: 'ticket'
      }
    })
  } catch (error) {
    errorMsg.value = error.message || t('common.noData')
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.ticket-checkout-page {
  padding-top: 0;
  padding-bottom: 28px;
}

.checkout-hero-card {
  padding: 16px 18px;
}

.checkout-hero__title {
  font-size: 22px;
  font-weight: 700;
  color: #3b2b1f;
  margin-bottom: 16px;
}

.checkout-hero__content {
  display: grid;
  grid-template-columns: 144px minmax(0, 1fr) 132px;
  gap: 18px;
  align-items: start;
}

.checkout-hero__media {
  width: 144px;
}

.checkout-hero__image {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: 14px;
  background: #f5f5f5;
}

.checkout-hero__image--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34px;
  color: rgba(0,0,0,0.18);
}

.checkout-hero__date {
  font-size: 22px;
  font-weight: 700;
  color: #2f261d;
}

.checkout-hero__name {
  margin-top: 12px;
  font-size: 16px;
  font-weight: 700;
  color: #2f261d;
  line-height: 1.5;
}

.checkout-hero__sub {
  margin-top: 10px;
  font-size: 13px;
  color: #6e5a42;
  line-height: 1.6;
}

.checkout-hero__note {
  margin-top: 10px;
  font-size: 12px;
  color: #8d7b67;
}

.checkout-hero__price-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.checkout-hero__unit {
  font-size: 12px;
  color: #8d7b67;
}

.checkout-hero__price {
  font-size: 24px;
  font-weight: 700;
  color: #ff6b00;
}

.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

.summary-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}

.summary-sub {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.selected-package-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
}

.selected-package-list--compact {
  margin-top: 14px;
}

.selected-package-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #efe4d4;
  border-radius: 12px;
  background: #fffdf9;
}

.selected-package-item--compact {
  padding: 10px 12px;
}

.selected-package-name {
  font-size: 14px;
  font-weight: 700;
  color: #3b2b1f;
}

.selected-package-type {
  margin-top: 4px;
  font-size: 12px;
  color: #8d7b67;
}

.selected-package-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.selected-package-price {
  font-size: 16px;
  font-weight: 700;
  color: #b98745;
}

.summary-price {
  margin-top: 10px;
  font-size: 24px;
  font-weight: 700;
  color: var(--accent);
}

.calendar-selected-head {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.calendar-selected-label {
  font-size: 12px;
  color: #8d7b67;
}

.calendar-selected-value {
  margin-top: 4px;
  font-size: 18px;
  font-weight: 700;
  color: #3b2b1f;
}

.calendar-month-switch {
  display: flex;
  align-items: center;
  gap: 10px;
}

.month-btn {
  width: 34px;
  height: 34px;
  border: 1px solid #eadfce;
  border-radius: 999px;
  background: #fff;
  color: #6e5a42;
  font-size: 20px;
}

.month-btn:disabled {
  cursor: not-allowed;
  opacity: 0.38;
}

.month-title {
  min-width: 64px;
  text-align: center;
  font-size: 18px;
  font-weight: 700;
  color: #3b2b1f;
}

.booking-window-tip {
  margin-bottom: 12px;
  font-size: 12px;
  color: #8d7b67;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  margin-bottom: 10px;
  color: #666;
  font-size: 13px;
  text-align: center;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}

.calendar-day {
  position: relative;
  min-height: 72px;
  border: 1px solid #efe4d4;
  border-radius: 16px;
  background: #fff;
  padding: 8px 4px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.calendar-day.empty {
  visibility: hidden;
}

.calendar-day.disabled {
  opacity: 0.36;
  background: #faf7f2;
}

.calendar-day.selected {
  border-color: #2e2a24;
  box-shadow: inset 0 0 0 1px #2e2a24;
}

.calendar-day.today .day-number {
  color: #c69a62;
}

.day-tag {
  position: absolute;
  top: 6px;
  left: 6px;
  font-size: 10px;
  color: #9b8a73;
}

.day-number {
  font-size: 16px;
  font-weight: 700;
  color: #1f1f1f;
}

.day-price {
  margin-top: 6px;
  font-size: 11px;
  color: #8d7b67;
}

.traveler-tip {
  margin-bottom: 12px;
  font-size: 12px;
  color: #8d7b67;
  line-height: 1.6;
}

.traveler-card {
  padding: 12px;
  border: 1px solid #f0e7dc;
  border-radius: 12px;
  background: #fffdf9;
}

.traveler-card + .traveler-card {
  margin-top: 12px;
}

.traveler-card__title {
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #3b2b1f;
}

.price-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.total-row {
  border-top: 1px solid var(--border);
  margin-top: 4px;
  padding-top: 12px;
  font-weight: 700;
  color: var(--text);
}

  .contact-soft-tip {
    margin-bottom: 10px;
    font-size: 12px;
    color: #8d7b67;
  }

  .transfer-soft-tip {
    margin-bottom: 10px;
    font-size: 12px;
    line-height: 1.6;
    color: #8d7b67;
  }

.agree-card {
  padding: 12px 16px;
}

.agree-text {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.agree-link {
  color: var(--accent);
  text-decoration: underline;
}

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
}

.submit-wrap {
  padding: 16px;
}

/* ============ 移动端：横向 3 列 → 竖向堆叠 ============ */
@media (max-width: 768px) {
  .checkout-hero-card {
    padding: 14px;
  }

  .checkout-hero__title {
    font-size: 18px;
    margin-bottom: 12px;
  }

  /* 头部布局改为两行：上面 [小图 + 日期/名称/描述]，下面 [合计 / 价格] */
  .checkout-hero__content {
    grid-template-columns: 92px minmax(0, 1fr);
    grid-template-areas:
      "media info"
      "price price";
    gap: 12px;
    align-items: start;
  }

  .checkout-hero__media {
    grid-area: media;
    width: 92px;
  }

  .checkout-hero__image {
    border-radius: 10px;
  }

  .checkout-hero__info {
    grid-area: info;
    min-width: 0;
  }

  .checkout-hero__date {
    font-size: 16px;
  }

  .checkout-hero__name {
    margin-top: 6px;
    font-size: 14px;
    line-height: 1.45;
  }

  .checkout-hero__sub,
  .checkout-hero__note {
    margin-top: 6px;
    font-size: 12px;
    line-height: 1.5;
  }

  /* 合计/价格行：横排在内容下方 */
  .checkout-hero__price-wrap {
    grid-area: price;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid rgba(201, 169, 126, 0.18);
  }

  .checkout-hero__unit {
    font-size: 13px;
    font-weight: 600;
    color: #4a3728;
  }

  .checkout-hero__price {
    font-size: 22px;
  }

  /* 票种数量调整区在移动端也更紧凑 */
  .selected-package-list--compact {
    margin-top: 10px;
  }
}
</style>
