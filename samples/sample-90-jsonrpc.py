import json

from jsonschema import Draft7Validator

# JSON-RPC 2.0 共通部分
base_schema = {
    "type": "object",
    "properties": {
        "jsonrpc": {"type": "string", "const": "2.0"},
        "method": {"type": "string"},
        "params": {"type": ["object", "array"]},
        "id": {"type": ["string", "number", "null"]},
        "result": {},
        "error": {
            "type": "object",
            "properties": {
                "code": {"type": "integer"},
                "message": {"type": "string"},
                "data": {},
            },
            "required": ["code", "message"],
        },
    },
    "required": ["jsonrpc"],
    "additionalProperties": False,
}


def validate_jsonrpc(message: str):
    try:
        data = json.loads(message)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    validator = Draft7Validator(base_schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        return False, "; ".join(error.message for error in errors)

    # JSON-RPC 2.0 の追加ルールチェック
    if "method" in data:
        # Request or Notification
        if "result" in data or "error" in data:
            return False, "Request must not contain result or error"
    else:
        # Response
        if "result" not in data and "error" not in data:
            return False, "Response must contain either result or error"
        if "id" not in data:
            return False, "Response must have an id"

    return True, "Valid JSON-RPC 2.0 message"


# --- 動作テスト ---
msgs = [
    '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
    (
        "{"
        '"jsonrpc": "2.0", '
        '"method": "a", '
        '"params": {"a": [0,2,3], "ms":0.5 }, '
        '"id": 1'
        "}"
    ),
    (
        '{"params": {"a": [0,2,3], "b":0.5, "c":2}, '
        '"jsonrpc": "2.0", "method": "a", "id": 1}'
    ),
    '{"jsonrpc": "2.0", "result": 19, "id": 1}',
    (
        '{"jsonrpc": "2.0", '
        '"error": {"code": -32601, "message": "Not found"}, "id": 1}'
    ),
]

for m in msgs:
    valid, msg = validate_jsonrpc(m)
    print(m, "=>", valid, msg)
