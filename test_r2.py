"""
R2 连接测试脚本
用法: python test_r2.py
"""
import os
import sys
import ssl
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

# 去除末尾斜杠
endpoint = endpoint.rstrip('/')

# 验证 endpoint 格式
if endpoint:
    if 'r2.cloudflarestorage.com' not in endpoint:
        print("⚠️  警告: R2_ENDPOINT 应该是 S3 API 地址，格式如:")
        print("   https://<account-id>.r2.cloudflarestorage.com")
        print(f"   当前值: {endpoint}")
        print()

# SSL 环境信息
print("=" * 50)
print("SSL 环境信息")
print("=" * 50)
print(f"Python 版本:    {sys.version}")
print(f"OpenSSL 版本:   {ssl.OPENSSL_VERSION}")
print(f"默认协议:       TLS {ssl.PROTOCOL_TLS}")
print()

if not all([endpoint, access_key, secret_key]):
    print("❌ 缺少必要的 R2 配置，无法测试连接")
    sys.exit(1)

# 测试1: 先用 urllib3 直接测试 HTTPS 连接
print("=" * 50)
print("步骤1: 测试 HTTPS 连接到 R2...")
print("=" * 50)
try:
    import urllib3
    http = urllib3.PoolManager()
    resp = http.request('GET', endpoint, timeout=10)
    print(f"   ✅ HTTPS 连接成功 (状态码: {resp.status})")
except Exception as e:
    print(f"   ❌ HTTPS 连接失败: {e}")
    print()
    print("   尝试禁用 SSL 验证测试...")
    try:
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        urllib3.disable_warnings()
        resp = http.request('GET', endpoint, timeout=10)
        print(f"   ⚠️ 禁用 SSL 验证后连接成功 (状态码: {resp.status})")
        print("   这说明是 SSL 证书/协议问题")
        print()
        print("   解决方案:")
        print("   1. 升级 Python 到 3.10+ (推荐)")
        print("   2. 或运行: pip install --upgrade certifi urllib3 botocore boto3")
    except Exception as e2:
        print(f"   ❌ 禁用 SSL 后仍然失败: {e2}")
        print("   这说明是网络连接问题（防火墙/代理）")
    sys.exit(1)

# 测试2: 用 boto3 连接 R2
print()
print("=" * 50)
print("步骤2: 测试 boto3 连接 R2...")
print("=" * 50)

import boto3
from botocore.config import Config as BotoConfig

try:
    client = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=BotoConfig(signature_version='s3v4', connect_timeout=10, read_timeout=10, proxies={}),
        region_name='auto'
    )

    # 列出 bucket
    print("\n   测试列出 bucket...")
    buckets = client.list_buckets()
    print(f"   ✅ 连接成功! 找到 {len(buckets['Buckets'])} 个 bucket:")
    for b in buckets['Buckets']:
        marker = " ← 目标" if b['Name'] == bucket else ""
        print(f"      - {b['Name']}{marker}")

    # 上传测试文件
    print(f"\n   测试上传到 bucket '{bucket}'...")
    import io
    test_content = b"Hello R2 Test"
    client.upload_fileobj(
        io.BytesIO(test_content),
        bucket,
        '_test_connection.txt',
        ExtraArgs={'ContentType': 'text/plain'}
    )
    print("   ✅ 上传成功!")

    # 删除测试文件
    print("\n   清理测试文件...")
    client.delete_object(Bucket=bucket, Key='_test_connection.txt')
    print("   ✅ 已删除")

    print("\n" + "=" * 50)
    print("✅ R2 配置完全正确，所有测试通过!")
    print("=" * 50)

except Exception as e:
    print(f"\n   ❌ boto3 连接失败: {e}")
    print("\n   尝试禁用 SSL 验证...")
    try:
        import botocore.httpsession
        # 使用不验证 SSL 的方式
        client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=BotoConfig(signature_version='s3v4', connect_timeout=10, read_timeout=10),
            region_name='auto',
            verify=False
        )
        import urllib3
        urllib3.disable_warnings()
        buckets = client.list_buckets()
        print(f"   ⚠️ 禁用 SSL 验证后连接成功! 找到 {len(buckets['Buckets'])} 个 bucket")
        print()
        print("   解决方案（按优先级）:")
        print("   1. 升级 Python 到 3.10+")
        print("   2. 运行: pip install --upgrade certifi urllib3 botocore boto3")
        print("   3. 或者在代码中设置 verify=False（不推荐，但可临时使用）")
    except Exception as e2:
        print(f"   ❌ 禁用 SSL 后仍然失败: {e2}")
        print("\n可能的原因:")
        print("  1. Access Key ID 或 Secret Access Key 错误")
        print("  2. 网络无法连接到 Cloudflare R2（检查防火墙/VPN/代理）")
        print("  3. Bucket 名称不存在")
    sys.exit(1)
