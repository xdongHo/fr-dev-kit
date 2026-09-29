"""
批量修复深化学习目录下的错误 CPT 模板
问题：子 agent 生成的模板用了错误的 XML Schema（DataSets/TableDataList 而非 TableDataMap）
修复：将 DataSets/TableDataList/EmbeddedTableData 结构转换为 TableDataMap/TableData 结构
"""

# --- console-safe guard (2026-09-11 SOP 提速: GBK 控制台打印 emoji 不再 UnicodeEncodeError) ---
try:
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):
        if _s is not None and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass
except Exception:
    pass
# --- end guard ---
import xml.etree.ElementTree as ET
import os, sys, shutil
from copy import deepcopy

TEMPLATE_DIR = r'D:\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\深化学习'
BACKUP_DIR = r'D:\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\深化学习\_backup'

def fix_cpt(filepath):
    """修复单个 CPT 文件"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as e:
        return False, f"XML 解析失败: {e}"
    
    # 检查是否需要修复（已有 TableDataMap 则跳过）
    if root.find('.//TableDataMap') is not None:
        return False, "已有 TableDataMap，无需修复"
    
    # 找 DataSets
    ds = root.find('.//DataSets')
    if ds is None:
        return False, "无 DataSets 节点"
    
    # 提取 EmbeddedTableData 数据集
    datasets = []
    tdl = ds.find('.//TableDataList')
    if tdl is None:
        return False, "无 TableDataList 节点"
    
    for etd in tdl.findall('.//EmbeddedTableData'):
        name = etd.get('name', '')
        if not name:
            continue
        
        # 提取列信息
        col_names = ''
        col_types = ''
        rows = []
        
        for child in etd:
            if child.tag == 'TableData':
                for gc in child:
                    if gc.tag == 'ColumnNames':
                        # 列名可能在 gc.text 或 <String> 子元素中
                        if gc.text and gc.text.strip():
                            col_names = gc.text.strip()
                        else:
                            # 提取 <String> 子元素
                            strs = [s.text or '' for s in gc.findall('String')]
                            col_names = ','.join(strs)
                    elif gc.tag == 'ColumnType':
                        col_types = gc.text or ''
            elif child.tag == 'RowData':
                rows.append(child.text or '')
        
        if col_names:
            datasets.append({
                'name': name,
                'col_names': col_names,
                'col_types': col_types,
                'rows': rows
            })
    
    if not datasets:
        return False, "未提取到有效数据集"
    
    # 构建 TableDataMap
    tdm = ET.Element('TableDataMap')
    
    for ds_info in datasets:
        td = ET.SubElement(tdm, 'TableData')
        td.set('name', ds_info['name'])
        
        # Attributes
        attrs = ET.SubElement(td, 'Attributes')
        attrs.set('maxMemRowCount', '-1')
        
        # ColumnNames
        cn = ET.SubElement(td, 'ColumnNames')
        cn.text = ds_info['col_names']
        
        # ColumnType
        ct = ET.SubElement(td, 'ColumnType')
        ct.text = ds_info['col_types'] or ','.join(['0'] * len(ds_info['col_names'].split(',')))
        
        # RowData
        for row in ds_info['rows']:
            rd = ET.SubElement(td, 'RowData')
            rd.text = row
    
    # 将 TableDataMap 插入到 Root/Report 之前（WorkBook 的直接子节点）
    # 找到插入位置：在 DesignerVersion 之后，Root 之前
    insert_idx = 0
    for i, child in enumerate(root):
        if child.tag == 'DesignerVersion':
            insert_idx = i + 1
            break
    
    root.insert(insert_idx, tdm)
    
    # 删除旧的 DataSets
    report = root.find('.//Report')
    if report is not None:
        old_ds = report.find('DataSets')
        if old_ds is not None:
            report.remove(old_ds)
    
    # 修复根节点属性
    root.attrib.pop('jdk', None)
    root.attrib.pop('version', None)
    root.set('xmlVersion', '20170720')
    root.set('releaseVersion', '10.0.0')
    
    # 确保有 ParameterUI（如果没有则添加空的）
    if root.find('.//ParameterUI') is None:
        # 在 TableDataMap 之后添加
        pui = ET.Element('ParameterUI')
        root.insert(insert_idx + 1, pui)
    
    # 写回文件
    tree.write(filepath, encoding='utf-8', xml_declaration=True)
    
    return True, f"修复成功: {len(datasets)} 个数据集"

def main():
    # 创建备份目录
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 扫描所有模板
    files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.cpt') or f.endswith('.frm')]
    
    results = {'fixed': [], 'skipped': [], 'failed': []}
    
    for f in sorted(files):
        filepath = os.path.join(TEMPLATE_DIR, f)
        
        # 备份
        backup_path = os.path.join(BACKUP_DIR, f)
        if not os.path.exists(backup_path):
            shutil.copy2(filepath, backup_path)
        
        # 修复
        success, msg = fix_cpt(filepath)
        
        if success:
            results['fixed'].append((f, msg))
        elif '无需修复' in msg:
            results['skipped'].append((f, msg))
        else:
            results['failed'].append((f, msg))
    
    # 输出结果
    print(f"\n=== 修复结果 ===")
    print(f"修复成功: {len(results['fixed'])}")
    print(f"跳过(已正确): {len(results['skipped'])}")
    print(f"修复失败: {len(results['failed'])}")
    
    if results['fixed']:
        print(f"\n=== 修复成功的模板 ===")
        for f, msg in results['fixed']:
            print(f"  ✅ {f}: {msg}")
    
    if results['failed']:
        print(f"\n=== 修复失败的模板 ===")
        for f, msg in results['failed']:
            print(f"  ❌ {f}: {msg}")
    
    print(f"\n备份目录: {BACKUP_DIR}")

if __name__ == '__main__':
    main()
