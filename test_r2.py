"""
R2 连接测试脚本
用法: python test_r2.py
"""
import os
import sys
import io
from dotenv import load_dotenv

load_dotenv()

# 读取配置
endpoint = os.getenv('R2_ENDPOINT', '').rstrip('/')
access_key = os.getenv('R2_ACCESS_KEY_ID', '')
secret_key = os.getenv('R2_SECRET_ACCESS_KEY', '')
bucket = os.getenv('R2_BUCKET_NAME', 'homestay')
public_url = os.getenv('R2_PUBLIC_URL', '').rstrip('/')

print("=" * 50)
print("R2 配置检查")
print("=" * 50)
print(f"R2_ENDPOINT:          {endpoint or '❌ 未设置'}")
print(f"R2_ACCESS_KEY_ID:     {'✅ 已设置 (' + access_key[:6] + '...)' if access_key else '❌ 未设置'}")
print(f"R2_SECRET_ACCESS_KEY: {'✅ 已设置 (' + secret_key[:6] + '...)' if secret_key else '❌ 未设置'}")
print(f"R2_BUCKET_NAME:       {bucket}")
print(f"R2_PUBLIC_URL:        {public_url or '❌ 未设置'}")
print()

if not all([endpoint, access_key, secret_key]):
    print("❌ 缺少必要的 R2 配置，无法测试连接")
    sys.exit(1)

import boto3
from botocore.config import Config as BotoConfig

client = boto3.client(
    's3',
    endpoint_url=endpoint,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    config=BotoConfig(signature_version='s3v4', connect_timeout=10, read_timeout=10, proxies={}),
    region_name='auto'
)

# 测试1: 上传
print("=" * 50)
print(f"1. 测试上传到 bucket '{bucket}'...")
print("=" * 50)
try:
    test_content = b"Hello R2 Test - delete me"
    client.upload_fileobj(
        io.BytesIO(test_content),
        bucket,
        '_test_connection.txt',
        ExtraArgs={'ContentType': 'text/plain'}
    )
    print("   ✅ 上传成功!")
except Exception as e:
    print(f"   ❌ 上传失败: {e}")
    sys.exit(1)

# 测试2: 读取
print(f"\n2. 测试读取文件...")
try:
    resp = client.get_object(Bucket=bucket, Key='_test_connection.txt')
    body = resp['Body'].read()
    if body == test_content:
        print("   ✅ 读取成功，内容匹配!")
    else:
        print(f"   ⚠️ 内容不匹配")
except Exception as e:
    print(f"   ❌ 读取失败: {e}")

# 测试3: 公共 URL 访问
if public_url:
    print(f"\n3. 测试公共 URL 访问...")
    test_url = f"{public_url}/_test_connection.txt"
    print(f"   URL: {test_url}")
    try:
        import urllib3
        http = urllib3.PoolManager()
        resp = http.request('GET', test_url, timeout=10)
        if resp.status == 200:
            print(f"   ✅ 公共 URL 可访问! (状态码: {resp.status})")
        else:
            print(f"   ⚠️ 状态码: {resp.status}")
            print("   请检查 Cloudflare R2 bucket 的公共访问设置和自定义域名配置")
    except Exception as e:
        print(f"   ❌ 公共 URL 访问失败: {e}")

# 测试4: 清理
print(f"\n4. 清理测试文件...")
try:
    client.delete_object(Bucket=bucket, Key='_test_connection.txt')
    print("   ✅ 已删除")
except Exception as e:
    print(f"   ⚠️ 删除失败: {e}")

print("\n" + "=" * 50)
print("✅ R2 连接测试完成!")
print("=" * 50)
