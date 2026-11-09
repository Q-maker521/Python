# Python / FastAPI 学习项目

## 当前状态（2026-11-09）
- 异步工具注册与分发，日志、计时和取消处理。
- inspect.signature().bind() 在执行前检查缺失或多余参数；不验证参数值类型。
- 请求模型 ToolRequest 与预览响应模型 ToolPreviewResponse 分离。
- 带超时接口共享 Semaphore(2)，获得名额后执行超时为 2 秒。
- /tools/execute_with_timeout 已验证：正常 200、参数不匹配 422、未知工具 404、内部执行失败 500、超时 504。
- 五场景串行回归及五请求并发断言已实现；并发四成功、一超时，用户验证约 3.063 秒。
- 当前普通 /tools/execute 接口尚未复用上述错误映射、超时与并发限制。

## 运行与验证
在项目根目录使用已安装项目依赖的虚拟环境：

```powershell
python -m uvicorn demo_fastapi.main:app --reload
```

保持服务运行，在另一终端分别执行：

```powershell
python demo_fastapi/test_http_errors.py
python demo_fastapi/test_http_concurrency.py
```

测试包含预期的 4xx/5xx，服务日志中的模拟失败与取消不代表测试失败。
测试断言同时检查状态码和正文；耗时仅用于观察，不严格断言峰值并发。

## 下一步
1. 学习 pytest，将独立场景整理为测试用例。
2. 统一两个执行接口的错误处理，补充响应模型与 OpenAPI 错误响应说明。
3. 减少请求处理层重复 JSON 序列化和解析。
4. 后续完善参数值类型验证；内部异常对外返回简短说明，详细原因保留日志。

## Git
.gitignore 排除虚拟环境、缓存、日志和 IDE 文件。
在 VS Code 源代码管理输入框填写提交信息后提交。
