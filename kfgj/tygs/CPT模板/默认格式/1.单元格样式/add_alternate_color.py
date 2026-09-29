"""
给 示例实际表.cpt 数据行添加隔行换色 ConditionAttr
公式: row()%2==0 → 偶数行浅色背景，奇数行白色
"""
import re, shutil
from pathlib import Path
from datetime import datetime

FP = r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程\明细报表\示例实际表.cpt"

# 备份
bak = Path(FP).parent / f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
bak.mkdir(parents=True, exist_ok=True)
shutil.copy2(FP, bak / Path(FP).name)
print(f"备份: {bak}")

with open(FP, 'r', encoding='utf-8') as f:
    content = f.read()

# 偶数行红色 (-65536), 奇数行白色 (-1)
EVEN_COLOR = "-65536"
ODD_COLOR = "-1"

# ConditionAttr XML 模板 (偶数行红色)
COND_EVEN = f'''<ConditionAttr><ConditionCollection><Condition class="com.fr.data.condition.CommonCondition"><ConditionAttrData><ConditionAttrRowColumn rowType="0"/></ConditionAttrData><FormulaExpr class="com.fr.base.Formula"><Attributes><![CDATA[row()%2==0]]></Attributes></FormulaExpr></Condition></ConditionCollection><Style horizontal_alignment="0" imageLayout="1"><FRFont name="微软雅黑" style="0" size="72"/><Background name="ColorBackground" color="{EVEN_COLOR}"/><Border/></Style></ConditionAttr>'''

# 奇数行换色
COND_ODD = f'''<ConditionAttr><ConditionCollection><Condition class="com.fr.data.condition.CommonCondition"><ConditionAttrData><ConditionAttrRowColumn rowType="0"/></ConditionAttrData><FormulaExpr class="com.fr.base.Formula"><Attributes><![CDATA[row()%2==1]]></Attributes></FormulaExpr></Condition></ConditionCollection><Style horizontal_alignment="0" imageLayout="1"><FRFont name="微软雅黑" style="0" size="72"/><Background name="ColorBackground" color="{ODD_COLOR}"/><Border/></Style></ConditionAttr>'''

# 查找 CellElementList 中每个 DSColumn / 公式单元格
# 匹配: <C c="..." r="..." s="..."> ... <O t="DSColumn">...</O> ... </C>
# 或紧凑格式: <C c="..." r="..."><O><![CDATA[ds1.G(x)]]></O>

# 策略: 只给第一个数据行 (最小的非0 r 值对应的 DSColumn 行) 加 ConditionAttr
# 因为 ConditionAttr 的 rowType="0" 表示应用到当前行, FR 会自动对所有同类型行生效

# 先找到所有非0行的 r 值及其单元格类型
cell_re = re.compile(
    r'<C\s+c="(\d+)"\s+r="(\d+)"(?:\s+cs="\d+")?\s*(?:\s+rs="\d+")?\s+s="(\d+)"[^>]*>(.*?)</C>',
    re.DOTALL)

cells_by_row = {}
for m in cell_re.finditer(content):
    col, row, style = m.group(1), m.group(2), m.group(3)
    inner = m.group(4)
    r = int(row)
    if r == 0:
        continue  # 跳过标题行
    is_ds = ('t="DSColumn"' in inner) or ('ds1.G(' in inner) or ('ds1.S(' in inner)
    if not is_ds and '=(' in inner:
        is_ds = True
    if r not in cells_by_row:
        cells_by_row[r] = []
    cells_by_row[r].append((col, style, m.group(0), is_ds))

# 找第一个数据行 (有 DSColumn 或公式的最小 r)
data_rows = sorted([r for r, cells in cells_by_row.items() 
                    if any(c[3] for c in cells)])
if not data_rows:
    # 没有明显 DSColumn，找 r>0 的最小行
    data_rows = sorted([r for r in cells_by_row.keys() if r > 0])

if data_rows:
    first_data_row = data_rows[0]
    print(f"第一个数据行: r={first_data_row}")
    
    # 只给第一行第一列的单元格加 ConditionAttr
    first_cell = cells_by_row[first_data_row][0]
    old = first_cell[2]
    
    # 检查是否已有 ConditionAttr
    if '<ConditionAttr>' not in old:
        # 在 </C> 之前插入 ConditionAttr (偶数行变色)
        new = old.replace('</C>', COND_EVEN + '</C>')
        content = content.replace(old, new)
        print(f"  已添加隔行换色到 r={first_data_row} c={first_cell[0]}")
else:
    print("未找到数据行")

# 写回
with open(FP, 'w', encoding='utf-8') as f:
    f.write(content)

# 验证
import xml.etree.ElementTree as ET
try:
    ET.fromstring(content)
    print("XML 验证通过 ✓")
except ET.ParseError as e:
    print(f"XML 错误: {e}")
