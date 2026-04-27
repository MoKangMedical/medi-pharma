"""
分子优化模块
多目标优化：活性+ADMET+合成可行性
基于RDKit合法操作的分子优化
"""

import logging
import random
from typing import Optional, Callable
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """优化结果"""
    original_smiles: str
    optimized_smiles: str
    improvements: dict       # 各指标改善
    generation: int
    method: str


class MoleculeOptimizer:
    """
    分子优化器
    基于RDKit合法操作的迭代优化
    """

    # 有效的取代基（已验证）
    SUBSTITUENTS = [
        "C", "CC", "CCC",
        "N", "O", "F", "Cl", "Br",
        "C(=O)N", "C(=O)O", "C(=O)OC",
        "NC(=O)", "OC(=O)",
        "OCC", "NCC",
        "C(F)(F)F",
        "S(=O)(=O)N",
    ]

    # 有效连接器
    LINKERS = [
        "", "C", "CC",
        "C(=O)", "C(=O)N", "NC(=O)",
        "OCC", "NCC",
    ]

    def __init__(
        self,
        scoring_fn: Optional[Callable] = None,
        population_size: int = 50,
        n_generations: int = 20,
        mutation_rate: float = 0.3
    ):
        self.scoring_fn = scoring_fn or self._default_score
        self.population_size = population_size
        self.n_generations = n_generations
        self.mutation_rate = mutation_rate

    def optimize(
        self,
        smiles: str,
        objective: str = "multi",
        n_iterations: int = 100,
        target_props: Optional[dict] = None
    ) -> list[OptimizationResult]:
        """
        分子优化主流程

        Args:
            smiles: 起始SMILES
            objective: 优化目标
            n_iterations: 迭代次数
            target_props: 目标属性
        """
        logger.info(f"开始分子优化: {smiles[:50]}...")

        best_smiles = smiles
        best_score = self.scoring_fn(smiles)
        results = []

        for i in range(n_iterations):
            # 生成变异体
            mutant = self._mutate(best_smiles)
            if not mutant:
                continue

            mutant_score = self.scoring_fn(mutant)

            # 改进了就接受
            if mutant_score > best_score:
                improvement = {
                    "score_delta": round(mutant_score - best_score, 3),
                    "old_score": round(best_score, 3),
                    "new_score": round(mutant_score, 3),
                }

                results.append(OptimizationResult(
                    original_smiles=best_smiles,
                    optimized_smiles=mutant,
                    improvements=improvement,
                    generation=i,
                    method="hill_climbing"
                ))

                best_smiles = mutant
                best_score = mutant_score

            # 模拟退火：以一定概率接受较差解
            elif random.random() < 0.1 * (1 - i / n_iterations):
                best_smiles = mutant
                best_score = mutant_score

        logger.info(f"优化完成: {len(results)} 步改进, 最终分数 {best_score:.3f}")
        return results

    def genetic_optimize(
        self,
        initial_population: list[str],
        target_props: Optional[dict] = None,
    ) -> list[str]:
        """
        遗传算法优化

        Args:
            initial_population: 初始种群SMILES列表
            target_props: 目标属性
        """
        population = initial_population[:self.population_size]

        for gen in range(self.n_generations):
            # 评估适应度
            fitness = [self.scoring_fn(s) for s in population]

            # 选择
            selected = self._tournament_select(population, fitness, k=len(population) // 2)

            # 交叉
            offspring = []
            for _ in range(self.population_size - len(selected)):
                p1, p2 = random.sample(selected, 2)
                child = self._crossover(p1, p2)
                if child:
                    offspring.append(child)

            # 变异
            for i in range(len(offspring)):
                if random.random() < self.mutation_rate:
                    mutated = self._mutate(offspring[i])
                    if mutated:
                        offspring[i] = mutated

            population = selected + offspring

            # 报告进度
            if gen % 5 == 0:
                best_fitness = max(fitness)
                logger.info(f"Gen {gen}: Best fitness = {best_fitness:.3f}")

        # 返回最优种群
        final_fitness = [self.scoring_fn(s) for s in population]
        sorted_pop = [s for _, s in sorted(zip(final_fitness, population), reverse=True)]
        return sorted_pop

    def _mutate(self, smiles: str) -> Optional[str]:
        """执行随机分子变异（确保生成有效SMILES）"""
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem

            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            # 选择变异策略
            strategy = random.choice(["add_substituent", "replace_atom", "add_linker"])

            if strategy == "add_substituent":
                # 添加取代基
                linker = random.choice(self.LINKERS)
                subst = random.choice(self.SUBSTITUENTS)
                new_smi = smiles + linker + subst

            elif strategy == "replace_atom":
                # 替换原子（C<->N）
                atoms = list(smiles)
                if "C" in atoms:
                    idx = random.choice([i for i, c in enumerate(atoms) if c == "C"])
                    atoms[idx] = "N"
                    new_smi = "".join(atoms)
                elif "N" in atoms:
                    idx = random.choice([i for i, c in enumerate(atoms) if c == "N"])
                    atoms[idx] = "C"
                    new_smi = "".join(atoms)
                else:
                    new_smi = smiles + "C"

            else:  # add_linker
                # 添加连接器
                linker = random.choice(["C", "CC", "C(=O)", "C(=O)N"])
                new_smi = smiles + linker

            # 验证结果
            new_mol = Chem.MolFromSmiles(new_smi)
            if new_mol:
                return Chem.MolToSmiles(new_mol)
            return None

        except Exception:
            return None

    def _crossover(self, smiles1: str, smiles2: str) -> Optional[str]:
        """分子交叉：组合两个分子的片段（确保有效）"""
        try:
            from rdkit import Chem

            mol1 = Chem.MolFromSmiles(smiles1)
            mol2 = Chem.MolFromSmiles(smiles2)
            if mol1 is None or mol2 is None:
                return None

            # 简单交叉：取mol1的前半部分和mol2的后半部分
            s1 = Chem.MolToSmiles(mol1)
            s2 = Chem.MolToSmiles(mol2)

            mid1 = len(s1) // 2
            mid2 = len(s2) // 2
            child = s1[:mid1] + s2[mid2:]

            # 验证
            child_mol = Chem.MolFromSmiles(child)
            if child_mol:
                return Chem.MolToSmiles(child_mol)
            return None
        except:
            return None

    def _tournament_select(
        self, population: list[str], fitness: list[float], k: int
    ) -> list[str]:
        """锦标赛选择"""
        selected = []
        for _ in range(k):
            candidates = random.sample(range(len(population)), min(3, len(population)))
            winner_idx = max(candidates, key=lambda i: fitness[i])
            selected.append(population[winner_idx])
        return selected

    def _default_score(self, smiles: str) -> float:
        """默认评分函数（无外部模型时）"""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, QED

            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return 0.0

            qed = QED.qed(mol)
            logp = Descriptors.MolLogP(mol)
            mw = Descriptors.MolWt(mol)
            sa = 1.0 / (1 + Descriptors.RingCount(mol) * 0.2)

            # 综合评分
            score = qed * 0.4 + min(logp / 5, 1) * 0.2 + min(mw / 500, 1) * 0.2 + sa * 0.2
            return round(score, 4)
        except:
            return 0.5
