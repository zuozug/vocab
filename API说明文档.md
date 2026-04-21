# API 说明文档

## 1. 当前状态

当前后端已实现基础健康检查接口和单词管理接口。

后端技术栈：

- FastAPI
- PostgreSQL
- psycopg

本地开发默认地址：

```text
http://127.0.0.1:8000
```

FastAPI 自动文档：

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

---

## 2. 通用说明

### 2.1 请求格式

写入接口使用 JSON 请求体。

请求头示例：

```http
Content-Type: application/json
```

### 2.2 响应格式

接口默认返回 JSON。

### 2.3 认证

当前阶段未实现登录和鉴权。

### 2.4 错误格式

FastAPI 默认错误响应格式：

```json
{
  "detail": "错误信息"
}
```

---

## 3. 接口总览

| 模块 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| 健康检查 | `GET` | `/health` | 检查 API 服务是否正常 |
| 健康检查 | `GET` | `/health/db` | 检查数据库连接是否正常 |
| 单词管理 | `GET` | `/api/words` | 查询单词列表 |
| 单词管理 | `POST` | `/api/words` | 新增单词 |
| 单词管理 | `GET` | `/api/words/{word_id}` | 查询单词详情 |
| 单词管理 | `PUT` | `/api/words/{word_id}` | 编辑单词 |
| 单词管理 | `DELETE` | `/api/words/{word_id}` | 删除单词 |

---

## 4. 数据结构

### 4.1 词性取值

当前支持以下词性：

- `n`
- `v`
- `adj`
- `adv`
- `prep`
- `pron`
- `conj`
- `interj`
- `num`
- `art`

### 4.2 单词请求结构

新增和编辑单词时，提交完整单词结构。

```json
{
  "spelling": "record",
  "senses": [
    {
      "part_of_speech": "n",
      "meanings": ["记录", "唱片"]
    },
    {
      "part_of_speech": "v",
      "meanings": ["记录", "录制"]
    }
  ]
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `spelling` | string | 是 | 单词拼写，不能为空，最大长度 `128` |
| `senses` | array | 是 | 词性列表，至少一项 |
| `senses[].part_of_speech` | string | 是 | 词性，取值见 `4.1` |
| `senses[].meanings` | array | 是 | 中文释义列表，至少一项 |

校验规则：

- `spelling` 会去除首尾空格。
- `meaning` 会去除首尾空格。
- 同一个单词请求中不能重复提交相同词性。
- 同一个词性下不能重复提交相同释义。

### 4.3 单词响应结构

```json
{
  "id": 1,
  "spelling": "record",
  "senses": [
    {
      "id": 1,
      "part_of_speech": "n",
      "meanings": [
        {
          "id": 1,
          "definition": "记录",
          "created_at": "2026-04-21T17:32:33.437681+08:00",
          "updated_at": "2026-04-21T17:32:33.437681+08:00"
        }
      ],
      "created_at": "2026-04-21T17:32:33.437681+08:00",
      "updated_at": "2026-04-21T17:32:33.437681+08:00"
    }
  ],
  "created_at": "2026-04-21T17:32:33.437681+08:00",
  "updated_at": "2026-04-21T17:32:33.437681+08:00"
}
```

---

## 5. 健康检查接口

### 5.1 API 服务健康检查

检查 FastAPI 服务是否正常运行。

```http
GET /health
```

#### 成功响应

状态码：`200`

```json
{
  "status": "ok",
  "environment": "development"
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | 服务状态 |
| `environment` | string | 当前运行环境，来自 `APP_ENV` 配置 |

---

### 5.2 数据库连接健康检查

检查后端是否可以连接 PostgreSQL。

```http
GET /health/db
```

#### 成功响应

状态码：`200`

```json
{
  "status": "ok",
  "database": "PostgreSQL 17.9 (Debian 17.9-0+deb13u1) ..."
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | 数据库连接状态 |
| `database` | string | PostgreSQL 版本信息 |

#### 失败响应

状态码：`503`

```json
{
  "detail": "Database is unavailable."
}
```

---

## 6. 单词管理接口

### 6.1 查询单词列表

```http
GET /api/words
```

查询参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `keyword` | string | 否 | 无 | 按英文单词模糊查询 |
| `limit` | integer | 否 | `50` | 每页数量，范围 `1` 到 `100` |
| `offset` | integer | 否 | `0` | 偏移量，不能小于 `0` |

请求示例：

```http
GET /api/words?keyword=rec&limit=10&offset=0
```

成功响应：

状态码：`200`

```json
{
  "items": [
    {
      "id": 1,
      "spelling": "record",
      "senses": [],
      "created_at": "2026-04-21T17:32:33.437681+08:00",
      "updated_at": "2026-04-21T17:32:33.437681+08:00"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

说明：实际返回的 `senses` 会包含该单词的词性和释义。

---

### 6.2 新增单词

```http
POST /api/words
```

请求体：

```json
{
  "spelling": "record",
  "senses": [
    {
      "part_of_speech": "n",
      "meanings": ["记录", "唱片"]
    },
    {
      "part_of_speech": "v",
      "meanings": ["记录", "录制"]
    }
  ]
}
```

成功响应：

状态码：`201`

返回新创建的单词详情，结构见 `4.3 单词响应结构`。

失败响应：

单词拼写已存在：

状态码：`409`

```json
{
  "detail": "Word spelling already exists."
}
```

请求体校验失败：

状态码：`422`

---

### 6.3 查询单词详情

```http
GET /api/words/{word_id}
```

路径参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `word_id` | integer | 单词 ID |

成功响应：

状态码：`200`

返回单词详情，结构见 `4.3 单词响应结构`。

失败响应：

状态码：`404`

```json
{
  "detail": "Word not found."
}
```

---

### 6.4 编辑单词

```http
PUT /api/words/{word_id}
```

编辑接口采用整体替换方式：提交新的 `spelling` 和完整 `senses` 结构，后端会替换该单词原有词性和释义。

路径参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `word_id` | integer | 单词 ID |

请求体：

```json
{
  "spelling": "record",
  "senses": [
    {
      "part_of_speech": "n",
      "meanings": ["记录", "唱片", "档案"]
    }
  ]
}
```

成功响应：

状态码：`200`

返回更新后的单词详情，结构见 `4.3 单词响应结构`。

失败响应：

单词不存在：

状态码：`404`

```json
{
  "detail": "Word not found."
}
```

单词拼写与其他单词冲突：

状态码：`409`

```json
{
  "detail": "Word spelling already exists."
}
```

请求体校验失败：

状态码：`422`

---

### 6.5 删除单词

```http
DELETE /api/words/{word_id}
```

删除时会按顺序删除该单词关联的：

- `meaning`
- `word_sense`
- `review_state`
- `word`

路径参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `word_id` | integer | 单词 ID |

成功响应：

状态码：`204`

无响应体。

失败响应：

状态码：`404`

```json
{
  "detail": "Word not found."
}
```
