"""
分子3D可视化模块
基于py3Dmol的交互式分子可视化
"""

import logging
from typing import Optional
import base64

logger = logging.getLogger(__name__)


def generate_3d_mol_html(smiles: str, width: int = 400, height: int = 300) -> str:
    """
    生成分子3D可视化的HTML代码
    
    Args:
        smiles: SMILES字符串
        width: 宽度
        height: 高度
        
    Returns:
        HTML代码字符串
    """
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem, Draw
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return _generate_error_html("无效的SMILES")
        
        # 添加氢原子
        mol = Chem.AddHs(mol)
        
        # 生成3D坐标
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        
        # 转换为MOL块
        mol_block = Chem.MolToMolBlock(mol)
        
        # 生成2D图像作为备用
        mol_2d = Chem.RemoveHs(mol)
        img = Draw.MolToImage(mol_2d, size=(width, height))
        
        # 转换为base64
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        # 生成HTML
        html = f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{img_str}" 
                 width="{width}" height="{height}"
                 style="border: 1px solid #ddd; border-radius: 8px;">
            <p style="margin-top: 8px; color: #666; font-size: 12px;">
                SMILES: {smiles[:50]}{'...' if len(smiles) > 50 else ''}
            </p>
        </div>
        """
        
        return html
        
    except ImportError:
        return _generate_error_html("RDKit未安装")
    except Exception as e:
        return _generate_error_html(f"生成失败: {str(e)}")


def generate_mol_grid_html(smiles_list: list, names: list = None, 
                          cols: int = 3, cell_size: int = 200) -> str:
    """
    生成分子网格的HTML代码
    
    Args:
        smiles_list: SMILES列表
        names: 分子名称列表
        cols: 列数
        cell_size: 单元格大小
        
    Returns:
        HTML代码字符串
    """
    try:
        from rdkit import Chem
        from rdkit.Chem import Draw
        
        if names is None:
            names = [f"分子 {i+1}" for i in range(len(smiles_list))]
        
        # 生成分子图像
        mols = []
        valid_names = []
        for smi, name in zip(smiles_list, names):
            mol = Chem.MolFromSmiles(smi)
            if mol:
                mols.append(mol)
                valid_names.append(name)
        
        if not mols:
            return _generate_error_html("没有有效分子")
        
        # 生成网格图像
        img = Draw.MolsToGridImage(
            mols, 
            molsPerRow=cols,
            subImgSize=(cell_size, cell_size),
            legends=valid_names
        )
        
        # 转换为base64
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        html = f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{img_str}" 
                 style="max-width: 100%; border: 1px solid #ddd; border-radius: 8px;">
        </div>
        """
        
        return html
        
    except Exception as e:
        return _generate_error_html(f"生成失败: {str(e)}")


def generate_mol_properties_html(smiles: str) -> str:
    """
    生成分子属性的HTML代码
    
    Args:
        smiles: SMILES字符串
        
    Returns:
        HTML代码字符串
    """
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, QED, Draw
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return _generate_error_html("无效的SMILES")
        
        # 计算属性
        props = {
            "分子量": f"{Descriptors.MolWt(mol):.1f}",
            "LogP": f"{Descriptors.MolLogP(mol):.2f}",
            "氢键供体": Descriptors.NumHDonors(mol),
            "氢键受体": Descriptors.NumHAcceptors(mol),
            "极性表面积": f"{Descriptors.TPSA(mol):.1f}",
            "可旋转键": Descriptors.NumRotatableBonds(mol),
            "环数": Descriptors.RingCount(mol),
            "QED": f"{QED.qed(mol):.3f}",
        }
        
        # 生成属性表格
        rows = ""
        for key, value in props.items():
            rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">{key}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{value}</td>
            </tr>
            """
        
        html = f"""
        <div style="font-family: sans-serif;">
            <table style="width: 100%; border-collapse: collapse;">
                {rows}
            </table>
            <p style="margin-top: 12px; color: #666; font-size: 12px;">
                SMILES: {smiles[:60]}{'...' if len(smiles) > 60 else ''}
            </p>
        </div>
        """
        
        return html
        
    except Exception as e:
        return _generate_error_html(f"计算失败: {str(e)}")


def _generate_error_html(message: str) -> str:
    """生成错误HTML"""
    return f"""
    <div style="padding: 20px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; text-align: center;">
        <p style="color: #856404; margin: 0;">⚠️ {message}</p>
    </div>
    """


def check_3dmol_available() -> bool:
    """检查py3Dmol是否可用"""
    try:
        import py3Dmol
        return True
    except ImportError:
        return False


def get_mol_info(smiles: str) -> dict:
    """获取分子信息"""
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, QED
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {"error": "无效的SMILES"}
        
        return {
            "smiles": smiles,
            "canonical_smiles": Chem.MolToSmiles(mol),
            "molecular_weight": round(Descriptors.MolWt(mol), 1),
            "logp": round(Descriptors.MolLogP(mol), 2),
            "hbd": Descriptors.NumHDonors(mol),
            "hba": Descriptors.NumHAcceptors(mol),
            "tpsa": round(Descriptors.TPSA(mol), 1),
            "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
            "rings": Descriptors.RingCount(mol),
            "qed": round(QED.qed(mol), 3),
            "num_atoms": mol.GetNumAtoms(),
            "num_heavy_atoms": mol.GetNumHeavyAtoms(),
        }
    except Exception as e:
        return {"error": str(e)}
