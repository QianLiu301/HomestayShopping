<template>
  <van-dialog
    v-model:show="visible"
    :title="t('review.title')"
    :show-cancel-button="true"
    :show-confirm-button="false"
    :close-on-click-overlay="!submitting"
    @cancel="onClose"
  >
    <div class="review-dialog__body">
      <div class="review-dialog__row">
        <div class="review-dialog__label">{{ t('review.ratingLabel') }}</div>
        <van-rate
          v-model="rating"
          :size="36"
          color="#ffd21e"
          void-icon="star"
          void-color="#e0e0e0"
        />
        <div class="review-dialog__hint">{{ t('review.ratingHint') }}</div>
      </div>

      <div class="review-dialog__row">
        <div class="review-dialog__label">{{ t('review.commentLabel') }}</div>
        <textarea
          v-model="comment"
          class="review-dialog__textarea"
          :placeholder="t('review.commentPlaceholder')"
          rows="4"
          maxlength="1000"
        />
        <div class="review-dialog__counter">{{ comment.length }} / 1000</div>
      </div>

      <button
        type="button"
        class="review-dialog__submit"
        :disabled="submitting || rating < 1"
        @click="onSubmit"
      >
        {{ submitting ? '...' : t('review.submit') }}
      </button>
    </div>
  </van-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { submitTransferReview, submitTicketReview } from '../api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  orderType: { type: String, required: true },  // 'transfer' | 'ticket'
  orderId: { type: [Number, String], required: true },
})

const emit = defineEmits(['update:modelValue', 'success'])

const { t, locale } = useI18n()

const visible = ref(props.modelValue)
const rating = ref(0)
const comment = ref('')
const submitting = ref(false)

watch(() => props.modelValue, (v) => { visible.value = v })
watch(visible, (v) => {
  emit('update:modelValue', v)
  if (!v) {
    // 关闭时清理
    rating.value = 0
    comment.value = ''
  }
})

function onClose() {
  if (submitting.value) return
  visible.value = false
}

async function onSubmit() {
  if (rating.value < 1) {
    showToast(t('review.ratingHint'))
    return
  }
  if (submitting.value) return

  submitting.value = true
  try {
    const payload = {
      order_id: Number(props.orderId),
      rating: rating.value,
      comment: comment.value.trim(),
      lang: locale.value || 'zh',
    }
    const fn = props.orderType === 'transfer' ? submitTransferReview : submitTicketReview
    await fn(payload)
    showToast(t('review.submitSuccess'))
    emit('success')
    visible.value = false
  } catch (e) {
    showToast(e?.message || 'submit failed')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.review-dialog__body {
  padding: 16px 20px 20px;
}

.review-dialog__row {
  margin-bottom: 18px;
}

.review-dialog__label {
  font-size: 14px;
  font-weight: 600;
  color: #4a3728;
  margin-bottom: 10px;
}

.review-dialog__hint {
  margin-top: 6px;
  font-size: 12px;
  color: #8d7b67;
}

.review-dialog__textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(200, 169, 126, 0.35);
  border-radius: 8px;
  background: #fffdf9;
  font-size: 14px;
  color: #3b2b1f;
  font-family: inherit;
  line-height: 1.55;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
}

.review-dialog__textarea:focus {
  outline: none;
  border-color: #c69a62;
  box-shadow: 0 0 0 3px rgba(198, 154, 98, 0.12);
}

.review-dialog__counter {
  margin-top: 4px;
  text-align: right;
  font-size: 11px;
  color: #b8a995;
}

.review-dialog__submit {
  width: 100%;
  padding: 12px 0;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #c69a62, #ae7b43);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.review-dialog__submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
