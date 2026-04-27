"""
MediPharma 单元测试
测试核心模块功能
"""

import pytest
import json
from pathlib import Path

# 测试数据路径
DATA_DIR = Path(__file__).parent.parent / "data"


class TestADMETPrediction:
    """ADMET预测模块测试"""
    
    def test_admet_engine_import(self):
        """测试ADMET引擎导入"""
        from admet_prediction.engine import ADMETEngine
        engine = ADMETEngine()
        assert engine is not None
    
    def test_toxicity_predictor_import(self):
        """测试毒性预测器导入"""
        from admet_prediction.toxicity import ToxicityPredictor
        predictor = ToxicityPredictor()
        assert predictor is not None
        assert hasattr(predictor, 'predict_ames')
        assert hasattr(predictor, 'predict_herg')
    
    def test_sa_score_class(self):
        """测试合成可及性评分类"""
        from admet_prediction.sa_score import SAScorer
        scorer = SAScorer()
        assert scorer is not None


class TestVirtualScreening:
    """虚拟筛选模块测试"""
    
    def test_screening_engine_import(self):
        """测试筛选引擎导入"""
        from virtual_screening.engine import VirtualScreeningEngine
        engine = VirtualScreeningEngine()
        assert engine is not None
    
    def test_compound_library(self):
        """测试化合物库加载"""
        from virtual_screening.compound_library import CompoundLibrary
        lib = CompoundLibrary()
        assert lib is not None


class TestTargetDiscovery:
    """靶点发现模块测试"""
    
    def test_target_engine_import(self):
        """测试靶点引擎导入"""
        from target_discovery.engine import TargetDiscoveryEngine
        engine = TargetDiscoveryEngine()
        assert engine is not None
    
    def test_pubmed_miner(self):
        """测试PubMed挖掘"""
        from target_discovery.pubmed_miner import PubMedMiner
        miner = PubMedMiner()
        assert miner is not None


class TestMolecularGeneration:
    """分子生成模块测试"""
    
    def test_generation_engine_import(self):
        """测试生成引擎导入"""
        from molecular_generation.engine import MolecularGenerationEngine
        engine = MolecularGenerationEngine()
        assert engine is not None
    
    def test_optimizer_import(self):
        """测试优化器导入"""
        from molecular_generation.optimizer import MoleculeOptimizer
        optimizer = MoleculeOptimizer()
        assert optimizer is not None


class TestDataFiles:
    """数据文件测试"""
    
    def test_demo_compounds_exist(self):
        """测试Demo化合物数据文件存在"""
        path = DATA_DIR / "demo_compounds.json"
        assert path.exists(), f"Missing: {path}"
    
    def test_demo_compounds_valid_json(self):
        """测试Demo化合物数据格式正确"""
        path = DATA_DIR / "demo_compounds.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0
            assert "smiles" in data[0]
    
    def test_demo_targets_exist(self):
        """测试Demo靶点数据文件存在"""
        path = DATA_DIR / "demo_targets.json"
        assert path.exists(), f"Missing: {path}"
    
    def test_demo_targets_valid_json(self):
        """测试Demo靶点数据格式正确"""
        path = DATA_DIR / "demo_targets.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0
            assert "target_id" in data[0]
            assert "gene_symbol" in data[0]


class TestBackendAPI:
    """后端API测试"""
    
    def test_backend_import(self):
        """测试后端导入"""
        from backend.api import app
        assert app is not None
    
    def test_models_import(self):
        """测试模型导入"""
        from backend.models import HealthResponse
        assert HealthResponse is not None


class TestAgents:
    """Agent模块测试"""
    
    def test_agents_import(self):
        """测试Agent模块导入"""
        from agents import one_person_pharma
        assert one_person_pharma is not None


class TestCLI:
    """CLI命令测试"""
    
    def test_main_import(self):
        """测试main模块导入"""
        import main
        assert main is not None
    
    def test_argparse_setup(self):
        """测试参数解析"""
        import main
        assert hasattr(main, 'main')
        assert hasattr(main, 'cmd_serve')
        assert hasattr(main, 'cmd_target')
        assert hasattr(main, 'cmd_screen')
        assert hasattr(main, 'cmd_admet')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
