import json


# 呼び出したいメソッドを定義
def move(angle_diffs, move_sec, step_n):
    # 本来はロボット制御とか処理を書く
    print(f"move(angle_diffs={angle_diffs}, move_sec={move_sec}, step_n={step_n})")
    return [1, 2, 3, 4]

# 利用可能なメソッドをディスパッチ用にまとめる
methods = {
    "move": move,
}

def handle_request(json_str):
    try:
        request = json.loads(json_str)

        # 必須フィールドのチェック
        if request.get("jsonrpc") != "2.0":
            raise ValueError("Invalid JSON-RPC version")

        method_name = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        if method_name not in methods:
            raise ValueError(f"Method not found: {method_name}")

        # 関数呼び出し
        result = methods[method_name](**params)

        # レスポンスを作成
        response = {
            "jsonrpc": "2.0",
            "result": result,
            "id": req_id,
        }
    except Exception as e:
        # エラーレスポンス
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,  # Internal error
                "message": str(e),
            },
            "id": request.get("id") if "request" in locals() else None,
        }

    return json.dumps(response)

# --- 動作テスト ---
if __name__ == "__main__":
    request_json = """
    {
      "jsonrpc": "2.0",
      "method": "move",
      "params": {
        "angle_diffs": [10, -10, 0, 0],
        "move_sec": 0.2,
        "step_n": 40
      },
      "id": 1
    }
    """

    response_json = handle_request(request_json)
    print("Response:", response_json)
