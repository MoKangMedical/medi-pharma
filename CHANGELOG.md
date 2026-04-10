# Changelog

All notable changes to MediPharma will be documented in this file.

## [2.0.0] - 2026-04-10

### Added
- **10个REST API端点**：靶点发现/虚拟筛选/分子生成/ADMET预测/先导优化/知识引擎/全流水线
- **18个核心测试**：API端点+引擎模块全覆盖
- **Docker部署**：Dockerfile + docker-compose.yml
- **pyproject.toml**：现代Python打包配置
- **相对导入修复**：lead_optimization/engine.py, backend/api.py, orchestrator/pipeline.py
- **7大模块**：靶点发现/虚拟筛选/分子生成/ADMET/先导优化/知识引擎/Agent编排
- **35个文件**：完整代码+文档+示例

### Changed
- 版本号统一为 v2.0.0
- 修复相对导入问题（..admet_prediction → admet_prediction）

## [1.0.0] - 2026-04-06

### Added
- 初始版本：7大模块架构设计
- 虚拟筛选引擎（ChEMBL集成）
- ADMET预测（毒性+PK+合成可及性）
- 分子生成引擎（骨架优化+虚拟库）
- 先导优化（多参数平衡+分子编辑）
- 知识引擎（RAG+专利+临床试验）
- Agent编排（Pipeline+DMTA+决策+报告）
- REST API：15+端点（FastAPI+Swagger）
