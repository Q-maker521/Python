# Python / FastAPI 学习项目

## 当前状态（2026-11-10）
- 异步工具注册与分发，日志、计时和取消处理。
- inspect.signature().bind() 在执行前检查缺失或多余参数；尚不验证参数值类型。
- 请求模型 ToolRequest 与预览响应模型 ToolPreviewResponse 分离。
- create_app() 为每个应用创建独立的 Semaphore(2)，同一应用的带超时请求共享名额，获得名额后执行超时为 2 秒。
- /tools/execute_with_timeout 覆盖正常 200、参数不匹配 422、未知工具 404、内部执行失败 500、超时 504。
- pytest 参数化覆盖五个功能场景、两轮并发，共 7 项测试。
- function 级 client fixture 每次新建应用，使用 ASGITransport 直接调用应用，无需外部 Uvicorn 服务。
- 普通 /tools/execute 尚未复用上述错误映射、超时与并发限制。
- 已添加 asyncpg 与 SQLAlchemy 异步依赖；数据库连接代码仍为注释草稿，尚未完成连接验证。

## 运行与验证
在项目根目录执行：

```powershell
uv sync
uv run uvicorn demo_fastapi.main:app --reload
```

运行测试无需先启动服务：

```powershell
uv run pytest -v
```

测试断言同时检查 HTTP 状态码和正文。模拟失败和取消日志属于预期场景。
并发耗时仅用于观察，尚未直接测量或断言峰值并发数。
应用工厂隔离应用内信号量；不代表未来的数据库数据也已隔离。

## 下一步
1. 数据库基础：表、主键、SELECT / INSERT / UPDATE / DELETE。
2. 独立验证 PostgreSQL 连接，执行 SELECT 1 并正确关闭连接。
3. 将帖子 CRUD 练习的数据存储从内存列表迁至数据库，验证服务重启后数据仍在。
4. 学习连接池生命周期，并为数据库测试提供独立数据环境。

## 后续完善
- 统一两个执行接口的错误处理，补充响应模型与 OpenAPI 错误响应说明。
- 减少请求处理层重复 JSON 序列化和解析。
- 补充参数值类型验证；内部异常对外返回简短说明，详细原因保留日志。

## Git
.gitignore 排除虚拟环境、缓存、日志和 IDE 文件。
在 VS Code 源代码管理输入框填写提交信息后提交。
