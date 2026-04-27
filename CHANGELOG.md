# Changelog

All notable changes to MediPharma will be documented in this file.

## [2.1.0] - 2026-04-27

### Added
- Streamlit Web界面 (app.py) - 5个功能标签页，专业UI设计
- 本地化合物库 (data/local_compound_library.json) - 30个常见药物分子
- 端到端闭环演示脚本 (demo_e2e.py)
- 完整单元测试套件 (tests/test_comprehensive.py) - 18个测试
- GitHub Actions CI/CD配置
- Docker完整部署支持

### Fixed
- 分子生成器SMILES质量问题 - 使用RDKit BRICS确保有效性
- 虚拟筛选本地化合物库支持 - 无需网络即可运行
- conftest.py导入路径修复

### Changed
- 放宽分子生成属性过滤
- 更新README.md文档
- 优化Streamlit前端UI

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
