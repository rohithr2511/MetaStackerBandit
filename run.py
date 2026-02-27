import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def setup_logger(log_file: str):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )


def write_metrics(output_path: str, payload: dict):
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)


def load_and_validate_config(config_path: str) -> dict:
    if not Path(config_path).exists():
        raise FileNotFoundError("Config file not found")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError("Invalid config structure")

    for key in ["seed", "window", "version"]:
        if key not in config:
            raise ValueError(f"Missing config field: {key}")

    if not isinstance(config["window"], int) or config["window"] <= 0:
        raise ValueError("window must be a positive integer")

    return config


def load_and_validate_data(input_path: str) -> pd.DataFrame:
    if not Path(input_path).exists():
        raise FileNotFoundError("Input CSV file not found")

    try:
        df = pd.read_csv(input_path)
    except Exception:
        raise ValueError("Invalid CSV format")
        
    df.columns = df.columns.str.strip().str.lower()

    if df.empty:
        raise ValueError("Input CSV is empty")

    if "close" not in df.columns:
        raise ValueError("Missing required column: close")

    return df


def main():
    parser = argparse.ArgumentParser(description="Minimal MLOps batch job")
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)
    args = parser.parse_args()

    start_time = time.time()

    try:
        setup_logger(args.log_file)
        logging.info("Job started")

        # Load config
        config = load_and_validate_config(args.config)
        logging.info(
            f"Config loaded | seed={config['seed']} window={config['window']} version={config['version']}"
        )

        # Determinism
        np.random.seed(config["seed"])

        # Load data
        df = load_and_validate_data(args.input)
        logging.info(f"Rows loaded: {len(df)}")

        # Rolling mean
        logging.info("Computing rolling mean")
        rolling_mean = df["close"].rolling(window=config["window"]).mean()

        # Signal generation
        logging.info("Generating signals")
        signal = (df["close"] > rolling_mean).astype(int)
        signal = signal.fillna(0)

        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": config["version"],
            "rows_processed": int(len(df)),
            "metric": "signal_rate",
            "value": float(signal.mean()),
            "latency_ms": latency_ms,
            "seed": config["seed"],
            "status": "success",
        }

        write_metrics(args.output, metrics)

        logging.info(f"Metrics summary: {metrics}")
        logging.info("Job finished successfully")

        # Required: print final metrics to stdout
        print(json.dumps(metrics, indent=2))
        sys.exit(0)

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)

        error_metrics = {
            "version": "v1",
            "status": "error",
            "error_message": str(e),
        }

        try:
            write_metrics(args.output, error_metrics)
        except Exception:
            pass

        logging.exception("Job failed")
        print(json.dumps(error_metrics, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()