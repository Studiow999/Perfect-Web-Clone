#!/usr/bin/env python3
"""
测试引力API (yinli.one) 的连通性 - 全面测试版

测试文件位置: /Users/eric/AI_development/perfect-web-clone_V2/backend/test_yinli_api.py
测试完成后可以删除此文件
"""

import asyncio
import httpx
import json

# 配置
API_KEY = "sk-XBpSFjg4uVOxsmH6axYSqRKMR5gquF3VlnAIwrys4xvfUdTk"
MODEL = "claude-3-5-haiku-20241022"

# 所有可能的端点组合
BASE_URLS = [
    "https://yinli.one",
    "https://api.yinli.one",
    "https://yinli.one/api",
]

CHAT_PATHS = [
    "/v1/chat/completions",
    "/chat/completions",
    "/v1/completions",
]

MODELS_PATHS = [
    "/v1/models",
    "/models",
]


async def test_models_endpoint(client: httpx.AsyncClient, base_url: str, path: str):
    """测试 /models 端点获取可用模型列表"""
    url = base_url + path
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            try:
                data = response.json()
                models = data.get("data", [])
                model_ids = [m.get("id", "?") for m in models[:10]]
                return {
                    "url": url,
                    "success": True,
                    "status": 200,
                    "models": model_ids,
                    "total": len(models),
                }
            except:
                pass
        return {
            "url": url,
            "success": False,
            "status": response.status_code,
            "error": response.text[:150],
        }
    except Exception as e:
        return {"url": url, "success": False, "error": str(e)}


async def test_chat_endpoint(client: httpx.AsyncClient, base_url: str, path: str):
    """测试 chat/completions 端点"""
    url = base_url + path
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Say hi"}],
        "max_tokens": 20,
    }

    try:
        response = await client.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                data = response.json()
                # 检查是否是有效的API响应（不是HTML）
                if "choices" in data or "content" in data:
                    content = ""
                    if "choices" in data:
                        content = data["choices"][0].get("message", {}).get("content", "")
                    return {
                        "url": url,
                        "success": True,
                        "status": 200,
                        "response": content[:100],
                    }
            except:
                pass
            # 如果是HTML响应
            if "<!doctype" in response.text.lower() or "<html" in response.text.lower():
                return {
                    "url": url,
                    "success": False,
                    "status": 200,
                    "error": "返回了HTML网页，不是API端点",
                }

        return {
            "url": url,
            "success": False,
            "status": response.status_code,
            "error": response.text[:200],
        }
    except Exception as e:
        return {"url": url, "success": False, "error": str(e)}


async def main():
    print("=" * 70)
    print("引力API (yinli.one) 全面测试")
    print("=" * 70)
    print(f"API Key: {API_KEY[:12]}...{API_KEY[-4:]}")
    print(f"测试模型: {MODEL}")
    print("=" * 70)
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 测试 /models 端点
        print("【第一步】测试 /models 端点，获取可用模型列表...")
        print("-" * 50)

        models_results = []
        for base in BASE_URLS:
            for path in MODELS_PATHS:
                result = await test_models_endpoint(client, base, path)
                models_results.append(result)

                status_icon = "✅" if result["success"] else "❌"
                print(f"{status_icon} {result['url']}")
                if result["success"]:
                    print(f"   模型数量: {result['total']}")
                    print(f"   部分模型: {result['models'][:5]}")
                else:
                    print(f"   错误: {result.get('error', '')[:80]}")
                print()

        # 2. 测试 chat/completions 端点
        print()
        print("【第二步】测试 chat/completions 端点...")
        print("-" * 50)

        chat_results = []
        for base in BASE_URLS:
            for path in CHAT_PATHS:
                result = await test_chat_endpoint(client, base, path)
                chat_results.append(result)

                status_icon = "✅" if result["success"] else "❌"
                print(f"{status_icon} {result['url']}")
                if result["success"]:
                    print(f"   响应: {result['response']}")
                else:
                    print(f"   状态: {result.get('status', 'N/A')}")
                    print(f"   错误: {result.get('error', '')[:100]}")
                print()

    # 总结
    print()
    print("=" * 70)
    print("【测试结果总结】")
    print("=" * 70)

    successful_models = [r for r in models_results if r["success"]]
    successful_chat = [r for r in chat_results if r["success"]]

    if successful_models:
        print("\n✅ 可用的 Models 端点:")
        for r in successful_models:
            print(f"   {r['url']}")

    if successful_chat:
        print("\n✅ 可用的 Chat 端点:")
        for r in successful_chat:
            print(f"   {r['url']}")

        # 推荐配置
        best = successful_chat[0]
        base_url = best["url"].rsplit("/", 2)[0]  # 去掉 /v1/chat/completions
        print(f"\n【推荐 .env 配置】")
        print(f"   USE_CLAUDE_PROXY=true")
        print(f"   CLAUDE_PROXY_API_KEY={API_KEY}")
        print(f"   CLAUDE_PROXY_BASE_URL={base_url}")
        print(f"   CLAUDE_PROXY_MODEL={MODEL}")
    else:
        print("\n❌ 没有找到可用的端点!")
        print("\n可能原因:")
        print("   1. API Key 无效或过期")
        print("   2. 账户余额不足")
        print("   3. 模型名称不正确")
        print("\n请登录 https://yinli.one 检查账户状态")

    if successful_models and not successful_chat:
        print("\n💡 提示: Models 端点可用但 Chat 端点不可用")
        print("   可能是模型名称问题，上面列出的可用模型列表供参考")


if __name__ == "__main__":
    asyncio.run(main())
