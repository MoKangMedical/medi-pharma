# Changelog

All notable changes to MediPharma will be documented in this file.

## [2.1.0] - 2026-04-27

### Added
- Streamlit Web界面 (`app.py`) - 完整的可视化操作界面
- Demo示例数据 - 10个热门药物和10个热门靶点
- GitHub Actions CI/CD - 自动化测试和部署
- Docker完整部署支持 - Dockerfile + docker-compose.yml
- 完整单元测试套件 (`tests/test_comprehensive.py`)
- 6个AI Agents模块
- 全流程Pipeline编排器

### Changed
- 更新requirements.txt添加streamlit依赖
- 更新README.md文档
- 优化项目结构

### Fixed
- Docker配置完善

## [2.0.0] - 2026-04-15

### Added
- 7大核心模块完整实现
- FastAPI后端API
- CLI命令行工具
- 知识图谱引擎
- 先导化合物优化

## [1.0.0] - 2026-04-01

### Added
- 初始版本发布
- 基础药物发现功能
- ChEMBL化合物检索
- OpenTargets靶点分析
