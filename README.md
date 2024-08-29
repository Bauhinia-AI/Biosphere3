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
