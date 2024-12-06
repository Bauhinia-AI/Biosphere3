# post
import requests
import json
from typing import Any, Dict, List, Callable

# 扩展的工具配置字典
TOOL_CONFIG = {
    "trade_item": {
        "method": "POST",
        "url": "http://47.95.21.135:8082/ammPool/trade",
        "headers": {"Content-Type": "application/json"},
        "params": {
            # param_name: (api_param_name, param_type)
            "character_id": ("characterId", int),
            "trade_type": ("tradeType", int),
            "item_name": ("itemName", str),
            "item_quantity": ("itemQuantity", int),
            "item_trade_quantity": ("itemTradeQuantity", int),
            "money": ("money", float),
        },
    },
    "get_freelance_jobs": {
        "method": "GET",
        "url": "http://47.95.21.135:8082/freelanceWork/getAll",
        "headers": {"Content-Type": "application/json"},
        "params": {},
    },
    "get_public_jobs": {
        "method": "GET",
        "url": "http://47.95.21.135:8082/publicWork/getAll",
        "headers": {"Content-Type": "application/json"},
        "params": {},
    },
}


def make_http_request(
    method: str, url: str, headers: Dict[str, str], payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    通用 HTTP 请求函数
    """
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=payload)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, data=json.dumps(payload))
        else:
            return {"Error": f"Unsupported HTTP method: {method}"}

        if response.status_code == 200:
            return response.json()
        else:
            return {"Error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"Error": f"Request failed: {str(e)}"}


def execute_tool(tool_name: str, **kwargs: Any) -> Dict[str, Any]:
    """
    执行指定的工具函数，并进行参数检查

    :param tool_name: 要执行的工具函数名称
    :param kwargs: 传递给工具函数的参数
    :return: 工具函数的执行结果或错误信息
    """
    if tool_name not in TOOL_CONFIG:
        return {"Error": f"Tool '{tool_name}' not found"}

    tool_config = TOOL_CONFIG[tool_name]
    expected_params = tool_config["params"]

    # 检查参数数量
    if len(kwargs) != len(expected_params):
        return {
            "Error": f"Incorrect number of parameters for '{tool_name}'. Expected {len(expected_params)}, got {len(kwargs)}"
        }

    # 检查参数类型并构建 payload
    payload = {}
    for param_name, (api_param_name, param_type) in expected_params.items():
        if param_name not in kwargs:
            return {"Error": f"Missing parameter '{param_name}' for '{tool_name}'"}
        if not isinstance(kwargs[param_name], param_type):
            return {
                "Error": f"Incorrect type for parameter '{param_name}' in '{tool_name}'. Expected {param_type.__name__}, got {type(kwargs[param_name]).__name__}"
            }
        payload[api_param_name] = kwargs[param_name]

    # 执行 HTTP 请求
    return make_http_request(
        method=tool_config["method"],
        url=tool_config["url"],
        headers=tool_config["headers"],
        payload=payload,
    )


def execute_action_sequence(action_sequence: List[str]) -> List[Dict[str, Any]]:
    """
    执行一系列动作

    :param action_sequence: 要执行的动作序列
    :return: 每个动作的执行结果列表
    """
    results = []
    for action in action_sequence:
        print(f"Executing action: {action}")
        try:
            # 解析动作字符串，提取工具名称和参数
            tool_name, args_str = action.split("(", 1)
            args_str = args_str.rstrip(")")
            args = [arg.strip() for arg in args_str.split(",") if arg.strip()]

            # 将参数转换为字典
            kwargs = {}
            for arg in args:
                if "=" in arg:
                    key, value = arg.split("=")
                    kwargs[key.strip()] = eval(value.strip())
                else:
                    # 如果没有明确的键值对,假设是按顺序的参数
                    kwargs[f"arg{len(kwargs)}"] = eval(arg.strip())

            # 执行工具函数
            result = execute_tool(tool_name, **kwargs)
        except Exception as e:
            # 捕获所有异常,并将错误信息作为结果
            result = {"Error": f"Action execution failed: {str(e)}"}
        
        results.append({action: result})

    return results


# Example usage
# result = execute_tool(
#     "trade_item",
#     character_id=0,
#     trade_type=2,
#     item_name="apple",
#     item_quantity=1,
#     item_trade_quantity=1,
#     money=2.0,
# )
# result = execute_tool("get_freelance_jobs")
# result = execute_tool("get_public_jobs")

# print(result)
