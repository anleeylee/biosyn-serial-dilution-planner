# BioSyn Serial Dilution Planner

> **Lab serial dilution planner** — input stock and target concentrations, get a step-by-step multi-tube dilution plan with safety checks.

## Overview

Tired of manually calculating each dilution step? **BioSyn Serial Dilution Planner** takes your starting concentration and target concentrations (or a fixed dilution factor) and generates a complete, tube-by-tube operation plan — with pipetting volumes, tube labels, and safety warnings when transfer volumes are too small.

> For online calculators, visit [BioSyn serial dilution calculator](https://biosyn-inc.com/tools/serial-dilution-calculator) — this is the desktop planning companion.

## Quick Start

```bash
git clone https://github.com/your-org/biosyn-serial-dilution-planner.git
cd biosyn-serial-dilution-planner
pip install -r requirements.txt

# 1:10 serial dilution, 5 tubes, 1000 µL each
python -m src.main factor --start 1000 --factor 10 --tubes 5 --volume 1000

# Custom target concentrations
python -m src.main targets --start 1000 --targets 100,10,1,0.1 --volume 500
```

## Methods

- `C1V1 = C2V2` → `V1 = C2 × V2 / C1`
- `DF = C1 / C2`
- Transfer volume below threshold → WARNING (does not change conditions)

## Disclaimer

Verify against your lab SOP before use. Not a validated SOP.

## Keywords

`serial dilution calculator`, `dilution planner`, `lab dilution tool`, `pipetting calculator`, `concentration series`, `serial dilution protocol`, `lab calculation`

## About

Built by [BioSyn Inc.](https://biosyn-inc.com/)

## License

[MIT](LICENSE)
