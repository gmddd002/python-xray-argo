import os
import base64
import json
from flask import Flask, Response

app = Flask(__name__)

# 固定 UUID（如果没有，就生成一个）
UUID = os.environ.get("UUID", "20e6e496-cf19-45c8-b883-14f5e11cd9f1")

# 预置优选 IP 列表
CFIP_LIST = [
    "104.26.13.229",
    "104.16.165.90",
    "104.17.36.89",
    "104.19.155.123",
    "172.64.87.150",
    "ProxyIP.JP.CMLiussss.net"
]

# Argo 隧道域名（由 test.sh 捕获）
ARGO_DOMAIN = os.environ.get("ARGO_DOMAIN", "example.trycloudflare.com")


def gen_vless(ip):
    return f"vless://{UUID}@{ip}:443?encryption=none&security=tls&sni={ARGO_DOMAIN}&fp=chrome&type=ws&host={ARGO_DOMAIN}&path=/vless-argo?ed=2560#VLESS-{ip}"


def gen_vmess(ip):
    config = {
        "v": "2",
        "ps": f"VMESS-{ip}",
        "add": ip,
        "port": "443",
        "id": UUID,
        "aid": "0",
        "scy": "none",
        "net": "ws",
        "type": "none",
        "host": ARGO_DOMAIN,
        "path": "/vmess-argo?ed=2560",
        "tls": "tls",
        "sni": ARGO_DOMAIN,
        "fp": "chrome"
    }
    return "vmess://" + base64.b64encode(json.dumps(config).encode()).decode()


def gen_trojan(ip):
    return f"trojan://{UUID}@{ip}:443?security=tls&sni={ARGO_DOMAIN}&fp=chrome&type=ws&host={ARGO_DOMAIN}&path=/trojan-argo?ed=2560#Trojan-{ip}"


@app.route("/")
def index():
    return "Xray-Argo is running!"


@app.route("/nodes")
def nodes():
    # 生成节点文本
    nodes_list = []
    for ip in CFIP_LIST:
        nodes_list.append(gen_vless(ip))
        nodes_list.append(gen_vmess(ip))
        nodes_list.append(gen_trojan(ip))
    return Response("\n".join(nodes_list), mimetype="text/plain")


@app.route("/sub")
def sub():
    # 生成 Base64 订阅
    nodes_list = []
    for ip in CFIP_LIST:
        nodes_list.append(gen_vless(ip))
        nodes_list.append(gen_vmess(ip))
        nodes_list.append(gen_trojan(ip))
    sub_content = "\n".join(nodes_list)
    sub_b64 = base64.b64encode(sub_content.encode()).decode()
    return Response(sub_b64, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
