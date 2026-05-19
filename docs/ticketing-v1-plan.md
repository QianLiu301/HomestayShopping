# Ticketing V1 方案设计

## 目标
新增一个独立的“门票 / 玩乐”业务线，用于售卖迪士尼、上海动物园、上海中心等景点门票，并支持：

- 多景点管理
- 成人 / 儿童 / 老人票型
- 指定游玩日期
- 实名信息收集
- 护照/证件信息收集
- 可选接送 / 包车加购
- 后台独立维护价格
- 后台上传 PDF / 图片票据并发送给客人
- 与现有订单体系尽量保持一致的支付与查询体验

---

## 一、产品定位
门票业务不并入现有商城商品模型，也不直接塞进接送机模型，而是作为第三条独立业务线：

1. 接送机
2. 商城
3. 门票 / 玩乐

首页在 [`h5/src/views/Home.vue`](h5/src/views/Home.vue) 的服务区新增一个服务卡片入口，点击进入门票列表页。

---

## 二、V1 实施顺序
建议按以下顺序开发：

### 第 1 阶段：后端模型 + API
先把门票业务的数据结构稳定下来。

### 第 2 阶段：后台管理
先让你能录入景点、票种、价格、订单与票据。

### 第 3 阶段：H5 门票页面
再接列表页、详情页、下单页。

### 第 4 阶段：首页入口
最后把门票入口卡片挂到首页。

这样可以避免首页先放入口、但实际业务页和后台数据都还没准备好。

---

## 三、数据库模型设计
建议在 [`app/models/__init__.py`](app/models/__init__.py) 中新增以下模型。

### 1. TicketAttraction 景点主表
用于保存景点基础信息。

字段建议：

- `id`
- `name_zh` / `name_en` / `name_ru` / `name_es`
- `subtitle_zh` / `subtitle_en` / `subtitle_ru` / `subtitle_es`
- `desc_zh` / `desc_en` / `desc_ru` / `desc_es`
- `address_zh` / `address_en` / `address_ru` / `address_es`
- `open_hours_zh` / `open_hours_en` / `open_hours_ru` / `open_hours_es`
- `visit_notice_zh` / `visit_notice_en` / `visit_notice_ru` / `visit_notice_es`
- `refund_rule_zh` / `refund_rule_en` / `refund_rule_ru` / `refund_rule_es`
- `cover_image`
- `images` (JSON)
- `city`
- `category`
- `tags` (JSON)
- `featured`
- `real_name_required`
- `passport_required`
- `status`
- `sort_order`
- `created_at`
- `updated_at`

### 2. TicketPackage 票种表
一个景点可对应多个票种。

示例：

- 上海迪士尼 1 日成人票
- 上海迪士尼 1 日儿童票
- 上海动物园 成人票
- 上海中心 118 层观光票

字段建议：

- `id`
- `attraction_id`
- `package_name_zh` / `package_name_en` / `package_name_ru` / `package_name_es`
- `ticket_type`：`adult` / `child` / `senior` / `family` / `combo`
- `sale_price`
- `original_price`
- `age_rule_zh` / `age_rule_en` / `age_rule_ru` / `age_rule_es`
- `booking_notice_zh` / `booking_notice_en` / `booking_notice_ru` / `booking_notice_es`
- `refund_rule_zh` / `refund_rule_en` / `refund_rule_ru` / `refund_rule_es`
- `inventory_mode`：`unlimited` / `manual_quota`
- `quota_total`
- `quota_used`
- `available_days` (JSON，可选)
- `status`
- `sort_order`
- `created_at`
- `updated_at`

### 3. TicketOrder 门票订单表
门票订单主表。

字段建议：

- `id`
- `order_no`
- `attraction_id`
- `visit_date`
- `contact_name`
- `contact_phone`
- `contact_email`
- `booking_no`
- `lang`
- `total_price`
- `status`
- `payment_status`
- `remark`
- `admin_note`
- `need_transfer`
- `transfer_vehicle_id`
- `transfer_service_type`
- `transfer_price_snapshot`
- `package_snapshot` (JSON)
- `voucher_delivery_status`
- `created_at`
- `updated_at`

### 4. TicketTraveler 出行人表
一个订单可对应多个实名游客。

字段建议：

- `id`
- `order_id`
- `traveler_type`：`adult` / `child` / `senior`
- `full_name`
- `nationality`
- `document_type`
- `document_no`
- `date_of_birth`
- `gender`
- `created_at`

### 5. TicketVoucher 票据文件表
后台上传给客人的电子票据。

字段建议：

- `id`
- `order_id`
- `file_url`
- `file_name`
- `file_type`
- `uploaded_by`
- `sent_to_customer`
- `sent_at`
- `created_at`

### 6. TicketTransportPrice 门票加购用车价格表
复用现有车辆，但价格单独配置。

字段建议：

- `id`
- `attraction_id`
- `vehicle_id`
- `service_type`：`pickup_only` / `dropoff_only` / `round_trip` / `charter`
- `price`
- `status`
- `sort_order`

---

## 四、后端 API 设计
建议新增 [`app/api/tickets.py`](app/api/tickets.py)。

### H5 公开接口
- `GET /api/tickets/attractions`
- `GET /api/tickets/attractions/<id>`
- `GET /api/tickets/packages?attraction_id=...`
- `GET /api/tickets/transport-options?attraction_id=...`
- `POST /api/tickets/orders`
- `POST /api/tickets/orders/query`
- `GET /api/tickets/orders/<order_no>`

