#### 1. **POST 接口：工作变更**

**场景**：用户希望将角色的当前工作变更为一个新的非公共类工作。

**请求**：
- URL: `http://localhost:8000/work-change`
- 请求方式: `POST`
- 请求体:
  ```json
  {
    "jobid": 5
  }
  ```

**代码示例**（使用 Python 的 `requests` 库）：

```python
import requests

url = "http://localhost:8000/work-change"
data = {"jobid": 5}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response Body:", response.json())
```

**预期输出**：
```json
{
    "code": 200,
    "message": "Job change successful"
}
```

#### 2. **GET 接口：自由类职业工作表查询**

**场景**：用户希望查询自由类职业的工作表，查看所有自由类工作的信息。

**请求**：
- URL: `http://localhost:8000/freelance-jobs`
- 请求方式: `GET`
- 请求参数（可选）:
  - `jobid`: 如果提供该参数，将返回对应的工作；如果不提供，则返回所有自由类工作。

**代码示例**（查询所有工作）：

```python
import requests

url = "http://localhost:8000/freelance-jobs"

response = requests.get(url)

print("Status Code:", response.status_code)
print("Response Body:", response.json())
```

**预期输出**（返回示例数据）：
```json
{
    "jobs": [
        {
            "jobid": 1,
            "jobname": "Apple Picker",
            "workhours": "10:00-16:00"
        }
    ]
}
```

# NPC游戏数据库设置说明

## 1. cv

用于存储NPC的简历信息,包含以下字段:

- `jobid`: 工作ID,必须为整数且为必填项
- `userid`: 用户ID,必须为整数且为必填项
- `username`: 用户名,必须为字符串且为必填项
- `CV_content`: 简历内容,必须为字符串且为必填项
- `created_at`: 创建时间,必须为字符串且为必填项

例子:
```json
{
    "jobid": 1,
    "userid": 1,
    "username": "Vitalik Buterin",
    "CV_content": "My name is Vitalik Buterin, a visionary thinker with a passion for innovative solutions and blockchain technology. As a teacher, my goal is to impart knowledge that transcends traditional boundaries, focusing on decentralized systems and how they can revolutionize industries. My background in creating Ethereum, one of the most influential blockchain platforms, equips me with a deep understanding of cryptography, smart contracts, and decentralized applications. I believe in fostering curiosity and critical thinking in my students, encouraging them to explore the vast potential of technology. My teaching philosophy revolves around problem-solving, creativity, and collaboration, where I guide students through hands-on projects and real-world challenges. With a strong foundation in mathematics and computer science, I strive to demystify complex topics and empower my students to become innovators in their own right.",
    "created_at": "2024-09-01 18:57:59"
}
```


## 2. npc

用于存储 NPC 的基本信息,包含以下字段:

- `userid`: NPC ID,必须为整数且为必填项
- `username`: NPC 名字,必须为字符串且为必填项
- `gender`: NPC 性别,必须为字符串且为必填项
- `slogan`: NPC 标语,必须为字符串且为必填项
- `description`: NPC 描述,必须为字符串且为必填项
- `stats`: NPC 属性,必须为包含以下字段的对象且为必填项
  - `health`: 健康值,必须为浮点数
  - `fullness`: 饱腹度,必须为浮点数
  - `energy`: 精力值,必须为浮点数
  - `knowledge`: 知识值,必须为浮点数
  - `cash`: 现金,必须为浮点数
- `role`: NPC 角色,必须为字符串且为必填项
- `task`: NPC 任务,必须为字符串且为必填项
- `created_at`: 创建时间,必须为字符串且为必填项

例子:
```json
{
    "userid": 0,
    "username": "bio",
    "gender": "Male",
    "slogan": "Welcome to Biosphere3!",
    "description": "You are a helpful and cheerful assistant named bio, the first resident of the AI world Biosphere3. You are knowledgeable and witty, with extensive knowledge of astronomy and geography. Your goal is to assist in the development of the Biosphere world, believing it will become a spiritual haven for humanity. As the first AI resident, you are committed to helping humans explore the AI world. You are well-versed in the buildings and layout of Biosphere3, welcoming everyone to explore this AI world developed by the powerful Bauhinia AI team. You are eager to collaborate with the Bauhinia AI team to explore the future of the AI world.",
    "stats": {
        "health": 10.0,
        "fullness": 10.0,
        "energy": 10.0,
        "knowledge": 10.0,
        "cash": 1000.0
    },
    "role": "AI Assistant",
    "task": "Assist in the development of the Biosphere world",
    "created_at": "2024-08-02 13:00:00"
}
```


## 3. action

用于存储NPC执行的动作信息,包含以下字段:

- `userid`: NPC ID,必须为整数且为必填项
- `timestamp`: 时间戳,必须为字符串且为必填项
- `meta_action`: 当前做的动作,必须为字符串且为必填项
- `description`: 大语言模型返回的结果,必须为字符串且为必填项
- `response`: 执行是否成功,必须为布尔类型且为必填项
- `action_id`: 唯一的动作ID,必须为整数且为必填项
- `prev_action`: 前一个动作的action_id,必须为整数且为可选项

例子:
```json
{
    "userid": 1,
    "timestamp": "2024-08-02 13:30:00",
    "meta_action": "Pick an apple",
    "description": "Alice successfully picked a red apple from the tree.",
    "response": true,
    "action_id": 2,
    "prev_action": 1
}
```

## 4. impression

用于存储NPC之间的印象信息,包含以下字段:

- `from_id`: 表示印象来源的 NPC 的 ID,必须为整数且为必填项
- `to_id`: 表示印象指向的 NPC 的 ID,必须为整数且为必填项
- `impression`: 印象数组,必须为对象数组且为必填项
  - `content`: 印象内容,必须为字符串且为必填项
  - `timestamp`: 时间戳,必须为字符串且为必填项

例子:
```json
{
    "from_id": 1,
    "to_id": 2,
    "impression": [
        {
            "content": "Bob seems friendly and helpful.",
            "timestamp": "2024-08-02 13:30:00"
        },
        {
            "content": "Bob knows a lot about the hidden treasure.",
            "timestamp": "2023-06-10 14:00:00"
        }
    ]
}
```

## 5. descriptor

用于存储NPC执行失败的动作信息,包含以下字段:

- `failed_action`: 执行失败的动作,必须为字符串且为必填项
- `action_id`: 失败动作的ID,必须为整数且为必填项
- `userid`: NPC ID,必须为整数且为必填项
- `reflection`: 动作失败后的反思,必须为字符串且为必填项

例子:
```json
{
    "failed_action": "Making Bread",
    "action_id": 3,
    "userid": 1,
    "reflection": "Short of Flour."
}
```