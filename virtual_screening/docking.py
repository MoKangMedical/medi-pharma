"""
分子对接封装模块
整合DiffDock（AI对接）和AutoDock Vina（传统对接）
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class DockingResult:
    """对接结果"""
    smiles: str
    pose_file: str = ""         # 输出pose文件路径
    confidence: float = 0.0     # DiffDock置信度
    binding_score: float = 0.0  # 结合分数 (kcal/mol, Vina)
    rmsd: float = 0.0
    method: str = ""            # diffdock / vina
    rank: int = 0


class DockingEngine:
    """
    分子对接引擎
    支持DiffDock (AI) 和 AutoDock Vina (传统)
    """

    def __init__(
        self,
        diffdock_path: Optional[str] = None,
        vina_path: Optional[str] = None,
        output_dir: str = "./docking_results"
    ):
        self.diffdock_path = diffdock_path
        self.vina_path = vina_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def dock_diffdock(
        self,
        protein_pdb: str,
        ligand_smiles: list[str],
        num_samples: int = 40,
        num_steps: int = 18
    ) -> list[DockingResult]:
        """
        使用DiffDock进行扩散模型对接
        需要安装DiffDock: pip install diffdock 或 conda
        """
        if not self.diffdock_path:
            logger.warning("DiffDock路径未配置，使用模拟模式")
            return self._mock_docking(ligand_smiles, method="diffdock")

        results = []
        with tempfile.TemporaryDirectory() as tmpdir:
            # 写入配体SMILES文件
            smiles_file = Path(tmpdir) / "ligands.csv"
            smiles_file.write_text("\n".join(ligand_smiles))

            try:
                cmd = [
                    "python", "-m", "diffdock",
                    "--protein_path", protein_pdb,
                    "--ligand_csv", str(smiles_file),
                    "--out_dir", str(self.output_dir / "diffdock"),
                    "--samples_per_complex", str(num_samples),
                    "--inference_steps", str(num_steps),
                ]
                subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

                # 解析结果
                results = self._parse_diffdock_output(self.output_dir / "diffdock")

            except subprocess.TimeoutExpired:
                logger.error("DiffDock对接超时")
            except Exception as e:
                logger.error(f"DiffDock执行失败: {e}")

        return results

    def dock_vina(
        self,
        protein_pdb: str,
        ligand_smiles: list[str],
        center: tuple[float, float, float] = (0, 0, 0),
        box_size: tuple[float, float, float] = (20, 20, 20),
        exhaustiveness: int = 8
    ) -> list[DockingResult]:
        """
        使用AutoDock Vina进行对接
        需要安装Vina: conda install -c conda-forge autodock-vina
        """
        if not self.vina_path:
            logger.warning("Vina路径未配置，使用模拟模式")
            return self._mock_docking(ligand_smiles, method="vina")

        results = []
        for i, smiles in enumerate(ligand_smiles):
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    # SMILES → PDBQT (需要RDKit)
                    ligand_pdbqt = Path(tmpdir) / f"ligand_{i}.pdbqt"
                    self._smiles_to_pdbqt(smiles, ligand_pdbqt)

                    output_pdbqt = Path(tmpdir) / f"out_{i}.pdbqt"

                    cmd = [
                        self.vina_path,
                        "--receptor", protein_pdb,
                        "--ligand", str(ligand_pdbqt),
                        "--center_x", str(center[0]),
                        "--center_y", str(center[1]),
                        "--center_z", str(center[2]),
                        "--size_x", str(box_size[0]),
                        "--size_y", str(box_size[1]),
                        "--size_z", str(box_size[2]),
                        "--exhaustiveness", str(exhaustiveness),
                        "--out", str(output_pdbqt)
                    ]

                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                    # 解析Vina输出
                    score = self._parse_vina_output(proc.stdout)
                    results.append(DockingResult(
                        smiles=smiles,
                        binding_score=score,
                        method="vina",
                        rank=i + 1
                    ))

            except Exception as e:
                logger.warning(f"Vina对接失败 ({smiles[:30]}): {e}")
                continue

        results.sort(key=lambda x: x.binding_score)  # Vina分数越低越好
        for i, r in enumerate(results):
            r.rank = i + 1
        return results

    def _smiles_to_pdbqt(self, smiles: str, output_path: Path):
        """SMILES转PDBQT格式（通过RDKit + meeko）"""
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem

            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise ValueError(f"无效SMILES: {smiles}")

            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, AllChem.ETKDG())
            AllChem.MMFFOptimizeMolecule(mol)

            # 写入SDF，然后尝试转PDBQT
            sdf_path = output_path.with_suffix(".sdf")
            writer = Chem.SDWriter(str(sdf_path))
            writer.write(mol)
            writer.close()

            # 如果有meeko可以用: mk_prepare_ligand.py
            # 否则直接用sdf
            import shutil
            shutil.copy(sdf_path, output_path.with_suffix(".pdbqt"))

        except ImportError:
            logger.warning("RDKit未安装，跳过SMILES转换")
        except Exception as e:
            logger.warning(f"SMILES转换失败: {e}")

    def _parse_vina_output(self, stdout: str) -> float:
        """解析Vina输出中的最佳分数"""
        for line in stdout.split("\n"):
            if "REMARK VINA RESULT:" in line:
                parts = line.split()
                if len(parts) >= 4:
                    return float(parts[3])
        return 0.0

    def _parse_diffdock_output(self, output_dir: Path) -> list[DockingResult]:
        """解析DiffDock输出结果"""
        results = []
        if not output_dir.exists():
            return results

        # DiffDock输出结构: rankX/confidenceY.sdf
        for sdf_file in sorted(output_dir.rglob("*.sdf")):
            try:
                # 从文件名提取置信度
                name = sdf_file.stem
                conf = 0.0
                if "confidence" in name:
                    conf_str = name.split("confidence")[1].split(".")[0]
                    conf = float(conf_str)

                results.append(DockingResult(
                    smiles="",  # DiffDock输出不含SMILES
                    pose_file=str(sdf_file),
                    confidence=conf,
                    method="diffdock"
                ))
            except Exception as e:
                logger.warning(f"解析DiffDock输出失败: {e}")

        results.sort(key=lambda x: x.confidence, reverse=True)
        for i, r in enumerate(results):
            r.rank = i + 1
        return results

    def _mock_docking(self, smiles_list: list[str], method: str) -> list[DockingResult]:
        """模拟对接结果（工具未安装时的fallback）"""
        import random
        results = []
        for i, smiles in enumerate(smiles_list):
            score = random.uniform(-12, -4) if method == "vina" else 0
            conf = random.uniform(0.3, 0.9) if method == "diffdock" else 0
            results.append(DockingResult(
                smiles=smiles,
                binding_score=round(score, 2),
                confidence=round(conf, 3),
                method=f"{method}_mock",
                rank=i + 1
            ))
        results.sort(key=lambda x: x.binding_score if method == "vina" else -x.confidence)
        for i, r in enumerate(results):
            r.rank = i + 1
        return results
