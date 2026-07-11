<template>
  <div class="checkin-page">
    <van-nav-bar :title="L.title" left-arrow @click-left="$router.back()" />

    <!-- 语言切换 -->
    <div class="lang-bar">
      <button
        v-for="l in langs"
        :key="l.value"
        type="button"
        class="lang-chip"
        :class="{ active: lang === l.value }"
        @click="lang = l.value"
      >{{ l.label }}</button>
    </div>

    <!-- 登记须知弹窗 -->
    <van-popup v-model:show="showNotice" round :close-on-click-overlay="false" class="notice-popup">
      <div class="notice-box">
        <div class="notice-langs">
          <button
            v-for="l in langs"
            :key="l.value"
            type="button"
            class="lang-chip lang-chip--sm"
            :class="{ active: lang === l.value }"
            @click="lang = l.value"
          >{{ l.label }}</button>
        </div>
        <h2 class="notice-title">{{ L.noticeTitle }}</h2>
        <div class="notice-body">{{ L.noticeBody }}</div>
        <label class="notice-agree">
          <van-checkbox v-model="agreed" shape="square" icon-size="18px" />
          <span>{{ L.agreeLabel }}</span>
        </label>
        <button type="button" class="notice-btn" :disabled="!agreed" @click="showNotice = false">
          {{ L.continueBtn }}
        </button>
      </div>
    </van-popup>

    <!-- 登记成功 -->
    <div v-if="submitted" class="success-box">
      <div class="success-icon">✅</div>
      <h2 class="success-title">{{ L.successTitle }}</h2>
      <p class="success-desc">{{ L.successDesc }}</p>
      <div class="success-links">
        <button type="button" class="success-link primary" @click="goAfterSuccess('/guides')">
          <span class="link-title">{{ L.linkGuides }}</span>
          <span class="link-sub">{{ L.linkGuidesSub }}</span>
        </button>
        <button type="button" class="success-link" @click="goAfterSuccess('/transfer')">
          <span class="link-title">{{ L.linkTransfer }}</span>
          <span class="link-sub">{{ L.linkTransferSub }}</span>
        </button>
        <button type="button" class="success-link" @click="goAfterSuccess('/tickets')">
          <span class="link-title">{{ L.linkTickets }}</span>
          <span class="link-sub">{{ L.linkTicketsSub }}</span>
        </button>
        <button type="button" class="success-link" @click="goAfterSuccess('/shop')">
          <span class="link-title">{{ L.linkShop }}</span>
          <span class="link-sub">{{ L.linkShopSub }}</span>
        </button>
      </div>
    </div>

    <!-- 登记表单 -->
    <div v-else class="form-body">
      <div class="card">
        <div class="card-title">{{ L.platformLabel }} <span class="required">*</span></div>
        <div class="platform-grid">
          <button
            v-for="p in platforms"
            :key="p.value"
            type="button"
            class="platform-btn"
            :class="{ active: form.platform === p.value }"
            @click="form.platform = p.value"
          >{{ p.label }}</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">{{ L.bookingNoLabel }} <span class="required">*</span></div>
        <input v-model.trim="form.booking_no" class="text-input" :placeholder="L.bookingNoPlaceholder" maxlength="100" />
      </div>

      <div class="card">
        <div class="card-title">{{ L.nameLabel }} <span class="required">*</span></div>
        <div class="name-grid">
          <div class="field">
            <label class="field-label">{{ L.surname }} *</label>
            <input v-model.trim="form.surname" class="text-input" :placeholder="L.surnamePlaceholder" maxlength="100" />
          </div>
          <div class="field">
            <label class="field-label">{{ L.givenName }} *</label>
            <input v-model.trim="form.given_name" class="text-input" :placeholder="L.givenNamePlaceholder" maxlength="100" />
          </div>
          <div class="field">
            <label class="field-label">{{ L.middleName }}</label>
            <input v-model.trim="form.middle_name" class="text-input" :placeholder="L.middleNamePlaceholder" maxlength="100" />
          </div>
        </div>
        <p class="field-hint">{{ L.nameHint }}</p>
      </div>

      <div class="card">
        <div class="card-title">{{ L.dobLabel }} <span class="required">*</span></div>
        <div class="dob-row">
          <div class="dob-field">
            <label class="field-label">{{ L.dobDay }}</label>
            <input
              v-model.trim="dob.day"
              class="text-input dob-input"
              type="text"
              inputmode="numeric"
              maxlength="2"
              placeholder="DD"
            />
          </div>
          <div class="dob-field dob-field--month">
            <label class="field-label">{{ L.dobMonth }}</label>
            <select v-model="dob.month" class="text-input dob-select">
              <option value="" disabled>{{ L.dobMonthPlaceholder }}</option>
              <option v-for="(m, idx) in L.months" :key="idx" :value="String(idx + 1).padStart(2, '0')">
                {{ String(idx + 1).padStart(2, '0') }} — {{ m }}
              </option>
            </select>
          </div>
          <div class="dob-field">
            <label class="field-label">{{ L.dobYear }}</label>
            <input
              v-model.trim="dob.year"
              class="text-input dob-input"
              type="text"
              inputmode="numeric"
              maxlength="4"
              placeholder="YYYY"
            />
          </div>
        </div>
        <p class="field-hint">{{ L.dobHint }}</p>
      </div>

      <div class="card">
        <div class="card-title">{{ L.passportLabel }} <span class="required">*</span></div>
        <div class="upload-row">
          <div class="sample-box">
            <img :src="'/checkin/passport-sample.png'" class="sample-img" @error="passportSampleMissing = true" v-show="!passportSampleMissing" />
            <div v-if="passportSampleMissing" class="sample-fallback">🛂<br />{{ L.sampleLabel }}</div>
            <div class="sample-caption">{{ L.sampleLabel }}</div>
          </div>
          <div class="upload-box" @click="pickFile('passport')">
            <template v-if="passportPreview">
              <img :src="passportPreview" class="upload-preview" />
              <div v-if="uploading.passport" class="upload-mask"><van-loading size="20px" color="#fff" /></div>
            </template>
            <template v-else>
              <span class="upload-plus">＋</span>
              <span class="upload-text">{{ L.uploadBtn }}</span>
            </template>
          </div>
        </div>
        <p class="privacy-note">🔒 {{ L.privacyNote }}</p>
      </div>

      <div class="card">
        <div class="card-title">{{ L.handheldLabel }} <span class="required">*</span></div>
        <div class="upload-row">
          <div class="sample-box">
            <img :src="'/checkin/handheld-sample.png'" class="sample-img" @error="handheldSampleMissing = true" v-show="!handheldSampleMissing" />
            <div v-if="handheldSampleMissing" class="sample-fallback">🤳<br />{{ L.sampleLabel }}</div>
            <div class="sample-caption">{{ L.sampleLabel }}</div>
          </div>
          <div class="upload-box" @click="pickFile('handheld')">
            <template v-if="handheldPreview">
              <img :src="handheldPreview" class="upload-preview" />
              <div v-if="uploading.handheld" class="upload-mask"><van-loading size="20px" color="#fff" /></div>
            </template>
            <template v-else>
              <span class="upload-plus">＋</span>
              <span class="upload-text">{{ L.uploadBtn }}</span>
            </template>
          </div>
        </div>
        <p class="privacy-note">🔒 {{ L.privacyNote }}</p>
      </div>

      <button type="button" class="submit-btn" :disabled="submitting" @click="onSubmit">
        <van-loading v-if="submitting" size="18px" color="#fff" style="margin-right:6px" />
        {{ L.submitBtn }}
      </button>

      <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileChange" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { showToast } from 'vant'
