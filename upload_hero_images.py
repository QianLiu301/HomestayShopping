"""
上传 hero 背景图到 Cloudflare R2
用法: python upload_hero_images.py <desktop_image> <mobile_image>
示例: python upload_hero_images.py hero-bg.jpg hero-bg-mobile.jpg

需要在 .env 中配置:
  R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME
"""
import os
import sys

import boto3
from botocore.config import Config as BotoConfig

# 尝试加载 .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CONTENT_TYPES = {
    'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
    'png': 'image/png', 'webp': 'image/webp',
}

def get_r2_client():
    endpoint = os.getenv('R2_ENDPOINT')
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    if not all([endpoint, access_key, secret_key]):
        print("ERROR: R2_ENDPOINT / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY 未配置")
        sys.exit(1)
    return boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=BotoConfig(signature_version='s3v4', proxies={}),
        region_name='auto',
    )

def upload(client, bucket, local_path, r2_key):
    ext = local_path.rsplit('.', 1)[-1].lower()
    ct = CONTENT_TYPES.get(ext, 'application/octet-stream')
    with open(local_path, 'rb') as f:
        client.upload_fileobj(f, bucket, r2_key, ExtraArgs={'ContentType': ct})
    public_url = os.getenv('R2_PUBLIC_URL', '').rstrip('/')
    print(f"  OK: {local_path} -> {r2_key}")
    if public_url:
        print(f"  URL: {public_url}/{r2_key}")

def main():
    if len(sys.argv) < 3:
        print("用法: python upload_hero_images.py <desktop_image> <mobile_image>")
        print("示例: python upload_hero_images.py hero-bg.jpg hero-bg-mobile.jpg")
        sys.exit(1)

    desktop_img = sys.argv[1]
    mobile_img = sys.argv[2]

    for path in [desktop_img, mobile_img]:
        if not os.path.isfile(path):
            print(f"ERROR: 文件不存在 -> {path}")
            sys.exit(1)

    client = get_r2_client()
    bucket = os.getenv('R2_BUCKET_NAME', 'homestay')

    print(f"\n上传 hero 背景图到 R2 bucket: {bucket}\n")
    upload(client, bucket, desktop_img, 'hero-bg.jpg')
    upload(client, bucket, mobile_img, 'hero-bg-mobile.jpg')
    print("\n完成! 请确保 VITE_R2_PUBLIC_URL 已正确配置。")

if __name__ == '__main__':
    main()
