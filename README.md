# BioSyn Serial Dilution Planner

> **梯度稀释操作计划生成器** — 输入起始浓度和目标浓度，自动生成完整的多管稀释操作步骤，含安全检查和试管标签。
>
> A lab serial dilution planner: input stock and target concentrations, get a step-by-step multi-tube dilution plan with pipetting volumes, tube labels, and safety warnings.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 核心功能

| 功能 | 说明 |
|------|------|
| **三种模式** | A: 浓度序列 / B: 固定稀释因子（如 1:10）/ C: 自定义目标浓度 |
| **操作计划** | 逐管显示：从哪取、转多少 µL、加多少稀释液、最终浓度 |
| **安全检查** | 自动检测转移体积过小、稀释倍数过大、储备液不足等问题 |
| **试管标签** | 自动生成 S01-T01、S01-T02 格式标签 |
| **反向计算** | 已知目标浓度和体积，反推储备液和稀释液用量 |
| **单位统一** | 自动处理 µg/mL、mg/mL、g/L、M、mM 等单位 |
| **多格式导出** | XLSX（5 个 Sheet）、CSV |
| **完全离线** | 纯数学计算，不上传任何数据 |

## 解决的痛点

做梯度稀释时，每次都要手动算每管加多少 µL 原液、加多少稀释液，算错了整组实验就废了。BioSyn Serial Dilution Planner 自动生成完整操作表，并在转移体积太小时发出警告。

> 在线稀释计算工具请访问 [BioSyn 梯度稀释计算器](https://biosyn-inc.com/tools/serial-dilution-calculator) — 本工具是其桌面端批量规划增强版。

## 依赖与安装

### 环境要求

- **Python 3.10+**

### 依赖包

| 包 | 用途 | 是否必需 |
|------|------|----------|
| `openpyxl` | XLSX 报告导出 | 必需 |
| `reportlab` | PDF 打印版操作表（计划中） | 可选 |

> 核心计算引擎（C1V1=C2V2、稀释因子、单位换算）**仅依赖 Python 标准库**。

### 安装指令

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/biosyn-serial-dilution-planner.git
cd biosyn-serial-dilution-planner

# 2. 安装依赖
pip install -r requirements.txt

# 3. 模式 B: 固定稀释因子 (1:10, 5管, 每管1000µL)
python -m src.main factor --start 1000 --factor 10 --tubes 5 --volume 1000 --name Standard

# 模式 C: 自定义目标浓度
python -m src.main targets --start 1000 --targets 100,10,1,0.1 --volume 500 --name MySample
```

## 输出示例

```
Tube 1: Source: Stock,  Transfer: 100 µL, Diluent: 900 µL, → 100.0 µg/mL
Tube 2: Source: Tube 1, Transfer: 100 µL, Diluent: 900 µL, → 10.0 µg/mL
Tube 3: Source: Tube 2, Transfer: 100 µL, Diluent: 900 µL, → 1.0 µg/mL
```

## 计算方法

```
C1V1 = C2V2  →  V1 = C2 × V2 / C1
稀释倍数: DF = C1 / C2
```

## 安全边界

> Verify the calculated preparation plan against your laboratory SOP, reagent compatibility, and instrument/pipetting constraints before use. 本工具只负责数学规划，不替代经过验证的 SOP。

## Keywords

`serial dilution calculator`, `dilution planner`, `lab dilution tool`, `pipetting calculator`, `concentration series`, `serial dilution protocol`, `lab calculation tool`, `dilution factor calculator`

## About

By [BioSyn Inc.](https://biosyn-inc.com/) — explore more [serial dilution and lab calculation tools](https://biosyn-inc.com/tools/serial-dilution-calculator).

## License

[MIT](LICENSE)