import { uploadGuestDoc, submitGuestRegistration } from '../api'

const lang = ref('en')
const langs = [
  { value: 'en', label: 'English' },
  { value: 'zh', label: '中文' },
  { value: 'ja', label: '日本語' },
  { value: 'ko', label: '한국어' },
  { value: 'ru', label: 'Русский' },
  { value: 'es', label: 'Español' },
]

const DICT = {
  en: {
    title: 'Guest Check-in Registration',
    noticeTitle: 'Registration Notice',
    noticeBody: 'According to Chinese law, foreign nationals staying in accommodation other than hotels must register their stay with the local Public Security Bureau within 24 hours of check-in. This is your legal obligation and an important record for future visa applications. Please fill in the information truthfully. False declarations, late declarations or failure to declare may be subject to penalties under the law.',
    agreeLabel: 'I have read and agree',
    continueBtn: 'Continue',
    platformLabel: 'Booking Platform',
    bookingNoLabel: 'Booking / Reservation Number',
    bookingNoPlaceholder: 'Enter your booking confirmation number',
    nameLabel: 'Name (as shown on passport)',
    surname: 'Surname',
    givenName: 'Given Name',
    middleName: 'Middle Name (optional)',
    surnamePlaceholder: 'e.g. SMITH',
    givenNamePlaceholder: 'e.g. JOHN',
    middleNamePlaceholder: 'Optional',
    nameHint: 'Please enter your name exactly as it appears on your passport.',
    dobLabel: 'Date of Birth',
    dobDay: 'Day',
    dobMonth: 'Month',
    dobYear: 'Year',
    dobMonthPlaceholder: 'Select month',
    dobHint: 'Day / Month / Year, as shown on your passport.',
    months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    passportLabel: 'Passport Photo Page',
    handheldLabel: 'Photo of You Holding Your Passport',
    sampleLabel: 'Example',
    uploadBtn: 'Upload Photo',
    privacyNote: 'This photo is used only for the homestay accommodation registration required by law. It will not be used for any other purpose.',
    submitBtn: 'Submit Registration',
    successTitle: 'Registration Successful!',
    successDesc: 'Thank you. We will file your accommodation registration with the authorities. Enjoy your stay in Shanghai!',
    linkGuides: 'Free Guides', linkGuidesSub: 'Shanghai Travel Guides / Free',
    linkTransfer: 'Book Transfer', linkTransferSub: 'Airport Transfer / On Time',
    linkTickets: 'Tickets & Experiences', linkTicketsSub: 'Attractions / Transfer',
    linkShop: 'Explore Shop', linkShopSub: 'Curated Gifts / Delivery',
    errPlatform: 'Please select your booking platform',
    errBookingNo: 'Please enter your booking number',
    errName: 'Please enter your surname and given name',
    errDob: 'Please enter a valid date of birth',
    errPassport: 'Please upload your passport photo page',
    errHandheld: 'Please upload the photo of you holding your passport',
    errUploadFail: 'Upload failed, please try again',
    errImageOnly: 'Please upload an image file',
  },
  zh: {
    title: '住宿登记',
    noticeTitle: '登记须知',
    noticeBody: '根据中国法律有关规定，境外人员在旅馆业以外场所入住后24小时内申报住宿登记是您应遵守的法律义务，也是您将来申请签证证件的重要依据。请如实填报相关信息。恶意虚假申报、超时申报或不申报均将被依法查处。',
    agreeLabel: '我已阅读并同意',
    continueBtn: '继续',
    platformLabel: '预订平台',
    bookingNoLabel: '平台预约单号',
    bookingNoPlaceholder: '请输入预订确认单号',
    nameLabel: '姓名（按护照填写）',
    surname: '姓',
    givenName: '名',
    middleName: '中间名（选填）',
    surnamePlaceholder: '如：ZHANG',
    givenNamePlaceholder: '如：SAN',
    middleNamePlaceholder: '选填',
    nameHint: '请严格按照护照上的拼写填写姓名。',
    dobLabel: '出生日期',
    dobDay: '日',
    dobMonth: '月',
    dobYear: '年',
    dobMonthPlaceholder: '选择月份',
    dobHint: '按 日 / 月 / 年 填写，与护照一致。',
    months: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
    passportLabel: '护照信息页照片',
    handheldLabel: '手持护照照片',
    sampleLabel: '示例',
    uploadBtn: '上传照片',
    privacyNote: '照片仅用于法律要求的民宿住宿登记申报，不作任何其他用途。',
    submitBtn: '提交登记',
    successTitle: '登记成功！',
    successDesc: '感谢配合，我们会为您完成住宿登记申报。祝您在上海旅途愉快！',
    linkGuides: '免费攻略', linkGuidesSub: '上海旅游攻略 / 免费',
    linkTransfer: '预约接送机', linkTransferSub: '机场接送 / 准时',
    linkTickets: '门票玩乐', linkTicketsSub: '景点门票 / 接送',
    linkShop: '逛逛商城', linkShopSub: '精选好物 / 送货上门',
    errPlatform: '请选择预订平台',
    errBookingNo: '请输入预约单号',
    errName: '请填写姓和名',
    errDob: '请填写正确的出生日期',
    errPassport: '请上传护照信息页照片',
    errHandheld: '请上传手持护照照片',
    errUploadFail: '上传失败，请重试',
    errImageOnly: '请上传图片文件',
  },
  ja: {
    title: '宿泊登録',
    noticeTitle: '登録に関するご案内',
    noticeBody: '中国の法律により、ホテル以外の場所に宿泊する外国人は、チェックイン後24時間以内に現地の公安機関へ宿泊登録を申告する法的義務があります。これは将来のビザ申請の重要な記録にもなります。情報は正確にご記入ください。虚偽申告・期限超過・未申告は法律により処罰される場合があります。',
    agreeLabel: '内容を読み、同意します',
    continueBtn: '続ける',
    platformLabel: '予約プラットフォーム',
    bookingNoLabel: '予約番号',
    bookingNoPlaceholder: '予約確認番号を入力してください',
    nameLabel: '氏名（パスポート記載通り）',
    surname: '姓',
    givenName: '名',
    middleName: 'ミドルネーム（任意）',
    surnamePlaceholder: '例：YAMADA',
    givenNamePlaceholder: '例：TARO',
    middleNamePlaceholder: '任意',
    nameHint: 'パスポートに記載されている通りに氏名をご記入ください。',
    dobLabel: '生年月日',
    dobDay: '日',
    dobMonth: '月',
    dobYear: '年',
    dobMonthPlaceholder: '月を選択',
    dobHint: '日 / 月 / 年 の順で、パスポート記載通りにご入力ください。',
    months: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
    passportLabel: 'パスポート写真ページ',
    handheldLabel: 'パスポートを持った本人の写真',
    sampleLabel: '見本',
    uploadBtn: '写真をアップロード',
    privacyNote: 'この写真は法律で義務付けられた民泊の宿泊登録のみに使用され、他の用途には一切使用されません。',
    submitBtn: '登録を送信',
    successTitle: '登録が完了しました！',
    successDesc: 'ご協力ありがとうございます。当方にて宿泊登録の申告を行います。上海でのご滞在をお楽しみください！',
    linkGuides: '無料ガイド', linkGuidesSub: '上海旅行ガイド / 無料',
    linkTransfer: '送迎を予約', linkTransferSub: '空港送迎 / 時間厳守',
    linkTickets: 'チケット・体験', linkTicketsSub: '観光チケット / 送迎',
    linkShop: 'ショップを見る', linkShopSub: '厳選ギフト / 配達',
    errPlatform: '予約プラットフォームを選択してください',
    errBookingNo: '予約番号を入力してください',
    errName: '姓と名を入力してください',
    errDob: '正しい生年月日を入力してください',
    errPassport: 'パスポート写真ページをアップロードしてください',
    errHandheld: 'パスポートを持った写真をアップロードしてください',
    errUploadFail: 'アップロードに失敗しました。もう一度お試しください',
    errImageOnly: '画像ファイルをアップロードしてください',
  },
  ko: {
    title: '숙박 등록',
    noticeTitle: '등록 안내',
    noticeBody: '중국 법률에 따라 호텔 이외의 장소에 숙박하는 외국인은 체크인 후 24시간 이내에 현지 공안 기관에 숙박 등록을 신고해야 할 법적 의무가 있습니다. 이는 향후 비자 신청의 중요한 기록이기도 합니다. 정보를 사실대로 기입해 주세요. 허위 신고, 기한 초과 또는 미신고 시 법에 따라 처벌될 수 있습니다.',
    agreeLabel: '내용을 읽고 동의합니다',
    continueBtn: '계속하기',
    platformLabel: '예약 플랫폼',
    bookingNoLabel: '예약 번호',
    bookingNoPlaceholder: '예약 확인 번호를 입력하세요',
    nameLabel: '이름 (여권 기재대로)',
    surname: '성',
    givenName: '이름',
    middleName: '중간 이름 (선택)',
    surnamePlaceholder: '예: KIM',
    givenNamePlaceholder: '예: MINSU',
    middleNamePlaceholder: '선택 사항',
    nameHint: '여권에 기재된 것과 동일하게 이름을 입력해 주세요.',
    dobLabel: '생년월일',
    dobDay: '일',
    dobMonth: '월',
    dobYear: '년',
    dobMonthPlaceholder: '월 선택',
    dobHint: '일 / 월 / 년 순서로 여권 기재대로 입력해 주세요.',
    months: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
    passportLabel: '여권 사진면',
    handheldLabel: '여권을 든 본인 사진',
    sampleLabel: '예시',
    uploadBtn: '사진 업로드',
    privacyNote: '이 사진은 법률상 요구되는 민박 숙박 등록 신고에만 사용되며, 다른 용도로는 일절 사용되지 않습니다.',
    submitBtn: '등록 제출',
    successTitle: '등록이 완료되었습니다!',
    successDesc: '협조해 주셔서 감사합니다. 저희가 숙박 등록 신고를 진행하겠습니다. 상하이에서 즐거운 여행 되세요!',
    linkGuides: '무료 가이드', linkGuidesSub: '상하이 여행 가이드 / 무료',
    linkTransfer: '픽업 예약', linkTransferSub: '공항 픽업 / 정시',
    linkTickets: '티켓 & 체험', linkTicketsSub: '관광지 티켓 / 픽업',
    linkShop: '쇼핑하기', linkShopSub: '엄선한 선물 / 배송',
    errPlatform: '예약 플랫폼을 선택해 주세요',
    errBookingNo: '예약 번호를 입력해 주세요',
    errName: '성과 이름을 입력해 주세요',
    errDob: '올바른 생년월일을 입력해 주세요',
    errPassport: '여권 사진면을 업로드해 주세요',
    errHandheld: '여권을 든 사진을 업로드해 주세요',
    errUploadFail: '업로드에 실패했습니다. 다시 시도해 주세요',
    errImageOnly: '이미지 파일을 업로드해 주세요',
  },
  ru: {
    title: 'Регистрация проживания',
    noticeTitle: 'Уведомление о регистрации',
    noticeBody: 'Согласно законодательству Китая, иностранные граждане, проживающие не в гостиницах, обязаны зарегистрировать своё проживание в местном отделении общественной безопасности в течение 24 часов после заселения. Это ваша юридическая обязанность и важная запись для будущих визовых заявлений. Пожалуйста, указывайте достоверную информацию. Ложные сведения, просрочка или отсутствие регистрации могут повлечь ответственность по закону.',
    agreeLabel: 'Я прочитал(а) и согласен(на)',
    continueBtn: 'Продолжить',
    platformLabel: 'Платформа бронирования',
    bookingNoLabel: 'Номер бронирования',
    bookingNoPlaceholder: 'Введите номер подтверждения бронирования',
    nameLabel: 'Имя (как в паспорте)',
    surname: 'Фамилия',
    givenName: 'Имя',
    middleName: 'Отчество / среднее имя (необязательно)',
    surnamePlaceholder: 'напр. IVANOV',
    givenNamePlaceholder: 'напр. IVAN',
    middleNamePlaceholder: 'Необязательно',
    nameHint: 'Пожалуйста, введите имя точно так, как оно указано в паспорте.',
    dobLabel: 'Дата рождения',
    dobDay: 'День',
    dobMonth: 'Месяц',
    dobYear: 'Год',
    dobMonthPlaceholder: 'Выберите месяц',
    dobHint: 'День / Месяц / Год, как в паспорте.',
    months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
    passportLabel: 'Страница паспорта с фото',
    handheldLabel: 'Фото с паспортом в руках',
    sampleLabel: 'Пример',
    uploadBtn: 'Загрузить фото',
    privacyNote: 'Фото используется только для обязательной по закону регистрации проживания и ни для каких других целей.',
    submitBtn: 'Отправить регистрацию',
    successTitle: 'Регистрация успешна!',
    successDesc: 'Спасибо! Мы подадим вашу регистрацию проживания в органы. Приятного пребывания в Шанхае!',
    linkGuides: 'Бесплатные гиды', linkGuidesSub: 'Путеводители по Шанхаю / Бесплатно',
    linkTransfer: 'Заказать трансфер', linkTransferSub: 'Трансфер из аэропорта / Вовремя',
    linkTickets: 'Билеты и впечатления', linkTicketsSub: 'Достопримечательности / Трансфер',
    linkShop: 'Магазин', linkShopSub: 'Подарки / Доставка',
    errPlatform: 'Выберите платформу бронирования',
    errBookingNo: 'Введите номер бронирования',
    errName: 'Введите фамилию и имя',
    errDob: 'Введите корректную дату рождения',
    errPassport: 'Загрузите страницу паспорта с фото',
    errHandheld: 'Загрузите фото с паспортом в руках',
    errUploadFail: 'Ошибка загрузки, попробуйте ещё раз',
    errImageOnly: 'Загрузите файл изображения',
  },
  es: {
    title: 'Registro de alojamiento',
    noticeTitle: 'Aviso de registro',
    noticeBody: 'Según la ley china, los extranjeros que se alojen en lugares distintos de hoteles deben registrar su estancia ante la oficina de seguridad pública local dentro de las 24 horas posteriores a su llegada. Es su obligación legal y un registro importante para futuras solicitudes de visado. Por favor, proporcione información veraz. Las declaraciones falsas, tardías o la falta de declaración pueden ser sancionadas por la ley.',
    agreeLabel: 'He leído y acepto',
    continueBtn: 'Continuar',
    platformLabel: 'Plataforma de reserva',
    bookingNoLabel: 'Número de reserva',
    bookingNoPlaceholder: 'Introduzca su número de confirmación',
    nameLabel: 'Nombre (como aparece en el pasaporte)',
    surname: 'Apellido',
    givenName: 'Nombre',
    middleName: 'Segundo nombre (opcional)',
    surnamePlaceholder: 'ej. GARCÍA',
    givenNamePlaceholder: 'ej. CARLOS',
    middleNamePlaceholder: 'Opcional',
    nameHint: 'Introduzca su nombre exactamente como aparece en su pasaporte.',
    dobLabel: 'Fecha de nacimiento',
    dobDay: 'Día',
    dobMonth: 'Mes',
    dobYear: 'Año',
    dobMonthPlaceholder: 'Seleccione el mes',
    dobHint: 'Día / Mes / Año, como en su pasaporte.',
    months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    passportLabel: 'Página de foto del pasaporte',
    handheldLabel: 'Foto sosteniendo su pasaporte',
    sampleLabel: 'Ejemplo',
    uploadBtn: 'Subir foto',
    privacyNote: 'Esta foto se usa únicamente para el registro de alojamiento exigido por la ley y para ningún otro fin.',
    submitBtn: 'Enviar registro',
    successTitle: '¡Registro exitoso!',
    successDesc: '¡Gracias! Presentaremos su registro de alojamiento ante las autoridades. ¡Disfrute su estancia en Shanghái!',
    linkGuides: 'Guías gratis', linkGuidesSub: 'Guías de viaje de Shanghai / Gratis',
    linkTransfer: 'Reservar traslado', linkTransferSub: 'Traslado al aeropuerto / Puntual',
    linkTickets: 'Entradas y experiencias', linkTicketsSub: 'Atracciones / Traslado',
    linkShop: 'Explorar tienda', linkShopSub: 'Regalos seleccionados / Entrega',
    errPlatform: 'Seleccione su plataforma de reserva',
    errBookingNo: 'Introduzca su número de reserva',
    errName: 'Introduzca su apellido y nombre',
    errDob: 'Introduzca una fecha de nacimiento válida',
    errPassport: 'Suba la página de foto de su pasaporte',
    errHandheld: 'Suba la foto sosteniendo su pasaporte',
    errUploadFail: 'Error al subir, inténtelo de nuevo',
    errImageOnly: 'Suba un archivo de imagen',
  },
}

