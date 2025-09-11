# coding: utf-8
import os, base64, json, subprocess, time, random

# 固定变量
UUID = os.environ.get("UUID", "20e6e496-cf19-45c8-b883-14f5e11cd9f1")
NAME = os.environ.get("NAME", "Vls-US-Amazon")
PORT = int(os.environ.get("PORT") or 3000)
CFIP_LIST = [
    "104.26.13.229",
    "104.16.165.90",
    "104.17.36.89",
    "104.19.155.123",
    "172.64.87.150",
    "ProxyIP.JP.CMLiussss.net"
]
CFIP = random.choice(CFIP_LIST)
CFPORT = 443
SUB_PATH = os.environ.get("SUB_PATH", "sub")

# 缓存目录
FILE_PATH = ".cache"
os.makedirs(FILE_PATH, exist_ok=True)

# Xray 配置（简化，主要inbounds/outbounds）
config = {
    "log": {"loglevel": "none"},
    "inbounds": [
        {
            "port": PORT,
            "protocol": "vless",
            "settings": {
                "clients": [{"id": UUID}],
                "decryption": "none",
                "fallbacks": [
                    {"path": "/vless-argo", "dest": 3001},
                    {"path": "/vmess-argo", "dest": 3002},
                    {"path": "/trojan-argo", "dest": 3003}
                ]
            },
            "streamSettings": {"network": "tcp"}
        },
        {"port": 3001, "listen": "127.0.0.1", "protocol": "vless",
         "settings": {"clients": [{"id": UUID}], "decryption": "none"},
         "streamSettings": {"network": "ws", "wsSettings": {"path": "/vless-argo"}}},
        {"port": 3002, "listen": "127.0.0.1", "protocol": "vmess",
         "settings": {"clients": [{"id": UUID, "alterId": 0}]},
         "streamSettings": {"network": "ws", "wsSettings": {"path": "/vmess-argo"}}},
        {"port": 3003, "listen": "127.0.0.1", "protocol": "trojan",
         "settings": {"clients": [{"password": UUID}]},
         "streamSettings": {"network": "ws", "wsSettings": {"path": "/trojan-argo"}}}
    ],
    "outbounds": [{"protocol": "freedom"}]
}

# 生成节点链接
async def generate_links():
    # 获取 Argo Tunnel 域名
    argo_domain = None
    try:
        with open("boot.log", "r", encoding="utf-8") as f:
            for line in f:
                if ".trycloudflare.com" in line:
                    argo_domain = line.strip().split("://")[-1]
                    break
    except:
        pass
    if not argo_domain:
        argo_domain = "example.trycloudflare.com"  # fallback

    ISP = "Cloudflare-Auto"

    # 节点链接
    VLESS_TLS = f"vless://{UUID}@{CFIP}:{CFPORT}?encryption=none&security=tls&sni={argo_domain}&fp=chrome&type=ws&host={argo_domain}&path=%2Fvless-argo%3Fed%3D2560#{NAME}-{ISP}-TLS"
    VMESS_TLS = {
        "v": "2", "ps": f"{NAME}-{ISP}-TLS", "add": CFIP, "port": str(CFPORT),
        "id": UUID, "aid": "0", "scy": "none", "net": "ws",
        "type": "none", "host": argo_domain, "path": "/vmess-argo?ed=2560",
        "tls": "tls", "sni": argo_domain, "fp": "chrome"
    }
    TROJAN_TLS = f"trojan://{UUID}@{CFIP}:{CFPORT}?security=tls&sni={argo_domain}&fp=chrome&type=ws&host={argo_domain}&path=%2Ftrojan-argo%3Fed%3D2560#{NAME}-{ISP}-TLS"

    VLESS_80 = f"vless://{UUID}@{CFIP}:80?encryption=none&security=none&type=ws&host={argo_domain}&path=%2Fvless-argo%3Fed%3D2560#{NAME}-{ISP}-80"
    VMESS_80 = {
        "v": "2", "ps": f"{NAME}-{ISP}-80", "add": CFIP, "port": "80",
        "id": UUID, "aid": "0", "scy": "none", "net": "ws",
        "type": "none", "host": argo_domain, "path": "/vmess-argo?ed=2560",
        "tls": "", "sni": "", "fp": ""
    }
    TROJAN_80 = f"trojan://{UUID}@{CFIP}:80?security=none&type=ws&host={argo_domain}&path=%2Ftrojan-argo%3Fed%3D2560#{NAME}-{ISP}-80"

    list_txt = "\n\n".join([
        VLESS_TLS,
        "vmess://" + base64.b64encode(json.dumps(VMESS_TLS).encode()).decode(),
        TROJAN_TLS,
        VLESS_80,
        "vmess://" + base64.b64encode(json.dumps(VMESS_80).encode()).decode(),
        TROJAN_80
    ])

    # 写入文件
    with open(os.path.join(FILE_PATH, "list.txt"), "w", encoding="utf-8") as f:
        f.write(list_txt)
    with open(os.path.join(FILE_PATH, "sub.txt"), "w", encoding="utf-8") as f:
        f.write(base64.b64encode(list_txt.encode()).decode())

    print("=== 节点信息 ===")
    print(list_txt)
    print("\n订阅链接(base64):")
    print(base64.b64encode(list_txt.encode()).decode())

    return list_txt

# 启动入口
if __name__ == "__main__":
    print("服务启动中...")
    import asyncio
    asyncio.run(generate_links())
