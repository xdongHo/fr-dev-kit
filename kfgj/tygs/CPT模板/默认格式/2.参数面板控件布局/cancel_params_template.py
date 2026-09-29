"""
取消使用常用参数组合（修复版 2026-08-05）。

FR 10.0 中「常用参数组合」由**两处** XML 控制，必须全部置 false 才真正取消：
  1. 参数面板 Layout 内:  <UseParamsTemplate use="true"/>  →  use="false"   （面板级开关）
  2. 报表参数属性:        ReportParameterAttr 的 Attributes 上
                         useParamsTemplate="true"            →  "false"     （报表级开关）

旧版 bug（导致"没生效"）：
  - 只替换属性版（第 2 处），Layout 标签版（第 1 处）不处理；
  - 提前返回判断 `if b'useParamsTemplate="false"' in raw` 会误判跳过——
    只要属性版已是 false（生成器默认产物），Layout 标签即使 true 也直接 return，实际没改。

用法:
    python cancel_params_template.py <cpt路径> [cpt路径...]
"""
import sys, os, shutil
from datetime import datetime

TAG_TRUE = b'<UseParamsTemplate use="true"/>'
TAG_FALSE = b'<UseParamsTemplate use="false"/>'
ATTR_TRUE = b'useParamsTemplate="true"'
ATTR_FALSE = b'useParamsTemplate="false"'


def cancel_params_template(cpt_path):
    if not os.path.exists(cpt_path):
        print(f"❌ 文件不存在: {cpt_path}")
        return False

    base = os.path.dirname(os.path.abspath(cpt_path))
    bak = os.path.join(base, f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(bak, exist_ok=True)
    shutil.copy2(cpt_path, os.path.join(bak, os.path.basename(cpt_path)))

    with open(cpt_path, 'rb') as f:
        raw = f.read()

    # 统计两处开关的现状
    n_tag_true = raw.count(TAG_TRUE)
    n_attr_true = raw.count(ATTR_TRUE)
    n_tag_false = raw.count(TAG_FALSE)
    n_attr_false = raw.count(ATTR_FALSE)

    if n_tag_true == 0 and n_attr_true == 0:
        print(f"ℹ️  两处均已是 false（标签×{n_tag_false} 属性×{n_attr_false}）: {os.path.basename(cpt_path)}")
        return False

    # 两处都替换
    changed = raw
    if n_tag_true:
        changed = changed.replace(TAG_TRUE, TAG_FALSE)
    if n_attr_true:
        changed = changed.replace(ATTR_TRUE, ATTR_FALSE)

    with open(cpt_path, 'wb') as f:
        f.write(changed)

    print(f"✅ 已取消常用参数组合: {os.path.basename(cpt_path)}"
          f"（Layout 标签×{n_tag_true}、属性×{n_attr_true} 已置 false）")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ok = 0
    for p in sys.argv[1:]:
        if cancel_params_template(p):
            ok += 1
    print(f"\n完成: {ok}/{len(sys.argv)-1} 个文件被修改")
