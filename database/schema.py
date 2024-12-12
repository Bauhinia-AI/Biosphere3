# storing different schemas

validators = {
    "agent_profile": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "characterId",
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
                    "bsonType": ["string", "null"],
                    "description": "character 名字,必须为字符串",
                },
                "gender": {
                    "bsonType": ["string", "null"],
                    "description": "character 性别,必须为字符串",
                },
                "spriteId": {  # 新增字段
                    "bsonType": "int",
                    "description": "agent 样貌, 必须为整数",
                },
                "relationship": {
                    "bsonType": ["string", "null"],
                    "description": "与玩家的关系",
                },
                "personality": {
                    "bsonType": ["string", "null"],
                    "description": "性格描述",
                },
                "long_term_goal": {
                    "bsonType": ["string", "null"],
                    "description": "长期目标",
                },
                "short_term_goal": {
                    "bsonType": ["string", "null"],
                    "description": "短期目标",
                },
                "language_style": {
                    "bsonType": ["string", "null"],
                    "description": "语言风格",
                },
                "biography": {"bsonType": ["string", "null"], "description": "简介"},
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间,必须为字符串且为必填项",
                },
                "updated_at": {
                    "bsonType": "string",
                    "description": "最后更新时间, 必须为字符串且为必填项",
                },
                "full_profile": {
                    "bsonType": "string",
                    "description": "完整的个人资料,必须为字符串",
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
                "to_id_name",  # 新增字段
                "to_id_spriteId",  # 新增字段
                "relationship",  # 新增字段
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
                "to_id_name": {  # 新增字段
                    "bsonType": "string",
                    "description": "指向角色的名字, 必须为字符串",
                },
                "to_id_spriteId": {  # 新增字段
                    "bsonType": "int",
                    "description": "指向角色的样貌ID, 必须为整数",
                },
                "relationship": {  # 新增字段
                    "bsonType": "string",
                    "description": "与指向角色的关系, 必须为字符串",
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
            "required": ["jobid", "characterId", "CV_content", "week"],
            "properties": {
                "jobid": {
                    "bsonType": "int",
                    "description": "工作ID, 必须为整数且为必填项",
                },
                "characterId": {
                    "bsonType": "int",
                    "description": "用户ID, 必须为整数且为必填项",
                },
                "CV_content": {
                    "bsonType": "string",
                    "description": "简历内容, 必须为字符串且为必填项",
                },
                "created_at": {
                    "bsonType": ["string", "null"],
                    "description": "创建时间, 必须为字符串且为必填项",
                },
                "week": {
                    "bsonType": "int",
                    "description": "周数, 必须为整数且为必填项",
                },
                "election_status": {
                    "bsonType": ["string", "null"],
                    "enum": ["not_yet", "failed", "succeeded"],
                    "description": "选举状态, 可以为 'not_yet'（未进行选举）、'failed'（选举失败）、'succeeded'（选举成功）",
                },
                "health": {
                    "bsonType": ["int", "null"],
                    "description": "健康值, 必须为整数且为必填项",
                },
                "studyxp": {
                    "bsonType": ["int", "null"],
                    "description": "学习经验值, 必须为整数且为必填项",
                },
                "date": {
                    "bsonType": ["int", "null"],
                    "description": "游戏中的日期数, 必须为整数且为必填项",
                },
                "experience": {
                    "bsonType": ["array", "null"],
                    "description": "经验列表, 必须为字符串数组且为必填项",
                    "items": {
                        "bsonType": "string",
                        "description": "经验内容, 必须为字符串",
                    },
                },
                "jobName": {
                    "bsonType": ["string", "null"],
                    "description": "工作名称, 必须为字符串且为必填项",
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
    "profile_sample": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "relationship",
                "personality",
                "long_term_goal",
                "short_term_goal",
                "language_style",
                "biography",
            ],
            "properties": {
                "relationship": {
                    "bsonType": "array",
                    "description": "关系列表, 必须为字符串数组且为必填项",
                    "items": {
                        "bsonType": "string",
                        "description": "与用户的关系, 必须为字符串",
                    },
                },
                "personality": {
                    "bsonType": "array",
                    "description": "性格特征列表, 必须为字符串数组且为必填项",
                    "items": {
                        "bsonType": "string",
                        "description": "性格特征, 必须为字符串",
                    },
                },
                "long_term_goal": {
                    "bsonType": "array",
                    "description": "长期目标列表, 必须为字符串数组且为必填项",
                    "items": {
                        "bsonType": "string",
                        "description": "长期目标, 必须为字符串",
                    },
                },
                "short_term_goal": {
                    "bsonType": "array",
                    "description": "短期目标列表, 必须为字符串数组且为必填项",
                    "items": {
                        "bsonType": "string",
                        "description": "短期目标, 必须为字符串",
                    },
                },
                "language_style": {
                    "bsonType": "array",
                    "description": "语言风格列表, 必须为字符串数组且为必填项",
                    "items": {
                        "bsonType": "string",
                        "description": "语言风格, 必须为字符串",
                    },
                },
                "biography": {
                    "bsonType": "array",
                    "description": "简介列表, 必须为字符串数组且为必填项",
                    "items": {
                        "bsonType": "string",
                        "description": "简介, 必须为字符串",
                    },
                },
            },
        }
    },
    "agent_prompt": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["characterId"],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "角色ID, 必须为整数且为必填项",
                },
                "daily_goal": {
                    "bsonType": "string",
                    "description": "玩家通过字符串调整的日常目标",
                },
                "refer_to_previous": {
                    "bsonType": "bool",
                    "description": "是否参考过去的日常目标",
                },
                "life_style": {
                    "bsonType": "string",
                    "enum": ["Busy", "Moderate", "Casual"],
                    "description": "调整生活风格, 可选项有Busy, Moderate, Casual",
                },
                "daily_objective_ar": {
                    "bsonType": "string",
                    "description": "一些补充信息，字符串内容",
                },
                "task_priority": {
                    "bsonType": "array",
                    "description": "任务优先级列表, 按重要度排序",
                    "items": {
                        "bsonType": "string",
                        "description": "任务名称",
                    },
                },
                "max_actions": {
                    "bsonType": "int",
                    "description": "允许规划的最大meta action数",
                },
                "meta_seq_ar": {
                    "bsonType": "string",
                    "description": "一些补充信息，字符串内容",
                },
                "replan_time_limit": {
                    "bsonType": "int",
                    "description": "重新规划的次数限制",
                },
                "meta_seq_adjuster_ar": {
                    "bsonType": "string",
                    "description": "一些补充信息，字符串内容",
                },
                "focus_topic": {
                    "bsonType": "array",
                    "description": "重点关注的话题, 按重要度排序",
                    "items": {
                        "bsonType": "string",
                        "description": "话题名称",
                    },
                },
                "depth_of_reflection": {
                    "bsonType": "string",
                    "enum": ["Deep", "Moderate", "Shallow"],
                    "description": "反思的深度, 可选项有Deep, Moderate, Shallow",
                },
                "reflection_ar": {
                    "bsonType": "string",
                    "description": "一些补充信息，字符串内容",
                },
                "level_of_detail": {
                    "bsonType": "string",
                    "enum": ["Deep", "Moderate", "Shallow"],
                    "description": "对于细节的关注, 可选项有Deep, Moderate, Shallow",
                },
                "tone_and_style": {
                    "bsonType": "string",
                    "enum": ["Formal", "Moderate", "Gentle"],
                    "description": "描述时语言的语气和风格, 可选项有Formal, Moderate, Gentle",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间,必须为字符串且为必填项",
                },
                "updated_at": {
                    "bsonType": "string",
                    "description": "最后更新时间, 必须为字符串且为必填项",
                },
            },
        }
    },
    "conversation_prompt": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["characterId"],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "角色ID, 必须为整数且为必填项",
                },
                "topic_requirements": {
                    "bsonType": ["string", "null"],
                    "description": "玩家对于对话主题的额外要求",
                },
                "relation": {
                    "bsonType": ["string", "null"],
                    "description": "如何看待其他agent",
                },
                "emotion": {
                    "bsonType": ["string", "null"],
                    "description": "情绪影响对话语气",
                },
                "personality": {
                    "bsonType": ["string", "null"],
                    "enum": ["Introversion", "Extraversion"],
                    "description": "影响对话长度和轮次数，可选项有Introversion，Extraversion",
                },
                "habits_and_preferences": {
                    "bsonType": ["string", "null"],
                    "description": "愿意和其他人分享的兴趣爱好",
                },
                "created_at": {
                    "bsonType": "string",
                    "description": "创建时间,必须为字符串且为必填项",
                },
                "updated_at": {
                    "bsonType": "string",
                    "description": "最后更新时间, 必须为字符串且为必填项",
                },
            },
        }
    },
    "decision": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["characterId"],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "角色ID, 必须为整数且为必填项",
                },
                "need_replan": {"bsonType": "bool", "description": "是否需要重新规划"},
                "action_description": {
                    "bsonType": "array",
                    "description": "动作描述列表",
                    "items": {
                        "bsonType": "string",
                        "description": "动作描述, 必须为字符串",
                    },
                },
                "action_result": {
                    "bsonType": "array",
                    "description": "动作结果列表",
                    "items": {
                        "bsonType": "string",
                        "description": "动作结果, 必须为字符串",
                    },
                },
                "new_plan": {
                    "bsonType": "array",
                    "description": "新计划列表",
                    "items": {
                        "bsonType": "string",
                        "description": "计划内容, 必须为字符串",
                    },
                },
                "daily_objective": {
                    "bsonType": "array",
                    "description": "每日目标列表",
                    "items": {
                        "bsonType": "string",
                        "description": "目标内容, 必须为字符串",
                    },
                },
                "meta_seq": {
                    "bsonType": "array",
                    "description": "元动作序列",
                    "items": {
                        "bsonType": "string",
                        "description": "元动作, 必须为字符串",
                    },
                },
                "reflection": {
                    "bsonType": "array",
                    "description": "反思列表",
                    "items": {
                        "bsonType": "string",
                        "description": "反思内容, 必须为字符串",
                    },
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
        },
    },
    "current_pointer": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["characterId", "current_pointer"],
            "properties": {
                "characterId": {
                    "bsonType": "int",
                    "description": "角色ID, 必须为整数且为必填项",
                },
                "current_pointer": {
                    "bsonType": "string",
                    "description": "当前指针, 必须为字符串",
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
}
