#!/usr/bin/env python3
"""
scripts/audit_privacy.py
========================
QuantPits-Arena 本地隐私与脱敏合规扫描器 (Zero-Leakage Local Auditor)

核心设计准则：
【零信息泄露原则 (Zero-Leakage Reporting)】
扫描器如果在文件中检出潜在敏感信息（例如真实个股代码、实盘账户余额、私有主机路径），
绝对禁止在 stdout/stderr、日志或终端中回显任何匹配到的明文敏感内容！
违规输出仅允许包含：触发规则类别、文件相对路径、违规行号、特征长度与截断哈希。
以此确保 CI/CD 构建日志、终端回显或 AI Agent 对话历史本身绝对不会构成二次泄密。

检查项：
1. 严禁任何模型二进制/权重文件被 Git 跟踪（.pkl, trained_model, .bin, .pt 等）
2. 严禁生产实盘私有状态文件或敏感字段入库（current_cash, current_holding 等）
3. 严禁未脱敏的真实 A 股个股标的代码出现在公开配置或报告中（市场指数代码如 SH000300 除外）
4. 严禁开发机私有绝对用户路径（/home/<user>/...）出现在公开文档或代码中
5. 严禁精确到分角的实盘资金余额零头出现在代码或文档中

退出码：
- 0: 全部合规 (PASS)
- 1: 存在脱敏违规项 (FAIL)
"""

import os
import sys
import re
import hashlib
import subprocess
from pathlib import Path

# 项目根目录
REPO_ROOT = Path(__file__).resolve().parent.parent

# 扫描的目标文本文件扩展名
TEXT_EXTENSIONS = {
    ".md", ".yaml", ".yml", ".json", ".py", ".sh", ".txt", ".csv", ".js", ".html", ".css"
}

# 必须排除的私有/动态目录（不纳入公开开源扫描）
IGNORE_DIRS = {
    ".git",
    "artifacts/models",
    "runs/*/predictions",
    "runs/*/private",
    "venv",
    ".venv",
    "__pycache__",
}

# 允许的例外文件（原始只读文档、脱敏审计脚本自身）
ALLOWED_FILE_EXCEPTIONS = {
    "REF.md",                  # 用户提供的原始只读环境引用
    "INIT.md",                 # 用户提供的原始只读需求
    "scripts/audit_privacy.py", # 审计工具自身（含正则定义）
}

# 允许的公开市场宽基指数代码（非个股持仓标的）
ALLOWED_MARKET_INDICES = {
    "SH000300", "SH000001", "SH000016", "SH000905", "SH000852",
    "SZ399001", "SZ399005", "SZ399006", "SZ399106", "SZ399300",
}

# ---------------------------------------------------------------------------
# 正则规则定义
# ---------------------------------------------------------------------------
# 1. 模型权重二进制后缀与特征文件名
FORBIDDEN_EXTENSIONS = {".pkl", ".pt", ".pth", ".bin", ".h5", ".joblib"}
FORBIDDEN_FILENAMES = {"trained_model"}

# 2. A 股股票代码正则（匹配标准 6 位标的代码，前缀或后缀标识）
RE_STOCK_TICKER = re.compile(
    r"\b([Ss][Hh]|[Ss][Zz]|[Bb][Jj])\d{6}\b|\b\d{6}\.([Ss][Hh]|[Ss][Zz]|[Bb][Jj])\b"
)

# 3. 生产账户私有状态字段关键字
RE_PROD_STATE_KEYS = re.compile(
    r"\b(current_holding|current_cash|current_full_cash|initial_holding|holding_log_full|trade_log_full|buy_suggestion|sell_suggestion)\b"
)

# 4. 精确到分角的账户资金金额模式（5位以上整数且精确带两位小数，例如 160610.43 等）
RE_PRECISE_DECIMAL_AMOUNT = re.compile(r"\b\d{5,}\.\d{2}\b")

# 5. 私有主机绝对主目录路径
RE_PRIVATE_HOME_PATH = re.compile(r"/home/[a-zA-Z0-9_\-\.]+/(?!src/QuantPits-Arena)")

