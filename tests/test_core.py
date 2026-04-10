"""MediPharma 核心模块测试。"""

import pytest
from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)


class TestHealth:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "healthy"


class TestTargetDiscovery:
    def test_discover(self):
        r = client.post("/api/v1/targets/discover", json={
            "disease": "重症肌无力",
            "max_papers": 10,
            "top_n": 3,
        })
        assert r.status_code == 200
        d = r.json()
        assert "disease" in d

    def test_discover_returns_target_info(self):
        r = client.post("/api/v1/targets/discover", json={
            "disease": "2型糖尿病",
            "max_papers": 5,
            "top_n": 3,
        })
        assert r.status_code == 200
        d = r.json()
        assert "targets" in d or "total_candidates" in d


class TestVirtualScreening:
    def test_screen(self):
        r = client.post("/api/v1/screening/run", json={
            "target_chembl_id": "CHEMBL2364162",
            "max_compounds": 10,
            "top_n": 5,
        })
        assert r.status_code == 200
        d = r.json()
        assert "top_candidates" in d


class TestMolecularGeneration:
    def test_generate(self):
        r = client.post("/api/v1/generate", json={
            "target_name": "CHRM1",
            "n_generate": 50,
            "top_n": 5,
        })
        assert r.status_code == 200
        d = r.json()
        assert d["total_generated"] > 0
        assert "top_candidates" in d


class TestADMET:
    def test_admet_single(self):
        r = client.post("/api/v1/admet/predict", json={
            "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
        })
        assert r.status_code == 200
        d = r.json()
        assert "absorption" in d
        assert "toxicity" in d
        assert "pass_filter" in d

    def test_admet_ethanol(self):
        r = client.post("/api/v1/admet/predict", json={
            "smiles": "CCO",
        })
        assert r.status_code == 200
        d = r.json()
        assert d["smiles"] == "CCO"

    def test_admet_batch(self):
        r = client.post("/api/v1/admet/batch", json={
            "smiles_list": ["CCO", "c1ccccc1", "CC(=O)O"],
        })
        assert r.status_code == 200


class TestOptimization:
    def test_optimize(self):
        r = client.post("/api/v1/optimize", json={
            "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
            "max_generations": 3,
            "population_size": 10,
        })
        assert r.status_code == 200
        d = r.json()
        assert "top_candidates" in d


class TestPipeline:
    def test_pipeline_run(self):
        r = client.post("/api/v1/pipeline/run", json={
            "disease": "2型糖尿病",
            "target_chembl_id": "CHEMBL2364162",
        })
        assert r.status_code == 200
        d = r.json()
        assert "disease" in d


class TestKnowledge:
    def test_knowledge_report(self):
        r = client.post("/api/v1/knowledge/report", json={
            "target": "GLP1R",
            "disease": "肥胖症",
        })
        assert r.status_code == 200
        d = r.json()
        assert "disease" in d or "literature_summary" in d


class TestADMETEngine:
    def test_engine_creation(self):
        from admet_prediction.engine import ADMETEngine
        engine = ADMETEngine()
        assert engine is not None

    def test_predict_single(self):
        from admet_prediction.engine import ADMETEngine
        engine = ADMETEngine()
        result = engine.predict("CC(C)Cc1ccc(cc1)C(C)C(=O)O")
        assert result is not None


class TestVirtualScreeningEngine:
    def test_engine_creation(self):
        from virtual_screening.engine import VirtualScreeningEngine
        engine = VirtualScreeningEngine()
        assert engine is not None

    def test_screen(self):
        from virtual_screening.engine import VirtualScreeningEngine
        engine = VirtualScreeningEngine()
        results = engine.screen("CHEMBL2364162")
        assert results is not None


class TestMolecularGenerationEngine:
    def test_engine_creation(self):
        from molecular_generation.engine import MolecularGenerationEngine
        engine = MolecularGenerationEngine()
        assert engine is not None


class TestDMTAManager:
    def test_creation(self):
        from orchestrator.dmta import DMTAManager
        mgr = DMTAManager()
        assert mgr is not None


class TestDecisionEngine:
    def test_creation(self):
        from orchestrator.decision import DecisionEngine
        engine = DecisionEngine()
        assert engine is not None
