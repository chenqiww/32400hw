"""Calculate average price improvement and execution speed by exchange."""

import argparse

import pandas as pd

TIME_FORMAT = "%Y%m%d-%H:%M:%S.%f"

def calculate_metrics(input_csv_file, output_metrics_file):
    """Load executions, calculate per-exchange metrics, and save the CSV."""
    executions = pd.read_csv(input_csv_file)

    order_times = pd.to_datetime(executions["OrderTransactTime"], format=TIME_FORMAT)
    execution_times = pd.to_datetime(
        executions["ExecutionTransactTime"], format=TIME_FORMAT
    )
    executions["ExecSpeedSecs"] = (execution_times - order_times).dt.total_seconds()

    buy_improvement = executions["LimitPrice"] - executions["AvgPx"]
    executions["PriceImprovement"] = buy_improvement.where(
        executions["Side"] == 1, -buy_improvement
    )

    metrics = executions.groupby("LastMkt", as_index=False).agg(
        AvgPriceImprovement=("PriceImprovement", "mean"),
        AvgExecSpeedSecs=("ExecSpeedSecs", "mean"),
    )
    metrics.to_csv(output_metrics_file, index=False)


def main():
    """Read command-line arguments and calculate exchange metrics."""
    parser = argparse.ArgumentParser(
        description="Calculate average price improvement and execution speed."
    )
    parser.add_argument(
        "--input_csv_file", required=True, help="Path to the input executions CSV."
    )
    parser.add_argument(
        "--output_metrics_file",
        required=True,
        help="Path to the output exchange metrics CSV.",
    )
    args = parser.parse_args()

    calculate_metrics(args.input_csv_file, args.output_metrics_file)


if __name__ == "__main__":
    main()
