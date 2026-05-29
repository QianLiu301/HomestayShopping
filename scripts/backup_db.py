"""数据库自动备份脚本
============================

功能：
    1. 用 pg_dump 把整个数据库导出为 SQL
    2. gzip 压缩（减小 5-10 倍体积，省 R2 流量）
    3. 上传到 Cloudflare R2 的 db_backups/ 目录
    4. 自动清理超过 RETENTION_DAYS 天的旧备份

环境变量：
    DATABASE_URL           - PostgreSQL 连接串 (必填)
    R2_ENDPOINT            - R2 接入点 (必填)
    R2_ACCESS_KEY_ID       - R2 访问密钥 (必填)
    R2_SECRET_ACCESS_KEY   - R2 密钥 (必填)
    R2_BUCKET_NAME         - R2 存储桶名 (必填)
    BACKUP_RETENTION_DAYS  - 保留天数 (选填，默认 30)
    BACKUP_PREFIX          - R2 内目录前缀 (选填，默认 db_backups/)

如何使用：
    # 本地测试
    python scripts/backup_db.py

    # Railway 上配置 Cron Job：
    # Railway 控制台 → 你的服务 → Settings → Cron Schedule
    # Schedule: 0 3 * * *   （每天凌晨 3 点 UTC = 北京时间 11:00）
    # Command:  python scripts/backup_db.py
"""

import os
import sys
import subprocess
import gzip
import shutil
import tempfile
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError


# ============ 配置 ============
DATABASE_URL = os.getenv('DATABASE_URL', '')
R2_ENDPOINT = os.getenv('R2_ENDPOINT', '')
R2_ACCESS_KEY = os.getenv('R2_ACCESS_KEY_ID', '')
R2_SECRET_KEY = os.getenv('R2_SECRET_ACCESS_KEY', '')
R2_BUCKET = os.getenv('R2_BUCKET_NAME', '')
RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
BACKUP_PREFIX = os.getenv('BACKUP_PREFIX', 'db_backups/')


def log(msg):
    """带时间戳的日志"""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    print(f'[{now}] {msg}', flush=True)


def check_env():
    """检查必需的环境变量"""
    missing = []
    for key in ['DATABASE_URL', 'R2_ENDPOINT', 'R2_ACCESS_KEY_ID',
                'R2_SECRET_ACCESS_KEY', 'R2_BUCKET_NAME']:
        if not os.getenv(key):
            missing.append(key)
    if missing:
        log(f'❌ 缺少环境变量: {", ".join(missing)}')
        sys.exit(1)


def dump_database(out_path):
    """用 pg_dump 导出数据库到 SQL 文件"""
    log(f'开始 pg_dump → {out_path}')

    # 解析 DATABASE_URL 拿到各组件，pg_dump 直接吃 URL 也行
    # 用 PGPASSWORD 环境变量避免密码出现在命令行
    parsed = urlparse(DATABASE_URL)
    env = os.environ.copy()
    if parsed.password:
        env['PGPASSWORD'] = parsed.password

    cmd = [
        'pg_dump',
        '--no-owner',         # 避免恢复时报 owner 不存在
        '--no-acl',           # 避免恢复时报权限
        '--clean',            # 加上 DROP 语句，可直接 restore
        '--if-exists',        # DROP 时加 IF EXISTS
        '--format=plain',
        DATABASE_URL,
    ]

    with open(out_path, 'w', encoding='utf-8') as f:
        result = subprocess.run(
            cmd, stdout=f, stderr=subprocess.PIPE,
            env=env, text=True, timeout=1800   # 30 分钟超时
        )

    if result.returncode != 0:
        log(f'❌ pg_dump 失败: {result.stderr[:1000]}')
        sys.exit(1)

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    log(f'✅ pg_dump 完成，{size_mb:.2f} MB')


def gzip_file(src, dst):
    """gzip 压缩"""
    log(f'压缩 → {dst}')
    with open(src, 'rb') as f_in:
        with gzip.open(dst, 'wb', compresslevel=6) as f_out:
            shutil.copyfileobj(f_in, f_out)
    size_mb = os.path.getsize(dst) / 1024 / 1024
    log(f'✅ 压缩完成，{size_mb:.2f} MB')


def upload_to_r2(local_path, remote_key):
    """上传到 R2"""
    log(f'上传 → s3://{R2_BUCKET}/{remote_key}')
    s3 = boto3.client(
        's3',
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name='auto',
    )
    s3.upload_file(local_path, R2_BUCKET, remote_key)
    log(f'✅ 上传完成')


def cleanup_old_backups():
    """清理 R2 上超过保留天数的旧备份"""
    if RETENTION_DAYS <= 0:
        log('跳过清理（RETENTION_DAYS=0）')
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    log(f'清理 {cutoff.strftime("%Y-%m-%d")} 之前的备份...')

    s3 = boto3.client(
        's3',
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name='auto',
    )

    deleted = 0
    try:
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=R2_BUCKET, Prefix=BACKUP_PREFIX):
            for obj in page.get('Contents', []):
                if obj['LastModified'] < cutoff:
                    s3.delete_object(Bucket=R2_BUCKET, Key=obj['Key'])
                    log(f'  删除: {obj["Key"]}')
                    deleted += 1
    except ClientError as e:
        log(f'⚠️  清理时出错（不影响本次备份）: {e}')
        return

    log(f'✅ 清理完成，删除 {deleted} 个旧备份')


def main():
    check_env()
    log('=' * 50)
    log('数据库备份开始')

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    remote_key = f'{BACKUP_PREFIX}backup_{timestamp}.sql.gz'

    with tempfile.TemporaryDirectory(prefix='dbbackup_') as tmpdir:
        sql_path = os.path.join(tmpdir, 'dump.sql')
        gz_path = os.path.join(tmpdir, 'dump.sql.gz')

        dump_database(sql_path)
        gzip_file(sql_path, gz_path)
        upload_to_r2(gz_path, remote_key)

    cleanup_old_backups()

    log('=' * 50)
    log('✅ 备份成功')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(f'❌ 备份失败: {type(e).__name__}: {e}')
        sys.exit(1)
