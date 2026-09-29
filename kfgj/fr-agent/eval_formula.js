/*
 * eval_formula.js — FR 公式模拟计算验证（借鉴 FR AI 助手 FormulaTools「模拟计算」）
 *
 * AI 助手做法：公式生成后调用工具在 FR 引擎里实际模拟计算，验证合法性，不合法自动纠正。
 * 我们落地：通过 fr-agent /exec（Nashorn）调用 FR Calculator 引擎求值，开发前/生成后验证公式。
 *
 * 用法（设计器运行 + fr-agent 注入后，脚本 return 验证结果字符串）：
 *   curl -X POST http://localhost:19000/exec -d @<(
 *     python -c "import json;print(json.dumps({'script':open(r'fr-agent/eval_formula.js',encoding='utf-8').read()}))")
 *
 * 依赖经验（AGENTS.md doc-810/1191）：
 *   com.fr.script.Calculator.createCalculator().evalValue("<公式串>") 即可求值，
 *   无需 WorkBook/Workspace；断言先判 com.fr.stable.Primitive 三态(NULL/ERROR_VALUE/ERROR_NAME)。
 *
 * 用法二（传入自定义公式）：把 formulas 数组替换成要验证的公式，或仿照下方逐个调用。
 */
(function () {
    var Calculator = Java.type("com.fr.script.Calculator");
    var Primitive = Java.type("com.fr.stable.Primitive");

    var formulas = [
        // 示例：把要验证的公式放这里
        "SUM(A1:A5)",
        "IF($lang=\"US\",\"Test\",\"测试\")"
    ];

    var out = [];
    var calc = Calculator.createCalculator();
    for (var i = 0; i < formulas.length; i++) {
        var f = formulas[i];
        try {
            var v = calc.evalValue(f);
            var state;
            if (v === null) state = "NULL";
            else if (v instanceof Primitive && (v.isError() || v.isErrorValue())) state = "ERROR";
            else state = "OK";
            out.push("[eval_formula] " + f + "  =>  " + state + "  value=" + v);
        } catch (e) {
            out.push("[eval_formula] " + f + "  =>  EXCEPTION: " + e);
        }
    }
    out.push("[eval_formula] DONE");
    return out.join("\n");
})();
