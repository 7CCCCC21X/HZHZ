from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # 导入 CORS
import requests
import time

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 固定 address
def fetch_transactions(wallet_addresses, fixed_address, key, chain="soneium", limit=20):
    base_url = "https://www.oklink.com/priapi/v1/lite/evm/address/detail/transactions"
    results = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Referer": "https://www.oklink.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "X-Apikey": key
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
            response.raise_for_status()
            data = response.json()
            # Only store the 'total' data
            results[address] = data.get('data', {}).get('total', None)
        except requests.RequestException as e:
            print(f"Error fetching data for {address}: {e}")
            results[address] = None

    return results


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_transactions')
def get_transactions():
    # 打印请求头
    print("Request Headers: ", request.headers)

    addresses = request.args.get('addresses', '')
    source = request.args.get('source', 'untitledbank')  # 默认来源为untitledbank

    if addresses:
        print(f"Received addresses: {source}")  # 打印接收到的钱包地址
        wallet_addresses = [addr.strip() for addr in addresses.split(',') if addr.strip()]

        if source == "quickswap":
            transactions_data = fetch_transactions(wallet_addresses, "0xeba58c20629ddab41e21a3e4e2422e583ebd9719",
                                                   "LWIzMWUtNDU0Ny05Mjk5LWI2ZDA3Yjc2MzFhYmEyYzkwM2NjfDI4NTMzMzE1MDEyOTkxNjU=",)
        elif source == "untitledbank1":
            transactions_data = fetch_transactions(wallet_addresses, "0x232554b4b291a446b4829300bec133fbb07a8f2a",
                                                   "LWIzMWUtNDU0Ny05Mjk5LWI2ZDA3Yjc2MzFhYmEyYzkwM2NjfDI4NTMzMzgzMTYzNTg0Nzc=")
        elif source == "untitledbank2":
            transactions_data = fetch_transactions(wallet_addresses, "0x85a4fb48c7f9383083864d62abeccdf318fd8e6f",
                                                   "LWIzMWUtNDU0Ny05Mjk5LWI2ZDA3Yjc2MzFhYmEyYzkwM2NjfDI4NTMzMzkxOTk0NzM4MzA=")
        elif source == "untitledbank3":
            transactions_data = fetch_transactions(wallet_addresses, "0xc675bb95d73ca7db2c09c3dc04daaa7944ccba41",
                                                   "LWIzMWUtNDU0Ny05Mjk5LWI2ZDA3Yjc2MzFhYmEyYzkwM2NjfDI4NTMzMzkxNTYyNTE3MjM=")

        result = {addr: total for addr, total in transactions_data.items()}
        return jsonify(result)
    else:
        return jsonify({"error": "没有提供钱包地址"}), 400


if __name__ == "__main__":
    app.run(debug=True)
