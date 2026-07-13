"""
文件上传工具 — 支持 Cloudflare R2 (S3兼容) 和本地存储
配置了 R2 环境变量时自动使用 R2，否则回退到本地 uploads 目录。
"""
import io
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

# 图片压缩配置
MAX_IMAGE_WIDTH = 1200    # 最大宽度
MAX_IMAGE_HEIGHT = 1200   # 最大高度
JPEG_QUALITY = 82         # JPEG 压缩质量
WEBP_QUALITY = 80         # WebP 压缩质量


def _compress_image(file_storage, ext):
    """压缩图片，返回 (BytesIO, new_ext)。Pillow 不可用时直接返回原文件。
    HEIC/HEIF（iPhone 默认格式）会转换为 JPEG。"""
    # GIF 不压缩
    if ext == 'gif':
        file_storage.stream.seek(0)
        buf = io.BytesIO(file_storage.stream.read())
        return buf, ext

    # 延迟导入 Pillow，不可用时跳过压缩
    try:
        from PIL import Image, ImageOps
    except ImportError:
        file_storage.stream.seek(0)
        buf = io.BytesIO(file_storage.stream.read())
        return buf, ext

    # HEIC/HEIF 需要 pillow-heif 插件解码，统一转成 JPEG
    if ext in ('heic', 'heif'):
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            # 插件不可用时无法解码 HEIC，原样返回（由调用方决定是否拒绝）
            file_storage.stream.seek(0)
            buf = io.BytesIO(file_storage.stream.read())
            return buf, ext
        try:
            file_storage.stream.seek(0)
            img = Image.open(file_storage.stream)
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=JPEG_QUALITY, optimize=True)
            buf.seek(0)
            return buf, 'jpg'
        except Exception:
            file_storage.stream.seek(0)
            buf = io.BytesIO(file_storage.stream.read())
            return buf, ext

    try:
        file_storage.stream.seek(0)
        img = Image.open(file_storage.stream)

        # 处理 EXIF 旋转
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # 转换 RGBA → RGB（JPEG 不支持 alpha）
        if img.mode in ('RGBA', 'P') and ext in ('jpg', 'jpeg'):
            img = img.convert('RGB')

        # 等比缩放
        img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.LANCZOS)

        buf = io.BytesIO()
        if ext in ('jpg', 'jpeg'):
            img.save(buf, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        elif ext == 'webp':
            img.save(buf, format='WEBP', quality=WEBP_QUALITY)
        elif ext == 'png':
            img.save(buf, format='PNG', optimize=True)
        else:
            img.save(buf, format=img.format or 'JPEG', quality=JPEG_QUALITY)

        buf.seek(0)
        return buf, ext
    except Exception:
        # 压缩失败时回退到原文件
        file_storage.stream.seek(0)
        buf = io.BytesIO(file_storage.stream.read())
        return buf, ext


def get_r2_public_url():
    """获取 R2 公开访问 URL，未配置时返回 None"""
    return os.getenv('R2_PUBLIC_URL', '').rstrip('/') or None


def upload_file(file_storage, upload_folder):
    """
    上传文件，返回可访问的 URL。
    - 如果配置了 R2 → 上传到 R2
      - 有 R2_PUBLIC_URL → 返回公开 URL（最快，CDN 直达）
      - 无 R2_PUBLIC_URL → 返回 /api/images/filename 代理路径
    - 否则 → 保存到本地 upload_folder，返回 /uploads/filename
    """
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    # 压缩图片
    compressed_buf, ext = _compress_image(file_storage, ext)

    r2 = _get_r2_client()
    bucket = os.getenv('R2_BUCKET_NAME', 'homestay')

    if r2:
        content_type = _CONTENT_TYPES.get(ext, 'application/octet-stream')
        compressed_buf.seek(0)
        r2.upload_fileobj(
            compressed_buf,
            bucket,
            filename,
            ExtraArgs={'ContentType': content_type}
        )
        # 优先返回公开 URL（CDN 直达，最快）
        public_url = get_r2_public_url()
        if public_url:
            url = f"{public_url}/{filename}"
        else:
            url = f"/api/images/{filename}"
    else:
        # 回退到本地存储
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        with open(filepath, 'wb') as f:
            f.write(compressed_buf.read())
        url = f"/uploads/{filename}"

    return url


def upload_private_file(file_storage, private_folder):
    """
    上传私密文件（如护照照片），返回文件 key（非公开 URL）。
    - R2 模式：存储在 private/ 前缀下，key = private/<uuid>.<ext>
    - 本地模式：存储在 private_folder（不在静态服务目录下），key = private/<uuid>.<ext>
    访问必须通过管理端鉴权代理接口。
    """
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    compressed_buf, ext = _compress_image(file_storage, ext)

    # HEIC 未能转换（缺 pillow-heif 插件）时拒绝，避免存下浏览器无法预览的格式
    if ext in ('heic', 'heif'):
        raise ValueError('HEIC_NOT_SUPPORTED')

    filename = f"{uuid.uuid4().hex}.{ext}"
    key = f"private/{filename}"

    r2 = _get_r2_client()
    bucket = os.getenv('R2_BUCKET_NAME', 'homestay')

    if r2:
        content_type = _CONTENT_TYPES.get(ext, 'application/octet-stream')
        compressed_buf.seek(0)
        r2.upload_fileobj(
            compressed_buf,
            bucket,
            key,
            ExtraArgs={'ContentType': content_type}
        )
    else:
        os.makedirs(private_folder, exist_ok=True)
        filepath = os.path.join(private_folder, filename)
        with open(filepath, 'wb') as f:
            f.write(compressed_buf.read())

    return key


def get_private_file(key, private_folder):
    """读取私密文件，返回 (bytes, content_type) 或 (None, None)。key 形如 private/<filename>"""
    if not key or not key.startswith('private/') or '..' in key:
        return None, None
    filename = key.split('/', 1)[1]

    r2 = _get_r2_client()
    if r2:
        return get_r2_file(key)

    filepath = os.path.join(private_folder, filename)
    if not os.path.isfile(filepath):
        return None, None
    ext = filename.rsplit('.', 1)[-1].lower()
    with open(filepath, 'rb') as f:
        return f.read(), _CONTENT_TYPES.get(ext, 'application/octet-stream')


# ==================== R2 图片代理缓存 ====================

# 简易 LRU 内存缓存：最多缓存 200 张图片（约 200MB 上限）
_image_cache = {}
_cache_order = []
_CACHE_MAX = 200


def _cache_put(key, data, content_type):
    """写入缓存"""
    if key in _image_cache:
        return
    if len(_cache_order) >= _CACHE_MAX:
        oldest = _cache_order.pop(0)
        _image_cache.pop(oldest, None)
    _image_cache[key] = (data, content_type)
    _cache_order.append(key)


def _cache_get(key):
    """读取缓存，命中时返回 (data, content_type)，否则 (None, None)"""
    item = _image_cache.get(key)
    if item:
        # 移到队尾（最近使用）
        try:
            _cache_order.remove(key)
            _cache_order.append(key)
        except ValueError:
            pass
        return item
    return None, None


def get_r2_file(key):
    """从 R2 读取文件（带内存缓存），返回 (bytes, content_type) 或 (None, None)"""
    # 先查缓存
    cached_data, cached_ct = _cache_get(key)
    if cached_data is not None:
        return cached_data, cached_ct

    r2 = _get_r2_client()
    if not r2:
        return None, None
    bucket = os.getenv('R2_BUCKET_NAME', 'homestay')
    try:
        resp = r2.get_object(Bucket=bucket, Key=key)
        data = resp['Body'].read()
        content_type = resp.get('ContentType', 'application/octet-stream')
        # 存入缓存
        _cache_put(key, data, content_type)
        return data, content_type
    except Exception:
        return None, None
