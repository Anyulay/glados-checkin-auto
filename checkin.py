import os
import requests
import sys
import time

KOA_SESS = os.getenv("KOA_SESS", "").strip()
KOA_SESS_SIG = os.getenv("KOA_SESS_SIG", "").strip()
UA = os.getenv("UA", "").strip()

if not KOA_SESS or not KOA_SESS_SIG or not UA:
    print("Error: 缺少必要环境变量")
    sys.exit(1)

headers = {
    "Cookie": f"koa:sess={KOA_SESS}; koa:sess.sig={KOA_SESS_SIG}",
    "User-Agent": UA,
    "Accept": "application/json"
}

CHECKIN_URL = "https://glados.cloud/api/user/checkin"
STATUS_URL = "https://glados.cloud/api/user/status"

def post_with_retry(url, retries=3, timeout=20):
    for i in range(retries):
        try:
            return requests.post(
                url,
                headers=headers,
                json={"token": "glados.one"},
                timeout=timeout
            )
        except requests.exceptions.ReadTimeout:
            print(f"超时，第 {i+1} 次重试...")
            time.sleep(2)
    raise RuntimeError("多次请求超时，放弃")

print("开始签到...")

try:
    checkin_resp = post_with_retry(CHECKIN_URL)
except Exception as e:
    print("Error:", e)
    sys.exit(1)

print("HTTP 状态码:", checkin_resp.status_code)
print("原始返回:", checkin_resp.text)

try:
    result = checkin_resp.json()
except Exception:
    print("Error: 返回不是 JSON")
    sys.exit(1)

message = result.get("message", "")
print("[签到返回信息]", message)

if any(k in message for k in ["Checkin", "Repeat", "Tomorrow", "Got"]):
    print("[OK] 签到完成")
else:
    print("Error: 未识别的返回")
    sys.exit(1)

print("获取账户信息...")

try:
    info_resp = requests.get(STATUS_URL, headers=headers, timeout=20)
    print("账户返回:", info_resp.text)
except Exception:
    print("Warning: 获取账户信息失败（不影响签到）")

print("脚本执行完毕")
