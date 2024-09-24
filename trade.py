#post
import requests
import json

def trade_item(character_id, trade_type, item_name, item_quantity, item_trade_quantity, money):
    url = "http://47.95.21.135:8082/ammPool/trade"
    
    payload = {
        "characterId": character_id,
        "tradeType": trade_type,
        "itemName": item_name,
        "itemQuantity": item_quantity,
        "itemTradeQuantity": item_trade_quantity,
        "money": money
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Example usage
result = trade_item(0, 2, "apple", 1, 1, 2)
print(result)
