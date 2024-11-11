# storing different schemas

validators = {
    "agent_profile": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "characterId",
                "characterName",
                "gender",
                "slogan",
                "description",
                "role",
                "task",
                "created_at",
                "updated_at",
                "full_profile",
            ],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "character ID,必须为整数且为必填项",
                },
                "characterName": {
                    "bsonType": "string",
                    "description": "character 名字,必须为字符串且为必填项",
                },
                "gender": {
                    "bsonType": "string",
                    "description": "character 性别,必须为字符串且为必填项",
                },
                "slogan": {
                    "bsonType": "string",
                    "description": "character 标语,必须为字符串且为必填项",
                },
                "description": {
                    "bsonType": "string",
                    "description": "character 描述,必须为字符串且为必填项",
                },
                "role": {
                    "bsonType": "string",
                    "description": "character 角色,必须为字符串且为必填项",
                },
                "task": {
                    "bsonType": "string",
                    "description": "character 任务,必须为字符串且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间,必须为字符串且为必填项",
                },
                "updated_at": {
                    "bsonType": "string",
                    "description": "最后更新时间, 必须为字符串且为必填项",
                },
                "full_profile": {  # 新增字段
                    "bsonType": "string",
                    "description": "完整的个人资料,必须为字符串且为必填项",
                },
            },
        }
    },
    "action": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "characterId",
                "action",
                "result",
                "description",
                "created_at",
            ],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "character ID，必须为整数且为必填项",
                },
                "action": {
                    "bsonType": "string",
                    "description": "当前执行的动作名称，必须为字符串且为必填项",
                },
                "result": {
                    "bsonType": "object",
                    "description": "动作执行的结果对象，可以包含任意内容",
                },
                "description": {
                    "bsonType": "string",
                    "description": "动作执行的描述，必须为字符串且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间,必须为字符串且为必填项",
                },
            },
        }
    },
    "impression": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["from_id", "to_id", "impression", "created_at"],
            "properties": {
                "from_id": {
                    "bsonType": "int",
                    "description": "表示印象来源的 character 的 ID, 必须为整数且为必填项",
                },
                "to_id": {
                    "bsonType": "int",
                    "description": "表示印象指向的 character 的 ID, 必须为整数且为必填项",
                },
                "impression": {
                    "bsonType": "string",
                    "description": "印象内容, 必须为字符串且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "时间戳, 必须为字符串且为必填项",
                },
            },
        }
    },
    "intimacy": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "from_id",
                "to_id",
                "intimacy_level",
                "created_at",
                "updated_at",
            ],
            "properties": {
                "from_id": {
                    "bsonType": "int",
                    "description": "表示亲密度来源的 character 的 ID, 必须为整数且为必填项",
                },
                "to_id": {
                    "bsonType": "int",
                    "description": "表示亲密度指向的 character 的 ID, 必须为整数且为必填项",
                },
                "intimacy_level": {
                    "bsonType": "int",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "亲密度等级, 必须为整数且必须在 0 到 100 之间",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间, 必须为字符串且为必填项",
                },
                "updated_at": {
                    "bsonType": "string",
                    "description": "最后更新时间, 必须为字符串且为必填项",
                },
            },
        }
    },
    "encounter_count": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["from_id", "to_id", "count", "created_at", "updated_at"],
            "properties": {
                "from_id": {
                    "bsonType": "int",
                    "description": "表示相遇来源的 character 的 ID, 必须为整数且为必填项",
                },
                "to_id": {
                    "bsonType": "int",
                    "description": "表示相遇指向的 character 的 ID, 必须为整数且为必填项",
                },
                "count": {
                    "bsonType": "int",
                    "description": "相遇次数, 必须为整数且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间, 必须为字符串且为必填项",
                },
                "updated_at": {
                    "bsonType": "string",
                    "description": "最后更新时间, 必须为字符串且为必填项",
                },
            },
        }
    },
    "cv": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "jobid",
                "characterId",
                "characterName",
                "CV_content",
                "created_at",
            ],
            "properties": {
                "jobid": {
                    "bsonType": "int",
                    "description": "工作ID, 必须为整数且为必填项",
                },
                "characterId": {
                    "bsonType": "int",
                    "description": "用户ID, 必须为整数且为必填项",
                },
                "characterName": {
                    "bsonType": "string",
                    "description": "用户名, 必须为字符串且为必填项",
                },
                "CV_content": {
                    "bsonType": "string",
                    "description": "简历内容, 必须为字符串且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间, 必须为字符串且为必填项",
                },
            },
        }
    },
    "descriptor": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["failed_action", "action_id", "characterId", "reflection"],
            "properties": {
                "failed_action": {
                    "bsonType": "string",
                    "description": "执行失败的动作, 必须为字符串且为必填项",
                },
                "action_id": {
                    "bsonType": "int",
                    "description": "失败动作的ID, 必须为整数且为必填项",
                },
                "characterId": {
                    "bsonType": "int",
                    "description": "character ID, 必须为整数且为必填项",
                },
                "reflection": {
                    "bsonType": "string",
                    "description": "动作失败后的反思, 必须为字符串且为必填项",
                },
            },
        }
    },
    "daily_objective": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["characterId", "created_at", "objectives"],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "用户ID, 必须为整数且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建日期, 必须为字符串且为必填项, 格式为 'YYYY-MM-DD HH:MM:SS'",
                },
                "objectives": {
                    "bsonType": "array",
                    "description": "每日目标列表, 必须为字符串数组且为必填项",
                    "items": {
                        "bsonType": "string",
                        "description": "目标内容, 必须为字符串",
                    },
                },
            },
        }
    },
    "plan": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["characterId", "created_at", "detailed_plan"],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "用户ID, 必须为整数且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建日期, 必须为字符串且为必填项, 格式为 'YYYY-MM-DD HH:MM:SS'",
                },
                "detailed_plan": {
                    "bsonType": "string",
                    "description": "详细计划, 必须为字符串且为必填项",
                },
            },
        }
    },
    "meta_seq": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["characterId", "created_at", "meta_sequence"],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "用户ID, 必须为整数且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建日期, 必须为字符串且为必填项",
                },
                "meta_sequence": {
                    "bsonType": "array",
                    "description": "元动作序列, 必须为字符串数组且为必填项",
                    "items": {
                        "bsonType": "string",
                        "description": "元动作, 必须为字符串",
                    },
                },
            },
        }
    },
    "knowledge": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "characterId",
                "day",
                "environment_information",
                "personal_information",
                "created_at",
            ],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "用户ID, 必须为整数且为必填项",
                },
                "day": {
                    "bsonType": "int",
                    "description": "记录这是哪一天的总结, 必须为整数且为必填项",
                },
                "environment_information": {
                    "bsonType": "string",
                    "description": "环境信息, 短期记忆, 必须为字符串且为必填项",
                },
                "personal_information": {
                    "bsonType": "string",
                    "description": "个人信息, 长期记忆, 必须为字符串且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间, 必须为字符串且为必填项",
                },
            },
        }
    },
    "tool": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["API", "text", "code"],
            "properties": {
                "API": {
                    "bsonType": "string",
                    "description": "API的名称, 必须为字符串且为必填项",
                },
                "text": {
                    "bsonType": "string",
                    "description": "工具的描述文本, 必须为字符串且为必填项",
                },
                "code": {
                    "bsonType": "string",
                    "description": "工具的代码段, 必须为字符串且为必填项",
                },
            },
        }
    },
    "conversation": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "characterIds",
                "start_day",
                "start_time",
                "dialogue",
                "created_at",
            ],
            "properties": {
                "characterIds": {
                    "bsonType": "array",
                    "description": "包含参与对话的character ID的数组, 必须为整数数组且为必填项",
                    "items": {
                        "bsonType": "int",
                        "description": "character的ID, 必须为整数",
                    },
                },
                "start_day": {
                    "bsonType": "int",
                    "description": "对话开始的天数, 必须为整数且为必填项",
                },
                "start_time": {
                    "bsonType": "string",
                    "description": "对话开始的时间, 必须为字符串且为必填项, 格式为 'HH:MM:SS'",
                },
                "dialogue": {
                    "bsonType": "array",
                    "description": "对话内容, 必须为对象数组且为必填项",
                    "items": {
                        "bsonType": "object",
                        "description": "对话中的单个发言",
                        "additionalProperties": {
                            "bsonType": "string",
                            "description": "发言内容, 必须为字符串",
                        },
                    },
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间, 必须为字符串且为必填项",
                },
            },
        }
    },
    "diary": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["characterId", "diary_content", "created_at"],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "用户ID, 必须为整数且为必填项",
                },
                "diary_content": {
                    "bsonType": "string",
                    "description": "日记内容, 必须为字符串且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间, 必须为字符串且为必填项",
                },
            },
        }
    },
    "character_arc": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["characterId", "category", "created_at"],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "角色ID, 必须为整数且为必填项",
                },
                "category": {
                    "bsonType": "array",
                    "description": "角色弧光的类别列表, 必须为对象数组且为必填项",
                    "items": {
                        "bsonType": "object",
                        "required": ["item", "origin_value"],
                        "properties": {
                            "item": {
                                "bsonType": "string",
                                "description": "类别项, 必须为字符串",
                            },
                            "origin_value": {
                                "bsonType": "string",
                                "description": "原始值, 必须为字符串",
                            },
                        },
                    },
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间, 必须为字符串且为必填项",
                },
            },
        }
    },
    "character_arc_change": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "characterId",
                "item",
                "cause",
                "context",
                "change",
                "created_at",
            ],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "角色ID, 必须为整数且为必填项",
                },
                "item": {
                    "bsonType": "string",
                    "description": "类别项, 必须为字符串且为必填项",
                },
                "cause": {
                    "bsonType": "string",
                    "description": "变化原因, 必须为字符串且为必填项",
                },
                "context": {
                    "bsonType": "string",
                    "description": "变化发生的背景, 必须为字符串且为必填项",
                },
                "change": {
                    "bsonType": "string",
                    "description": "情绪的变化, 必须为字符串且为必填项",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间, 必须为字符串且为必填项",
                },
            },
        }
    },
}
