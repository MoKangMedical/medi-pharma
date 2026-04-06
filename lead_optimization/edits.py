"""
分子编辑操作模块
定义先导优化中的化学变换操作
"""

from dataclasses import dataclass


@dataclass
class MolEdit:
    """分子编辑操作"""
    name: str
    description: str
    category: str  # scaffold / substituent / bioisostere / property


# 预定义编辑操作库
MOLECULAR_EDITS = [
    # 骨架编辑
    MolEdit("ring_expansion", "环扩展 (5→6元环)", "scaffold"),
    MolEdit("ring_contraction", "环缩小 (6→5元环)", "scaffold"),
    MolEdit("ring_opening", "开环", "scaffold"),
    MolEdit("ring_closure", "成环", "scaffold"),
    MolEdit("scaffold_hop", "骨架跃迁", "scaffold"),

    # 取代基编辑
    MolEdit("add_methyl", "加甲基 (-CH3)", "substituent"),
    MolEdit("remove_methyl", "去甲基", "substituent"),
    MolEdit("add_fluorine", "加氟 (-F)", "substituent"),
    MolEdit("add_chlorine", "加氯 (-Cl)", "substituent"),
    MolEdit("add_hydroxyl", "加羟基 (-OH)", "substituent"),
    MolEdit("add_amino", "加氨基 (-NH2)", "substituent"),
    MolEdit("add_cyano", "加氰基 (-CN)", "substituent"),
    MolEdit("add_trifluoromethyl", "加三氟甲基 (-CF3)", "substituent"),
    MolEdit("add_methoxy", "加甲氧基 (-OCH3)", "substituent"),

    # 生物电子等排体替换
    MolEdit("amide_to_oxazole", "酰胺→恶唑", "bioisostere"),
    MolEdit("phenyl_to_pyridine", "苯→吡啶", "bioisostere"),
    MolEdit("ester_to_amide", "酯→酰胺", "bioisostere"),
    MolEdit("carboxylate_to_tetrazole", "羧酸→四氮唑", "bioisostere"),
    MolEdit("ketone_to_oxazole", "酮→恶唑", "bioisostere"),
    MolEdit("ether_to_methylene", "醚→亚甲基", "bioisostere"),
    MolEdit("NH_to_O", "NH→O (酰胺→酯)", "bioisostere"),
    MolEdit("CH_to_N", "CH→N (芳环氮替换)", "bioisostere"),

    # 属性优化
    MolEdit("reduce_lipophilicity", "降低脂溶性", "property"),
    MolEdit("increase_solubility", "增加溶解性", "property"),
    MolEdit("block_metabolism", "代谢位点阻断", "property"),
    MolEdit("reduce_herg_risk", "降低hERG风险", "property"),
    MolEdit("improve_psa", "优化极性表面积", "property"),
]


def get_edits_by_category(category: str) -> list[MolEdit]:
    """按类别获取编辑操作"""
    return [e for e in MOLECULAR_EDITS if e.category == category]


def get_all_categories() -> list[str]:
    """获取所有编辑类别"""
    return list(set(e.category for e in MOLECULAR_EDITS))
