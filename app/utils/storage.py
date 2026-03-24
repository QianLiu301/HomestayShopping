"""
文件上传工具 — 支持 Cloudflare R2 (S3兼容) 和本地存储
配置了 R2 环境变量时自动使用 R2，否则回退到本地 uploads 目录。
"""
import os
import uuid

import boto3
from botocore.config import Config as BotoConfig


def _get_r2_client():
    """获取 R2 客户端，未配置时返回 None"""
    endpoint = os.getenv('R2_ENDPOINT')
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    if not all([endpoint, access_key, secret_key]):
        return None
    return boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=BotoConfig(
            signature_version='s3v4',
            proxies={},          # 绕过系统代理，直连 R2
        ),
        region_name='auto'
    )


# 文件扩展名 → Content-Type 映射
_CONTENT_TYPES = {
    'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
    'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'
}


def upload_file(file_storage, upload_folder):
    """
    上传文件，返回可访问的 URL。
    - 如果配置了 R2 → 上传到 R2，返回完整公开 URL
    - 否则 → 保存到本地 upload_folder，返回 /uploads/filename
    """
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    r2 = _get_r2_client()
    bucket = os.getenv('R2_BUCKET_NAME', 'homestay')
    public_url = os.getenv('R2_PUBLIC_URL', '')  # e.g. https://img.your-domain.com

    if r2 and public_url:
        content_type = _CONTENT_TYPES.get(ext, 'application/octet-stream')
        # 确保流位置在起始处，避免上传空文件
        file_storage.stream.seek(0)
        r2.upload_fileobj(
            file_storage.stream,
            bucket,
            filename,
            ExtraArgs={'ContentType': content_type}
        )
        # 返回完整公开 URL
        url = f"{public_url.rstrip('/')}/{filename}"
    else:
        # 回退到本地存储
        file_storage.save(os.path.join(upload_folder, filename))
        url = f"/uploads/{filename}"

    return url
