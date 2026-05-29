# scripts/ - 运维脚本

## backup_db.py - 数据库自动备份

每天凌晨自动把 PostgreSQL 数据库导出 + 压缩 + 上传到 R2，自动保留 30 天。

### 本地测试

```bash
cd D:\homestay_all\homestay-api
python scripts/backup_db.py
```

应该看到形如：
```
[2026-05-28 ...] 数据库备份开始
[2026-05-28 ...] 开始 pg_dump → /tmp/dbbackup_xxx/dump.sql
[2026-05-28 ...] ✅ pg_dump 完成，3.42 MB
[2026-05-28 ...] 压缩 → /tmp/dbbackup_xxx/dump.sql.gz
[2026-05-28 ...] ✅ 压缩完成，0.51 MB
[2026-05-28 ...] 上传 → s3://homestayshopping/db_backups/backup_20260528_120000.sql.gz
[2026-05-28 ...] ✅ 上传完成
[2026-05-28 ...] ✅ 清理完成，删除 0 个旧备份
[2026-05-28 ...] ✅ 备份成功
```

### Railway 上配置定时任务

Railway 现在原生支持 Cron Jobs（每个服务）。配置步骤：

1. 打开 Railway 控制台 → 进你的项目 → 选 `homestay-api` 服务
2. **Settings** 标签
3. 找到 **"Cron Schedule"** 字段
4. 填入：

```
0 3 * * *
```
（每天 UTC 时间 03:00 = 北京时间 11:00 自动跑一次）

5. **Custom Start Command** 字段填：
```
python scripts/backup_db.py
```

> ⚠️ **注意**：如果 Custom Start Command 填了备份命令，**主服务（gunicorn run:app）就不会启动了**。Railway 的 cron 模式是把"这个服务当成定时任务跑"，不是"在主服务旁边再跑一个"。

### 正确做法：在 Railway 上**新建一个 Service** 专门做备份

1. Railway 项目里点 "+ New" → "Empty Service"
2. 给它起名 `db-backup`
3. 连同一个 GitHub 仓库（同样代码）
4. 在它的 Settings 里：
   - **Cron Schedule**: `0 3 * * *`
   - **Start Command**: `python scripts/backup_db.py`
5. 复制环境变量（DATABASE_URL, R2_*）

这样：
- 主服务 `homestay-api` 继续跑 gunicorn 对外服务
- 新服务 `db-backup` 每天凌晨 3 点跑一次备份就退出

### 验证备份成功

打开 [Cloudflare R2 控制台](https://dash.cloudflare.com/) → 找到 `homestayshopping` bucket → 应该看到 `db_backups/backup_YYYYMMDD_HHMMSS.sql.gz` 文件。

### 如何恢复数据库（万一翻车了）

```bash
# 1. 下载备份
aws s3 cp s3://homestayshopping/db_backups/backup_20260528_030000.sql.gz . \
  --endpoint-url=$R2_ENDPOINT

# 2. 解压
gunzip backup_20260528_030000.sql.gz

# 3. 恢复（⚠️会清空目标库）
psql $DATABASE_URL < backup_20260528_030000.sql
```

### 修改保留天数

设置环境变量 `BACKUP_RETENTION_DAYS=7` 改为只保留 7 天（默认 30 天）。
