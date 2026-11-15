# Python / FastAPI 学习项目

## 当前进度（2026-11-15）
沿原课程学习后端开发，完成课程后再调整业务场景。

- 异步工具分发、日志、计时、超时和并发限制。
- FastAPI 应用工厂与 lifespan 数据库连接池管理。
- PostgreSQL 用户创建、删除及关联帖子 CRUD。
- 创建帖子先验证作者；更新帖子不修改作者。
- 重复邮箱/用户名映射为 409，不存在的作者返回 404。
- 10 项测试：2 项工具并发、5 项工具错误/成功场景、帖子 CRUD、重复邮箱、无效作者。
- 最近连续两轮通过：10 passed（8.91 秒、9.06 秒）。

## 启动
1. 安装依赖：`uv sync`。
2. 复制 `.env.example` 为 `.env`，填写本地连接信息，勿提交真实凭据。
3. 准备开发库 `fastapi` 和测试库 `fastapi_test`。
4. 仅在空库分别执行 `migrations/0001_users_posts_baseline.sql`；已有库先核对结构，不要重复执行或清空数据。
5. 运行 `uv run uvicorn demo_fastapi.main:app --reload`，访问 `/docs`。

## 代码结构
- `demo_fastapi/main.py`：应用工厂、工具接口、路由注册。
- `demo_fastapi/database.py`：读取配置、连接检查、连接池释放。
- `demo_fastapi/schemas.py`：请求与工具预览模型。
- `demo_fastapi/users.py`：用户创建、删除及临时用户查询演示。
- `demo_fastapi/posts.py`：帖子增删改查。
- `demo_fastapi/test/`：ASGI 进程内接口测试。
- `async_demo/`：工具执行、参数绑定、日志与超时练习。

## 接口
| 方法 | 路径 | 用途 |
|---|---|---|
| POST | /users/register | 创建用户，201 |
| DELETE | /users/{user_id} | 删除用户，204；应先删除关联帖子 |
| POST | /users/login | 临时用户名、邮箱查询；不是真实认证 |
| POST | /posts | 创建帖子，201 |
| GET | /posts | 帖子列表 |
| GET / PUT / DELETE | /posts/{post_id} | 查询、更新、删除 |
| POST | /tools/preview | 请求预览 |
| POST | /tools/execute_with_timeout | 带超时、错误映射和并发限制的工具执行 |

## 测试与全流程
运行 `uv run pytest -v`，无需另启 Uvicorn，但需要可连接的 PostgreSQL 测试库。

准备顺序：client 创建应用并启动 lifespan → test_user 创建唯一用户 → test_post 创建关联帖子 → 执行测试。
清理顺序：删除帖子 → 删除用户 → 关闭客户端 → 释放连接池。

`yield` 前是准备，之后是清理。测试断言失败仍会触发已准备完成的 fixture 清理；fixture 在 yield 前失败时，不执行其自身 yield 后的清理。

请求流程：JSON → 模型校验 → 路由 → 数据库事务 → SQL → 提交 → HTTP 响应。
`engine.begin()` 正常退出自动提交，异常退出自动回滚。创建帖子在同一事务内锁定作者行再插入，防止并发删除作者。

测试使用独立应用实例、共享 fastapi_test 数据库和显式清理，并非事务回滚隔离。唯一测试标识用于避免历史数据冲突，不能替代清理。不会自动删除历史残留。

## 已知限制与下一步
- 下一步跟课程学习密码哈希、登录、JWT 和作者权限。
- 当前没有真实认证或权限控制；user_id 暂由请求传入。
- 删除仍有帖子的用户尚未转换外键错误为友好 HTTP 响应。
- 邮箱格式、纯空白字符串校验、帖子响应模型和分页待完善。
- 用户名唯一约束错误目前按已知约束名识别，尚无单独回归用例。
- 普通 /tools/execute 尚未统一超时接口的错误映射和并发限制。
- 未直接测量峰值并发；尚未采用数据库迁移管理工具。

## 提交说明
.env、缓存、日志、本地数据库备份 sql_compare/ 和一次性维护脚本 db_ops/ 已忽略。
提交前运行 `git diff --check` 和测试，审阅 `git status --short`。