### 管理后台接口
建议在 [`app/api/admin.py`](app/api/admin.py) 中新增：

- `GET /api/admin/ticket-attractions`
- `POST /api/admin/ticket-attractions`
- `PUT /api/admin/ticket-attractions/<id>`
- `DELETE /api/admin/ticket-attractions/<id>`
- `GET /api/admin/ticket-packages`
- `POST /api/admin/ticket-packages`
- `PUT /api/admin/ticket-packages/<id>`
- `DELETE /api/admin/ticket-packages/<id>`
- `GET /api/admin/ticket-transport-pricing`
- `POST /api/admin/ticket-transport-pricing`
- `PUT /api/admin/ticket-transport-pricing/<id>`
- `DELETE /api/admin/ticket-transport-pricing/<id>`
- `GET /api/admin/ticket-orders`
- `GET /api/admin/ticket-orders/<id>`
- `PUT /api/admin/ticket-orders/<id>/status`
- `POST /api/admin/ticket-orders/<id>/voucher`
- `POST /api/admin/ticket-orders/<id>/send-voucher`

---

## 五、后台页面设计
建议新增以下页面。

### 1. `TicketAttractions.vue`
用于景点管理：

- 景点名称多语言
- 封面图 / 轮播图上传
- 地址 / 开放时间
- 预订须知 / 退款规则
- 是否推荐 / 是否启用

### 2. `TicketPackages.vue`
用于票种管理：

- 选择所属景点
- 成人 / 儿童 / 老人票
- 原价 / 售价
- 年龄说明
- 预订说明
- 启用状态

### 3. `TicketTransportPricing.vue`
用于门票加购用车价格管理：

- 景点
- 车辆
- 服务类型
- 单独价格

### 4. `TicketOrders.vue`
用于门票订单管理：

- 查看门票订单
- 查看出行人实名信息
- 更新状态
- 上传 PDF / 图片票据
- 标记已发送

---

## 六、H5 页面设计
建议新增以下 H5 页面。

### 1. `Tickets.vue`
门票列表页。

包含：
- 景点卡片
- 价格起始展示
- 可订标签
- 推荐标签
- 分类筛选（V1 可先简化）

### 2. `TicketDetail.vue`
门票详情页。

包含：
- 景点图片
- 地址 / 开放时间
- 预订须知
- 退款规则
- 游玩日期选择
- 成人 / 儿童 / 老人票种
- 可选用车加购

### 3. `TicketCheckout.vue`
门票下单页。

包含：
- 游玩日期
- 所选票种
- 出行人列表
- 护照 / 证件信息
- 联系方式
- 是否加购接送 / 包车
- 提交订单

### 4. `TicketOrderResult.vue`
下单成功页。

### 5. `TicketOrderQuery.vue`
门票订单查询页。

---

## 七、首页插入策略
在 [`h5/src/views/Home.vue`](h5/src/views/Home.vue) 的服务区域新增一个门票服务卡片。

推荐形式：

- 接送服务
- 精品商城
- 门票玩乐

点击门票玩乐卡片时：
- 不走现有 [`goToTransfer()`](h5/src/views/Home.vue) 逻辑
- 直接跳转到新页面 `/tickets`

注意：
当前首页的 [`serviceTypes`](h5/src/views/Home.vue) 是接送业务内部选项，不适合直接塞入“门票”。
所以首页服务区建议重构为：

1. 第一层：三大业务入口卡片
2. 第二层：如果当前选中“接送服务”，再展示车辆卡片

这样结构更清晰。

---

## 八、文件上传策略
继续复用 [`app/utils/storage.py`](app/utils/storage.py) 上传逻辑，但新增票据业务目录，例如：

- `tickets/vouchers/...`

支持格式建议：
- PDF
- JPG
- JPEG
- PNG
- WEBP

后台上传后：
- 保存到 `TicketVoucher`
- 记录文件名、类型、上传时间
- 后续可通过邮件或订单页下载给客人

---

## 九、V1 范围控制
### V1 必做
- 10 个左右景点
- 景点管理
- 票种管理
- 成人/儿童/老人票
- 游玩日期
- 实名 / 护照信息
- 可选门票加购用车
- 后台上传票据
- 订单状态流转
- 首页门票入口

### V1 暂不做
- 第三方 OTA 自动对接
- 实时库存同步
- 复杂日历库存算法
- 自动出票
- 多层组合套餐引擎

---

## 十、下一步执行清单
下一步将正式开始代码实现，按顺序推进：

1. 在 [`app/models/__init__.py`](app/models/__init__.py) 新增门票模型
2. 在 [`app/api/tickets.py`](app/api/tickets.py) 新增公开接口
3. 在 [`app/api/admin.py`](app/api/admin.py) 新增后台门票管理接口
4. 在 [`app/api/__init__.py`](app/api/__init__.py) 注册 tickets 路由
5. 在 [`admin/src/router/index.js`](admin/src/router/index.js) 与后台菜单中加入门票管理入口
6. 新增后台页面骨架
7. 新增 H5 路由与页面骨架
8. 最后在 [`h5/src/views/Home.vue`](h5/src/views/Home.vue) 增加门票服务卡片入口
