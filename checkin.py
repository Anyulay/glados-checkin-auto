import os
import sys
import time
import requests

# ====== 读取并清洗环境变量（去掉换行/空格）======
KOA_SESS = os.getenv("KOA_SESS", "").strip()
KOA_SESS_SIG = os.getenv("KOA_SESS_SIG", "").strip()
UA = os.getenv("UA", "").strip()

if not KOA_SESS or not KOA_SESS_SIG or not UA:
    print("Error: 缺少必要环境变量（KOA_SESS / KOA_SESS_SIG / UA）")
    sys.exit(1)

# ====== 请求头（绝对不能有换行）======
headers = {
    "Cookie": f"koa:sess={KOA_SESS}; koa:sess.sig={KOA_SESS_SIG}",
    "User-Agent": UA,
    "Accept": "application/json",
}

# ✅ 统一使用 glados.cloud
CHECKIN_URL = "https://glados.cloud/api/user/checkin"
STATUS_URL = "https://glados.cloud/api/user/status"

def post_with_retry(url, retries=3, timeout=30):
    for i in range(retries):
        try:
            return requests.post(
                url,
                headers=headers,
                json={"token": "glados.one"},
                timeout=timeout
            )
        except requests.exceptions.ReadTimeout:
            print(f"请求超时，第 {i+1}/{retries} 次重试...")
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print("网络请求异常：", repr(e))
            time.sleep(2)
    raise RuntimeError("多次请求失败/超时，放弃")

def get_with_retry(url, retries=3, timeout=30):
    for i in range(retries):
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except requests.exceptions.ReadTimeout:
            print(f"请求超时，第 {i+1}/{retries} 次重试...")
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print("网络请求异常：", repr(e))
            time.sleep(2)
    raise RuntimeError("多次请求失败/超时，放弃")

print("开始签到...")

try:
    checkin_resp = post_with_retry(CHECKIN_URL)
except Exception as e:
    print("Error: 签到请求失败：", e)
    sys.exit(1)

print("HTTP 状态码:", checkin_resp.status_code)
print("原始返回:", checkin_resp.text)

# 解析 JSON
try:
    result = checkin_resp.json()
except Exception:
    print("Error: 签到接口未返回 JSON（可能被拦截/异常页）")
    sys.exit(1)

code = result.get("code", None)
message = result.get("message", "")
print("[签到返回]", "code =", code, "| message =", message)

# ✅ 只把“真正签到成功/今天已签到”当成功
ok_keywords = [
    "Checkin! Got",                           # 签到成功
    "Checkin Repeats! Please Try Tomorrow",   # 今天已签到
]

if any(k.lower() in message.lower() for k in ok_keywords):
    print("[OK] 签到成功或今日已签到")
else:
    # 这里明确告诉你没签到成功，不再误判
    print("Error: 本次未签到成功（返回信息如下）：", message)
    sys.exit(1)

print("获取账户信息...")

try:
    info_resp = get_with_retry(STATUS_URL)
except Exception as e:
    print("Warning: 获取账户信息失败（不影响签到结果）：", e)
    print("脚本执行完毕")
    sys.exit(0)

print("账户接口 HTTP 状态码:", info_resp.status_code)
print("账户原始返回:", info_resp.text)

try:
    info = info_resp.json()
    print("[账户信息]", info)
except Exception:
    print("Warning: 账户信息不是 JSON（不影响签到）")

print("脚本执行完毕")
