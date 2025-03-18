from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # 导入 CORS
import requests
import time
import os

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)  # 启用 CORS

# 从环境变量中获取 API 密钥
API_KEY = os.getenv("API_KEY")  # 确保将你的API密钥设置为环境变量

# 获取交易数据的函数
def fetch_transactions(wallet_addresses, fixed_address, key, chain="soneium", limit=20):
    base_url = "https://www.oklink.com/priapi/v1/lite/evm/address/detail/transactions"
    results = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Referer": "https://www.oklink.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "X-Apikey": key  # 使用API密钥
    }
    for address in wallet_addresses:
        params = {
            "offset": 0,
            "direction": 3,
            "filterAddress": address,
            "limit": limit,
            "nonzeroValue": "false",
            "address": fixed_address,
            "chain": chain,
            "t": int(time.time() * 1000)  # 时间戳参数
        }
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()  # 确保请求成功
            data = response.json()
            # 只存储'total'数据
            results[address] = data.get('data', {}).get('total', None)
        except requests.RequestException as e:
            print(f"Error fetching data for {address}: {e}")
            results[address] = None

    return results

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 获取交易数据的路由
@app.route('/get_transactions')
def get_transactions():
    addresses = request.args.get('addresses', '')
    source = request.args.get('source', 'untitledbank')  # 默认来源为untitledbank

    if addresses:
        print(f"Received addresses: {source}")  # 打印接收到的钱包地址
        wallet_addresses = [addr.strip() for addr in addresses.split(',') if addr.strip()]

        # 根据请求的source选择对应的地址和API密钥
        if source == "quickswap":
            transactions_data = fetch_transactions(wallet_addresses, "0xeba58c20629ddab41e21a3e4e2422e583ebd9719", API_KEY)
        elif source == "untitledbank1":
            transactions_data = fetch_transactions(wallet_addresses, "0x232554b4b291a446b4829300bec133fbb07a8f2a", API_KEY)
        elif source == "untitledbank2":
            transactions_data = fetch_transactions(wallet_addresses, "0x85a4fb48c7f9383083864d62abeccdf318fd8e6f", API_KEY)
        elif source == "untitledbank3":
            transactions_data = fetch_transactions(wallet_addresses, "0xc675bb95d73ca7db2c09c3dc04daaa7944ccba41", API_KEY)

        result = {addr: total for addr, total in transactions_data.items()}
        return jsonify(result)
    else:
        return jsonify({"error": "没有提供钱包地址"}), 400

# 主程序入口
if __name__ == "__main__":
    app.run(debug=True)
