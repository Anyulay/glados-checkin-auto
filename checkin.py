import os
import requests
import sys

# 读取并清洗环境变量（关键）
KOA_SESS = os.getenv("KOA_SESS", "").strip()
KOA_SESS_SIG = os.getenv("KOA_SESS_SIG", "").strip()
UA = os.getenv("UA", "").strip()

# 基本校验
if not KOA_SESS or not KOA_SESS_SIG or not UA:
    print("Error: 缺少必要环境变量（KOA_SESS / KOA_SESS_SIG / UA）")
    sys.exit(1)

# 请求头（绝对不能有换行）
headers = {
    "Cookie": f"koa:sess={KOA_SESS}; koa:sess.sig={KOA_SESS_SIG}",
    "User-Agent": UA,
    "Accept": "application/json"
}

# ======================
# 签到
# ======================
print("开始签到...")

checkin_resp = requests.post(
    "https://glados.rocks/api/user/checkin",
    headers=headers,
    json={"token": "glados.one"},
    timeout=15
)

print("HTTP 状态码:", checkin_resp.status_code)
print("原始返回:", checkin_resp.text)

try:
    result = checkin_resp.json()
except Exception:
    print("Error: 签到接口未返回 JSON")
    sys.exit(1)

message = result.get("message", "")
print("[签到返回信息]", message)

# 只要是这些情况，都视为成功
success_keywords = [
    "Checkin!",
    "Got",
    "Repeat",
    "Tomorrow"
]

if any(k.lower() in message.lower() for k in success_keywords):
    print("[OK] 签到流程完成")
else:
    print("Error: 签到失败或返回异常")
    sys.exit(1)

# ======================
# 获取账户信息（非必须，但有助于验证）
# ======================
print("获取账户信息...")

info_resp = requests.get(
    "https://glados.rocks/api/user/status",
    headers=headers,
    timeout=15
)

print("账户接口 HTTP 状态码:", info_resp.status_code)
print("账户原始返回:", info_resp.text)

try:
    info = info_resp.json()
    print("[账户信息]", info)
except Exception:
    print("Warning: 账户信息不是 JSON，但不影响签到完成")

print("脚本执行完毕")
