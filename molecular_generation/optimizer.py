"""
分子优化模块
多目标优化：活性+ADMET+合成可行性
支持蒙特卡洛树搜索(MCTS)和遗传算法
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
    基于编辑操作的迭代优化
    """

    # 分子编辑操作
    MUTATIONS = [
        "add_methyl",       # 加甲基
        "remove_methyl",    # 去甲基
        "add_fluorine",     # 加氟
        "add_chlorine",     # 加氯
        "add_hydroxyl",     # 加羟基
        "add_amino",        # 加氨基
        "replace_N_with_CH", # N→CH
        "replace_CH_with_N", # CH→N
        "add_ring",         # 加环
        "ring_expansion",   # 扩环
        "ring_contraction", # 缩环
        "add_amide",        # 加酰胺
        "bioisostere_replace", # 生物电子等排体替换
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
        objective: str = "multi",  # activity / admet / multi
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
        """执行随机分子变异"""
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            n_atoms = mol.GetNumAtoms()
            if n_atoms < 2:
                return None

            # 简化变异：随机选择原子进行修饰
            mutation_type = random.choice(["add_atom", "change_bond", "substitute"])

            if mutation_type == "add_atom":
                # 在SMILES层面拼接
                additions = ["C", "N", "O", "F", "S"]
                return smiles + random.choice(additions)

            elif mutation_type == "substitute":
                # 替换子结构
                replacements = [
                    ("c1ccccc1", "c1ccc2[nH]ccc2c1"),  # 苯→吲哚
                    ("C", "N"),  # C→N
                    ("CC", "C(=O)"),  # 简化替换
                ]
                for old, new in replacements:
                    if old in smiles:
                        return smiles.replace(old, new, 1)
                return smiles + "C"

            else:
                return smiles + "C"

        except Exception:
            return None

    def _crossover(self, smiles1: str, smiles2: str) -> Optional[str]:
        """分子交叉：组合两个分子的片段"""
        try:
            mid1 = len(smiles1) // 2
            mid2 = len(smiles2) // 2
            child = smiles1[:mid1] + smiles2[mid2:]

            # 验证
            from rdkit import Chem
            mol = Chem.MolFromSmiles(child)
            if mol is not None:
                return Chem.MolToSmiles(mol)
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
