"""
R2 连接测试脚本
用法: python test_r2.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 读取配置
endpoint = os.getenv('R2_ENDPOINT', '')
access_key = os.getenv('R2_ACCESS_KEY_ID', '')
secret_key = os.getenv('R2_SECRET_ACCESS_KEY', '')
bucket = os.getenv('R2_BUCKET_NAME', 'homestay')
public_url = os.getenv('R2_PUBLIC_URL', '')

print("=" * 50)
print("R2 配置检查")
print("=" * 50)
print(f"R2_ENDPOINT:          {endpoint or '❌ 未设置'}")
print(f"R2_ACCESS_KEY_ID:     {'✅ 已设置 (' + access_key[:6] + '...)' if access_key else '❌ 未设置'}")
print(f"R2_SECRET_ACCESS_KEY: {'✅ 已设置 (' + secret_key[:6] + '...)' if secret_key else '❌ 未设置'}")
print(f"R2_BUCKET_NAME:       {bucket}")
print(f"R2_PUBLIC_URL:        {public_url or '❌ 未设置'}")
print()

# 验证 endpoint 格式
if endpoint:
    if 'r2.cloudflarestorage.com' not in endpoint:
        print("⚠️  警告: R2_ENDPOINT 应该是 S3 API 地址，格式如:")
        print("   https://<account-id>.r2.cloudflarestorage.com")
        print(f"   当前值: {endpoint}")
        print()

if not all([endpoint, access_key, secret_key]):
    print("❌ 缺少必要的 R2 配置，无法测试连接")
    sys.exit(1)

# 测试连接
print("=" * 50)
print("测试 R2 连接...")
print("=" * 50)

import boto3
from botocore.config import Config as BotoConfig

try:
    client = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=BotoConfig(signature_version='s3v4', connect_timeout=10, read_timeout=10),
        region_name='auto'
    )

    # 测试1: 列出 bucket
    print("\n1. 测试列出 bucket...")
    buckets = client.list_buckets()
    print(f"   ✅ 连接成功! 找到 {len(buckets['Buckets'])} 个 bucket:")
    for b in buckets['Buckets']:
        marker = " ← 目标" if b['Name'] == bucket else ""
        print(f"      - {b['Name']}{marker}")

    # 测试2: 上传测试文件
    print(f"\n2. 测试上传到 bucket '{bucket}'...")
    import io
    test_content = b"Hello R2 Test"
    client.upload_fileobj(
        io.BytesIO(test_content),
        bucket,
        '_test_connection.txt',
        ExtraArgs={'ContentType': 'text/plain'}
    )
    print("   ✅ 上传成功!")

    # 测试3: 读取测试文件
    print("\n3. 测试读取文件...")
    resp = client.get_object(Bucket=bucket, Key='_test_connection.txt')
    body = resp['Body'].read()
    if body == test_content:
        print("   ✅ 读取成功，内容匹配!")
    else:
        print(f"   ⚠️ 内容不匹配: 期望 {test_content}, 得到 {body}")

    # 测试4: 删除测试文件
    print("\n4. 清理测试文件...")
    client.delete_object(Bucket=bucket, Key='_test_connection.txt')
    print("   ✅ 已删除")

    # 测试5: 检查公共 URL
    if public_url:
        print(f"\n5. 公共 URL 配置: {public_url}")
        print(f"   图片将通过此域名访问: {public_url}/<filename>")

    print("\n" + "=" * 50)
    print("✅ R2 配置完全正确，所有测试通过!")
    print("=" * 50)

except Exception as e:
    print(f"\n   ❌ 连接失败: {e}")
    print("\n可能的原因:")
    print("  1. R2_ENDPOINT 地址不正确")
    print("  2. Access Key ID 或 Secret Access Key 错误")
    print("  3. 网络无法连接到 Cloudflare R2")
    print("  4. Bucket 名称不存在")
    sys.exit(1)
