# 阶段三单词管理 API 记录

## 1. 完成时间

2026-04-21

## 2. 已实现接口

- `GET /api/words`
- `POST /api/words`
- `GET /api/words/{word_id}`
- `PUT /api/words/{word_id}`
- `DELETE /api/words/{word_id}`

API 说明已更新：[API说明文档.md](API说明文档.md)

---

## 3. 实现文件

- [backend/app/api/routes/words.py](backend/app/api/routes/words.py)
- [backend/app/schemas/word.py](backend/app/schemas/word.py)
- [backend/app/services/word_service.py](backend/app/services/word_service.py)
- [backend/app/repositories/word_repository.py](backend/app/repositories/word_repository.py)
- [backend/app/services/errors.py](backend/app/services/errors.py)

---

## 4. 当前规则

新增和编辑单词时，提交完整结构：

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

编辑接口采用整体替换方式：

- 更新 `word.spelling`
- 删除原有 `meaning`
- 删除原有 `word_sense`
- 重新插入新的 `word_sense`
- 重新插入新的 `meaning`
- 保留已有 `review_state`

删除接口会按顺序删除：

- `meaning`
- `word_sense`
- `review_state`
- `word`

---

## 5. 验证结果

已通过自动化测试：

```text
4 passed
```

Lint 结果：

```text
All checks passed
```

已使用真实开发数据库完成一轮接口验证：

- `POST /api/words`：`201`
- `GET /api/words`：`200`
- `GET /api/words/{word_id}`：`200`
- `PUT /api/words/{word_id}`：`200`
- `DELETE /api/words/{word_id}`：`204`
- 删除后再次 `GET /api/words/{word_id}`：`404`

---

## 6. 服务状态

本地后端服务已重启，当前 OpenAPI 已包含：

- `/api/words`
- `/api/words/{word_id}`
- `/health`
- `/health/db`

访问地址：

```text
http://127.0.0.1:8000/docs
```

---

## 7. 阶段三结论

阶段三已完成。下一步可以进入阶段四：背诵与复习 API。