# 6. 真实模型身份关键词（在公开文件中检测是否残留真实模型名）
#    注意：将模式串拆分存放以避免扫描器自身被误报
_MODEL_ID_PARTS = [
    # 生产 ensemble 代号
    "Defensive" + "_V2", "different" + "_one", "good" + "_model",
    # 真实模型类名
    "TRAModel" + "IC", "LSTMICMo" + "del", "CatBoost" + "Model",
    "LGBMo" + "del", "ADA" + "RNN", "IGM" + "TF",
    # 框架/系统名
    "QuantPits" + "_Release", "quantpits" + "_static", "quantpits" + "_cpcv",
]
RE_MODEL_IDENTITY = re.compile("|".join(re.escape(p) for p in _MODEL_ID_PARTS), re.IGNORECASE)


def make_safe_fingerprint(matched_text: str) -> str:
    """
    生成零泄密的安全特征指纹：仅显示长度和 SHA256 截断前缀，
    开发者可在本地核验，但绝不会在日志中暴露原始字符。
    """
    digest = hashlib.sha256(matched_text.encode("utf-8", errors="ignore")).hexdigest()
    return f"len={len(matched_text)}, sha256_prefix={digest[:8]}"


def is_ignored_path(path: Path) -> bool:
    """判断路径是否属于被排除的目录"""
    rel_str = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    
    parts = rel_str.split("/")
    if ".git" in parts or "__pycache__" in parts:
        return True
    
    if rel_str.startswith("artifacts/models") or rel_str.startswith("artifacts/configs"):
        return True
    
    if rel_str.startswith("manifests/private"):
        return True
    
    if rel_str.startswith("docs/internal"):
        return True
    
    if "/private" in rel_str or "/predictions" in rel_str or "/monkeys" in rel_str:
        return True
        
    return False


