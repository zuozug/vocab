# API 说明文档

## 1. 当前状态

当前后端已实现基础健康检查接口、单词管理接口和背诵复习接口。

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
| 学习会话 | `GET` | `/api/study-sessions` | 查询学习历史列表 |
| 学习会话 | `POST` | `/api/study-sessions` | 创建学习会话 |
| 学习会话 | `GET` | `/api/study-sessions/{session_id}` | 查询学习会话详情 |
| 学习会话 | `POST` | `/api/study-sessions/{session_id}/finish` | 结束学习会话 |
| 背诵复习 | `GET` | `/api/reviews/next` | 获取待复习单词 |
| 背诵复习 | `POST` | `/api/reviews/answer` | 提交答案并更新复习状态 |

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

## 7. 学习会话 API

### 7.1 查询学习历史列表

```http
GET /api/study-sessions?limit=50&offset=0
```

查询参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `limit` | integer | 否 | `50` | 每页数量，范围 `1` 到 `100` |
| `offset` | integer | 否 | `0` | 分页偏移量，最小 `0` |

排序规则：

- 按 `coalesce(ended_at, started_at)` 倒序。
- 时间相同时按 `id` 倒序。

成功响应：

状态码：`200`

```json
{
  "items": [
    {
      "id": 1,
      "started_at": "2026-04-22T10:00:00Z",
      "ended_at": "2026-04-22T10:08:30Z",
      "reviewed_word_count": 10,
      "duration_seconds": 510
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### 7.2 创建学习会话

```http
POST /api/study-sessions
```

成功响应：

状态码：`201`

```json
{
  "id": 1,
  "started_at": "2026-04-22T10:00:00Z",
  "ended_at": null,
  "reviewed_word_count": 0,
  "duration_seconds": null
}
```

### 7.3 查询学习会话详情

```http
GET /api/study-sessions/{session_id}
```

成功响应：

状态码：`200`

```json
{
  "id": 1,
  "started_at": "2026-04-22T10:00:00Z",
  "ended_at": "2026-04-22T10:08:30Z",
  "reviewed_word_count": 10,
  "duration_seconds": 510
}
```

失败响应：

状态码：`404`

```json
{
  "detail": "Study session not found."
}
```

### 7.4 结束学习会话

```http
POST /api/study-sessions/{session_id}/finish
```

请求体：

```json
{
  "reviewed_word_count": 10
}
```

成功响应：

状态码：`200`

```json
{
  "id": 1,
  "started_at": "2026-04-22T10:00:00Z",
  "ended_at": "2026-04-22T10:08:30Z",
  "reviewed_word_count": 10,
  "duration_seconds": 510
}
```

失败响应：

状态码：`404`

```json
{
  "detail": "Study session not found."
}
```

---

## 8. 背诵复习 API

### 8.1 获取待复习单词

```http
GET /api/reviews/next?mode=zh_to_en&limit=10
```

查询参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `mode` | string | 否 | `zh_to_en` | 背诵模式，可选 `zh_to_en`、`en_to_zh` |
| `limit` | integer | 否 | `10` | 返回数量，范围 `1` 到 `100` |

获取队列前，系统会先自动应用未复习熟练度衰减。V1 规则为每满 `1` 天未复习降低 `1` 级，最低为 `0`，并通过 `last_decay_applied_at` 避免重复扣减。

成功响应：

状态码：`200`

```json
{
  "mode": "zh_to_en",
  "items": [
    {
      "word_id": 1,
      "spelling": "record",
      "meanings": [
        {
          "id": 1,
          "part_of_speech": "n",
          "definition": "记录"
        }
      ],
      "proficiency": 0,
      "last_reviewed_at": "2026-04-22T10:00:00Z"
    }
  ]
}
```

### 8.2 提交答案

```http
POST /api/reviews/answer
```

请求体：

```json
{
  "word_id": 1,
  "mode": "zh_to_en",
  "answer": "record"
}
```

判断规则：

- `zh_to_en`：答案去除首尾空格后，与 `word.spelling` 比较，忽略大小写。
- `en_to_zh`：答案去除首尾空格后，按空格拆分为词性和释义 token。
- `en_to_zh` 输入只包含词性、释义和空格；每个释义归属于它之前最近一次出现的词性。
- `en_to_zh` 必须匹配该单词所有 `(part_of_speech, meaning.definition)` 项，顺序不重要。
- `en_to_zh` 不能少写释义、不能多写释义，也不能写错词性。

英文到中文示例：

```json
{
  "word_id": 1,
  "mode": "en_to_zh",
  "answer": "n 记录 v 记录 n 猫 狗"
}
```

上例表示三个 `n` 释义：`记录`、`猫`、`狗`，以及一个 `v` 释义：`记录`。

复习状态更新规则：

- 答对：`proficiency = proficiency + 1`，并更新 `last_reviewed_at = now()`。
- 答错：`proficiency = greatest(proficiency - 2, 0)`，并更新 `last_reviewed_at = now()`。
- 每次答题后同步更新 `last_decay_applied_at = now()`。

成功响应：

状态码：`200`

```json
{
  "word_id": 1,
  "mode": "zh_to_en",
  "is_correct": true,
  "correct_answers": ["record"],
  "proficiency": 1,
  "last_reviewed_at": "2026-04-22T10:01:00Z"
}
```

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
