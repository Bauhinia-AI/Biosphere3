# storing different schemas

validators = {
    'npc': {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "userid",
                "username",
                "gender",
                "slogan",
                "description",
                "stats",
                "role",
                "task",
                "created_at",
            ],
            "properties": {
                "userid": {
                    "bsonType": "string",
                    "description": "Agent ID,必须为字符串且为必填项",
                },
                "username": {
                    "bsonType": "string",
                    "description": "NPC 名字,必须为字符串且为必填项",
                },
                "gender": {
                    "bsonType": "string",
                    "description": "NPC 性别,必须为字符串且为必填项",
                },
                "slogan": {
                    "bsonType": "string",
                    "description": "NPC 标语,必须为字符串且为必填项",
                },
                "description": {
                    "bsonType": "string",
                    "description": "NPC 描述,必须为字符串且为必填项",
                },
                "stats": {
                    "bsonType": "object",
                    "required": [
                        "health",
                        "fullness",
                        "energy",
                        "knowledge",
                        "cash",
                    ],
                    "properties": {
                        "health": {"bsonType": "double"},
                        "fullness": {"bsonType": "double"},
                        "energy": {"bsonType": "double"},
                        "knowledge": {"bsonType": "double"},
                        "cash": {"bsonType": "double"},
                    },
                },
                "role": {
                    "bsonType": "string",
                    "description": "NPC 角色,必须为字符串且为必填项",
                },
                "task": {
                    "bsonType": "string",
                    "description": "NPC 任务,必须为字符串且为必填项",
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "创建时间,必须为日期且为必填项",
                },
            },
        }
    },
    'action': {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "userid",
                "timestamp",
                "meta_action",
                "description",
                "response",
                "action_id",
            ],
            "properties": {
                "userid": {
                    "bsonType": "int",
                    "description": "NPC ID,必须为整数且为必填项",
                },
                "timestamp": {
                    "bsonType": "string",
                    "description": "时间戳,必须为字符串且为必填项",
                },
                "meta_action": {
                    "bsonType": "string",
                    "description": "当前做的动作,必须为字符串且为必填项",
                },
                "description": {
                    "bsonType": "string",
                    "description": "大语言模型返回的结果,必须为字符串且为必填项",
                },
                "response": {
                    "bsonType": "bool",
                    "description": "执行是否成功,必须为布尔类型且为必填项",
                },
                "action_id": {
                    "bsonType": "int",
                    "description": "唯一的动作ID,必须为整数且为必填项",
                },
                "prev_action": {
                    "bsonType": "int",
                    "description": "前一个动作的action_id,必须为整数且为可选项",
                },
            },
        }
    },
    # Add other validators similarly...
    'impression': {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["from_id", "to_id", "impression"],
            "properties": {
                "from_id": {
                    "bsonType": "int",
                    "description": "表示印象来源的 NPC 的 ID,必须为整数且为必填项",
                },
                "to_id": {
                    "bsonType": "int",
                    "description": "表示印象指向的 NPC 的 ID,必须为整数且为必填项",
                },
                "impression": {
                    "bsonType": "array",
                    "description": "印象数组,必须为对象数组且为必填项",
                    "items": {
                        "bsonType": "object",
                        "required": ["content", "timestamp"],
                        "properties": {
                            "content": {
                                "bsonType": "string",
                                "description": "印象内容,必须为字符串且为必填项",
                            },
                            "timestamp": {
                                "bsonType": "string",
                                "description": "时间戳,必须为字符串且为必填项",
                            },
                        },
                    },
                },
            },
        }
    },
    # Continue adding other schemas like 'descriptor', 'daily_objective', etc.
}