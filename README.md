# 民宿服务平台 API

基于 Flask 的民宿服务平台后端 API，支持伴手礼商城和接送机服务。

## 技术栈

- **框架**: Flask 3.0
- **数据库**: PostgreSQL (Neon)
- **ORM**: SQLAlchemy
- **认证**: JWT

## 项目结构

```
homestay-api/
├── app/
│   ├── __init__.py        # Flask应用初始化
│   ├── api/               # API路由
│   │   ├── __init__.py    # 蓝图注册
│   │   ├── auth.py        # 认证API
│   │   ├── products.py    # 商品API
│   │   ├── categories.py  # 分类API
│   │   ├── vehicles.py    # 车型API
│   │   ├── locations.py   # 民宿点API
│   │   ├── orders.py      # 订单API
│   │   ├── coupons.py     # 优惠券API
│   │   ├── admin.py       # 管理后台API
│   │   └── settings.py    # 系统设置API
│   ├── models/
│   │   └── __init__.py    # 数据模型
│   └── utils/
│       └── __init__.py    # 工具函数
├── config.py              # 配置文件
├── run.py                 # 入口文件
├── requirements.txt       # 依赖
├── Procfile              # Render部署配置
└── .env.example          # 环境变量示例
```

## 本地开发

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd homestay-api
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填写你的数据库连接等信息
```

### 5. 运行

```bash
python run.py
```

访问 http://localhost:5000/health 测试

## API 文档

### 用户端 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/products | 获取商品列表 |
| GET | /api/products/:id | 获取商品详情 |
| GET | /api/products/featured | 获取推荐商品 |
| GET | /api/categories | 获取分类列表 |
| GET | /api/vehicles | 获取车型列表 |
| GET | /api/locations | 获取民宿点列表 |
| GET | /api/districts | 获取上海各区列表 |
| GET | /api/transfer/price | 获取接送机价格 |
| POST | /api/transfer/orders | 创建接送机订单 |
| POST | /api/shop/orders | 创建商城订单 |
| POST | /api/orders/query | 查询订单 |
| POST | /api/coupons/verify | 验证优惠券 |

### 管理端 API（需要认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 管理员登录 |
| GET | /api/admin/products | 获取商品列表 |
| POST | /api/admin/products | 创建商品 |
| PUT | /api/admin/products/:id | 更新商品 |
| DELETE | /api/admin/products/:id | 删除商品 |
| ... | ... | 其他管理API同理 |

### 请求参数

#### 多语言支持

所有GET请求支持 `lang` 参数：

```
GET /api/products?lang=en
```

支持的语言：`zh`（中文）、`en`（英文）、`ru`（俄语）、`es`（西班牙语）

#### 分页

列表接口支持分页：

```
GET /api/admin/products?page=1&per_page=10
```

### 响应格式

```json
{
    "code": 200,
    "message": "success",
    "data": { ... }
}
```

## 部署到 Render

1. 在 Render 创建新的 Web Service
2. 连接你的 GitHub 仓库
3. 配置环境变量：
   - `DATABASE_URL`: Neon数据库连接字符串
   - `SECRET_KEY`: 随机字符串
   - `JWT_SECRET_KEY`: 随机字符串
   - `FLASK_ENV`: production
4. 部署！

## 默认管理员账号

- 用户名: `admin`
- 密码: `admin123`

**请在生产环境中修改默认密码！**