def get_git_tracked_files():
    """获取所有被 git 跟踪以及 staged 的文件列表"""
    try:
        res = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return [f.strip() for f in res.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def scan_file(file_path: Path):
    """单文件脱敏合规扫描（零信息泄露）"""
    violations = []
    rel_str = str(file_path.relative_to(REPO_ROOT)).replace("\\", "/")
    
    # 检查例外文件
    if rel_str in ALLOWED_FILE_EXCEPTIONS:
        return violations

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_idx, line in enumerate(f, start=1):
                # 规则 2: 股票代码扫描（排除指数代码与脱敏占位符）
                for match in RE_STOCK_TICKER.finditer(line):
                    ticker = match.group(0).upper()
                    if ticker in ALLOWED_MARKET_INDICES:
                        continue
                    if "STOCK_" in line or "SH6XXXXX" in line.upper() or "SZ0XXXXX" in line.upper():
                        continue
                    violations.append({
                        "rule": "RULE_02_STOCK_TICKER",
                        "desc": "发现疑似真实个股证券代码（市场宽基指数代码除外）",
                        "file": rel_str,
                        "line": line_idx,
                        "fingerprint": make_safe_fingerprint(ticker),
                    })

                # 规则 3: 生产私有状态键名扫描
                for match in RE_PROD_STATE_KEYS.finditer(line):
                    key_name = match.group(0)
                    violations.append({
                        "rule": "RULE_03_PROD_STATE_KEY",
                        "desc": "包含生产实盘私有账户状态字段关键字",
                        "file": rel_str,
                        "line": line_idx,
                        "fingerprint": make_safe_fingerprint(key_name),
                    })

                # 规则 4: 精确账户资金数额扫描
                for match in RE_PRECISE_DECIMAL_AMOUNT.finditer(line):
                    amount_str = match.group(0)
                    violations.append({
                        "rule": "RULE_04_PRECISE_CASH_BALANCE",
                        "desc": "包含疑似精确到分角的实盘资金余额或流水零头",
                        "file": rel_str,
                        "line": line_idx,
                        "fingerprint": make_safe_fingerprint(amount_str),
                    })

                # 规则 5: 私有主机绝对路径扫描
                for match in RE_PRIVATE_HOME_PATH.finditer(line):
                    path_str = match.group(0)
                    # 忽略以相对占位表示的说明
                    if "/home/<" in line:
                        continue
                    violations.append({
                        "rule": "RULE_05_PRIVATE_HOME_PATH",
                        "desc": "包含本地私有绝对开发机用户路径",
                        "file": rel_str,
                        "line": line_idx,
                        "fingerprint": make_safe_fingerprint(path_str),
                    })

                # 规则 6: 真实模型身份关键词扫描
                match_model = RE_MODEL_IDENTITY.search(line)
                if match_model:
                    violations.append({
                        "rule": "RULE_06_MODEL_IDENTITY",
                        "desc": "公开文件中发现疑似真实模型名称/类名/生产系统名",
                        "file": rel_str,
                        "line": line_idx,
                        "fingerprint": make_safe_fingerprint(match_model.group(0)),
                    })
    except Exception:
        pass

    return violations


def audit_repository():
    """主审计流程"""
    print("=" * 70)
    print(" 🛡️  QuantPits-Arena 本地隐私与脱敏合规审计 (Zero-Leakage Mode)")
    print("    [安全规范：检测到违规时严格禁止在终端打印任何明文敏感数据]")
    print("=" * 70)

    violations = []

    # 1. 检查 Git 跟踪清单中的禁用文件
    tracked_files = get_git_tracked_files()
    for rel_str in tracked_files:
        p = Path(rel_str)
        if p.suffix.lower() in FORBIDDEN_EXTENSIONS or p.name in FORBIDDEN_FILENAMES:
            violations.append({
                "rule": "RULE_01_FORBIDDEN_MODEL_BINARY",
                "desc": "模型二进制权重文件被 Git 跟踪（模型绝对禁止入库）",
                "file": rel_str,
                "line": 0,
                "fingerprint": f"Ext={p.suffix}, Name={p.name}",
            })
        if rel_str.startswith("artifacts/models/"):
            violations.append({
                "rule": "RULE_01_MODEL_DIR_TRACKED",
                "desc": "artifacts/models/ 目录下的文件被 Git 跟踪",
                "file": rel_str,
                "line": 0,
                "fingerprint": f"TrackedPath={rel_str}",
            })

    # 2. 遍历扫描所有待公开/已公开的文本文件
    scanned_files = 0
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if not is_ignored_path(Path(root) / d)]
        for file_name in files:
            file_path = Path(root) / file_name
            if is_ignored_path(file_path):
                continue
            if file_path.suffix in TEXT_EXTENSIONS or file_name in {"Makefile", "Dockerfile"}:
                scanned_files += 1
                v = scan_file(file_path)
                violations.extend(v)

    print(f"\n[INFO] 已合规扫描工作区文本文件数: {scanned_files} 个")

    # 3. 结果汇总
    if not violations:
        print("\n" + "─" * 70)
        print(" ✅ 审计通过 (AUDIT PASSED): 仓库状态完全满足公开开源脱敏要求！")
        print("    ✔ 0 处模型二进制权重泄露")
        print("    ✔ 0 处真实实盘账户资金/现金流指纹")
        print("    ✔ 0 处未脱敏个股标的代码")
        print("    ✔ 0 处私有开发机绝对用户路径")
        print("    ✔ 0 处真实模型身份/架构泄露")
        print("─" * 70 + "\n")
        return True
    else:
        print("\n" + "─" * 70)
        print(f" ❌ 审计失败 (AUDIT FAILED): 发现 {len(violations)} 处脱敏合规风险！")
        print("    【安全提醒：下表仅输出违规位置与指纹，绝不泄露原始内容】")
        print("─" * 70)
        for idx, item in enumerate(violations, start=1):
            print(f"[{idx:02d}] {item['rule']} | {item['desc']}")
            print(f"     位置: {item['file']}:{item['line']}")
            print(f"     指纹: [{item['fingerprint']}]")
            print("─" * 70)
        print("\n整改提示：请根据上述 [文件:行号] 逐项就地清理敏感数据，然后重新运行本工具。")
        print("运行命令: python3 scripts/audit_privacy.py\n")
        return False


if __name__ == "__main__":
    success = audit_repository()
    sys.exit(0 if success else 1)
