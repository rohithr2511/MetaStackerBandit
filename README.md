# MLOps Technical Assessment – Batch Signal Job

## Overview
This project implements a minimal MLOps-style batch job in Python.  
It demonstrates:

- Reproducibility via configuration and fixed random seed
- Observability through structured logs and machine-readable metrics
- Deployment readiness via Dockerized, one-command execution

The job processes OHLCV market data, computes a rolling mean on the close price, generates binary trading signals, and outputs metrics describing the run.

---

## Project Structure

```
.
├── run.py
├── config.yaml
├── data.csv
├── requirements.txt
├── Dockerfile
├── README.md
├── metrics.json
└── run.log
```

> `metrics.json` and `run.log` are sample outputs from a successful execution and are overwritten on each run.

---

## Configuration

`config.yaml` controls reproducibility and behavior.

```yaml
seed: 42
window: 5
version: "v1"
```

---

## Local Execution

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the job
```bash
python run.py \
  --input data.csv \
  --config config.yaml \
  --output metrics.json \
  --log-file run.log
```

Outputs:
- metrics.json
- run.log
- Metrics JSON printed to stdout

---

## Docker Execution

### Build image
```bash
docker build -t mlops-task .
```

### Run container
```bash
docker run --rm mlops-task
```

The container:
- Uses bundled data and config
- Writes metrics.json and run.log
- Prints metrics to stdout
- Exits with code 0 on success

---

## Metrics Output

Example successful output:

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4989,
  "latency_ms": 16,
  "seed": 42,
  "status": "success"
}
```

On failure, metrics.json still contains:
- version
- status: "error"
- error_message

---

## Logging

Logs include:
- Job lifecycle events
- Configuration details
- Data validation
- Processing steps
- Metrics summary
- Error traces if failures occur

All logs are written to `run.log`.

---

## Notes
- Deterministic and reproducible
- No hardcoded paths
- Docker-ready batch workflow
- Production-style MLOps structure