const L = computed(() => DICT[lang.value])

const platforms = [
  { value: 'booking', label: 'Booking.com' },
  { value: 'trip', label: 'Trip.com' },
  { value: 'agoda', label: 'Agoda' },
  { value: 'expedia', label: 'Expedia' },
]

const showNotice = ref(true)
const agreed = ref(false)
const submitted = ref(false)
const submitting = ref(false)
const passportSampleMissing = ref(false)
const handheldSampleMissing = ref(false)

const dob = reactive({ day: '', month: '', year: '' })

function buildDob() {
  const d = parseInt(dob.day, 10)
  const m = parseInt(dob.month, 10)
  const y = parseInt(dob.year, 10)
  if (!d || !m || !y || String(dob.year).length !== 4) return null
  if (y < 1900 || y > new Date().getFullYear()) return null
  const date = new Date(y, m - 1, d)
  // 校验是真实日期（如 2月31日 会被 Date 自动进位，这里要拒绝）
  if (date.getFullYear() !== y || date.getMonth() !== m - 1 || date.getDate() !== d) return null
  if (date > new Date()) return null
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`
}

const form = reactive({
  platform: '',
  booking_no: '',
  surname: '',
  given_name: '',
  middle_name: '',
  date_of_birth: '',
  passport_image: '',
  handheld_image: '',
})

const passportPreview = ref('')
const handheldPreview = ref('')
const uploading = reactive({ passport: false, handheld: false })

const fileInput = ref(null)
let pickTarget = 'passport'

function pickFile(target) {
  pickTarget = target
  fileInput.value?.click()
}

async function onFileChange(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (!file.type.startsWith('image/')) {
    showToast(L.value.errImageOnly)
    return
  }
  const target = pickTarget
  const previewUrl = URL.createObjectURL(file)
  if (target === 'passport') passportPreview.value = previewUrl
  else handheldPreview.value = previewUrl

  uploading[target] = true
  try {
    const res = await uploadGuestDoc(file)
    const key = res.data?.key
    if (!key) throw new Error('no key')
    if (target === 'passport') form.passport_image = key
    else form.handheld_image = key
  } catch {
    showToast(L.value.errUploadFail)
    if (target === 'passport') { passportPreview.value = ''; form.passport_image = '' }
    else { handheldPreview.value = ''; form.handheld_image = '' }
  } finally {
    uploading[target] = false
  }
}

function goAfterSuccess(path) {
  // 把全站语言同步为登记页所选语言（全站已支持 en/zh/ja/ko/ru/es）
  localStorage.setItem('lang', lang.value)
  // 用 replace 替换掉登记页的历史记录，浏览器返回时回到进入登记页之前的页面（如首页）
  window.location.replace(path)
}

async function onSubmit() {
  if (!form.platform) return showToast(L.value.errPlatform)
  if (!form.booking_no) return showToast(L.value.errBookingNo)
  if (!form.surname || !form.given_name) return showToast(L.value.errName)
  form.date_of_birth = buildDob()
  if (!form.date_of_birth) return showToast(L.value.errDob)
  if (!form.passport_image) return showToast(L.value.errPassport)
  if (!form.handheld_image) return showToast(L.value.errHandheld)
  if (uploading.passport || uploading.handheld) return

  submitting.value = true
  try {
    await submitGuestRegistration({
      platform: form.platform,
      booking_no: form.booking_no,
      surname: form.surname,
      given_name: form.given_name,
      middle_name: form.middle_name || undefined,
      date_of_birth: form.date_of_birth,
      passport_image: form.passport_image,
      handheld_image: form.handheld_image,
      lang: lang.value,
    })
    submitted.value = true
    window.scrollTo({ top: 0 })
  } catch (err) {
    showToast(err.message || L.value.errUploadFail)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.checkin-page {
  min-height: 100vh;
  background: var(--bg, #faf6ef);
  padding-bottom: 40px;
}

.lang-bar {
  display: flex;
  gap: 8px;
  padding: 12px 16px 4px;
  justify-content: center;
  flex-wrap: wrap;
}

.lang-chip {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid rgba(200, 169, 126, 0.4);
  background: #fff;
  color: #4a3728;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.lang-chip.active {
  color: #fff;
  border-color: var(--accent, #c8a97e);
  background: linear-gradient(135deg, #c69a62, #ae7b43);
}

.notice-popup {
  width: 88%;
  max-width: 480px;
}

.notice-box {
  padding: 20px;
}

.notice-langs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 14px;
}

.lang-chip--sm {
  padding: 4px 10px;
  font-size: 12px;
}

.notice-title {
  text-align: center;
  font-size: 19px;
  font-weight: 700;
  color: var(--text, #3b2b1f);
  margin: 0 0 16px;
}

.notice-body {
  background: #f7f3ec;
  border-radius: 10px;
  padding: 14px;
  font-size: 13.5px;
  line-height: 1.8;
  color: #4a3f34;
  max-height: 45vh;
  overflow-y: auto;
}

.notice-agree {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 16px 0;
  font-size: 14px;
  color: var(--text, #3b2b1f);
  cursor: pointer;
}

.notice-btn {
  width: 100%;
  padding: 12px 0;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #c69a62, #ae7b43);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}
.notice-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.form-body {
  padding: 12px 16px;
  max-width: 640px;
  margin: 0 auto;
}

.card {
  background: #fff;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 14px;
}

.card-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text, #3b2b1f);
  margin-bottom: 12px;
}

.required { color: #e15b5b; }

.platform-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.platform-btn {
  padding: 12px 0;
  border-radius: 10px;
  border: 1.5px solid #e8e0d3;
  background: #fdfbf7;
  color: #4a3728;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.platform-btn.active {
  border-color: var(--accent, #c8a97e);
  background: #fdf3e3;
  color: #8a5a23;
}

.text-input {
  width: 100%;
  padding: 11px 12px;
  border-radius: 10px;
  border: 1.5px solid #e8e0d3;
  background: #fdfbf7;
  font-size: 14px;
  color: var(--text, #3b2b1f);
  box-sizing: border-box;
}
.text-input:focus {
  outline: none;
  border-color: var(--accent, #c8a97e);
}

.name-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-label {
  display: block;
  font-size: 13px;
  color: #7d6e5c;
  margin-bottom: 5px;
  font-weight: 600;
}

.field-hint {
  margin: 10px 0 0;
  font-size: 12px;
  color: #9b8d7b;
}

.dob-row {
  display: flex;
  gap: 10px;
}

.dob-field {
  flex: 1;
}

.dob-field--month {
  flex: 1.6;
}

.dob-input {
  text-align: center;
}

.dob-select {
  appearance: auto;
  -webkit-appearance: auto;
  height: 42px;
}

.upload-row {
  display: flex;
  gap: 12px;
}

.sample-box {
  flex: 1;
  border: 1.5px dashed #d8cdbd;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  min-height: 110px;
  background: #fdfbf7;
}

.sample-img {
  width: 100%;
  height: 110px;
  object-fit: contain;
  display: block;
}

.sample-fallback {
  height: 110px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  color: #b9a689;
  text-align: center;
  line-height: 1.4;
}
.sample-fallback br + * { font-size: 12px; }

.sample-caption {
  position: absolute;
  top: 6px;
  left: 6px;
  padding: 1px 8px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 11px;
}

.upload-box {
  flex: 1;
  min-height: 110px;
  border: 1.5px dashed var(--accent, #c8a97e);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  background: #fdf6ea;
  position: relative;
  overflow: hidden;
}

.upload-plus {
  font-size: 26px;
  color: var(--accent, #c8a97e);
  line-height: 1;
}

.upload-text {
  font-size: 12px;
  color: #8a6f4d;
  font-weight: 600;
}

.upload-preview {
  width: 100%;
  height: 110px;
  object-fit: cover;
  display: block;
}

.upload-mask {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.privacy-note {
  margin: 10px 0 0;
  font-size: 12px;
  line-height: 1.6;
  color: #2e7d32;
  background: #eef7ee;
  border-radius: 8px;
  padding: 8px 10px;
}

.submit-btn {
  width: 100%;
  padding: 14px 0;
  margin-top: 6px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #c69a62, #ae7b43);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.submit-btn:disabled {
  opacity: 0.6;
}

.success-box {
  padding: 48px 20px;
  text-align: center;
  max-width: 560px;
  margin: 0 auto;
}

.success-icon { font-size: 56px; }

.success-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text, #3b2b1f);
  margin: 14px 0 8px;
}

.success-desc {
  font-size: 14px;
  color: var(--text-secondary, #8d7b67);
  line-height: 1.7;
  margin: 0 0 28px;
}

.success-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.success-link {
  padding: 14px 18px;
  border-radius: 999px;
  border: 1.5px solid rgba(200, 169, 126, 0.5);
  background: #fff;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  transition: all 0.2s;
}
.success-link:active { transform: scale(0.98); }

.success-link.primary {
  background: linear-gradient(135deg, #c69a62, #ae7b43);
  border-color: transparent;
}
.success-link.primary .link-title,
.success-link.primary .link-sub { color: #fff; }

.link-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text, #3b2b1f);
}

.link-sub {
  font-size: 12px;
  color: var(--text-secondary, #8d7b67);
}

@media (min-width: 600px) {
  .name-grid { flex-direction: row; }
  .name-grid .field { flex: 1; }
  .platform-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
