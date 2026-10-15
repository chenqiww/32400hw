"""Extract filled limit orders from a FIX log into CSV file."""
import argparse
import csv

CSV_COLUMNS = [
    "OrderID",
    "OrderTransactTime",
    "ExecutionTransactTime",
    "Symbol",
    "Side",
    "OrderQty",
    "LimitPrice",
    "AvgPx",
    "LastMkt",
]


def parse_fix_message(line):
    """Parse one log line into a dictionary of FIX tags and values."""
    fields = {}
    for field in line.rstrip("\n").split("\x01"):
        tag, separator, value = field.partition("=")
        if separator:
            fields[tag] = value
    return fields


def is_complete_limit_fill(fields):
    """Return whether a message reports a completely filled limit order."""
    return (
        fields.get("35") == "8"
        and fields.get("150") == "2"
        and fields.get("39") == "2"
        and fields.get("40") == "2"
    )


def convert_fix_to_csv(input_fix_file, output_csv_file):
    """Match complete fills to their original orders and write the CSV.

    Orders are assumed to appear in the log before their fills. Fills whose
    order is not in the log are skipped; a missing LastMkt is left blank.
    """
    orders = {}

    with (
        open(input_fix_file, "r", encoding="utf-8") as fix_file,
        open(output_csv_file, "w", newline="", encoding="utf-8") as csv_file,
    ):
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        for line in fix_file:
            fields = parse_fix_message(line)

            if fields.get("35") == "D" and fields.get("40") == "2":
                orders[fields["11"]] = fields
                continue

            if not is_complete_limit_fill(fields):
                continue

            order = orders.get(fields["11"])
            if order is None:
                continue

            writer.writerow(
                {
                    "OrderID": fields["11"],
                    "OrderTransactTime": order["60"],
                    "ExecutionTransactTime": fields["60"],
                    "Symbol": order["55"],
                    "Side": order["54"],
                    "OrderQty": order["38"],
                    "LimitPrice": order["44"],
                    "AvgPx": fields["6"],
                    "LastMkt": fields.get("30", ""),
                }
            )


def main():
    """Read command-line arguments and convert FIX messages to CSV."""
    parser = argparse.ArgumentParser(
        description="Convert complete limit-order fills from FIX to CSV."
    )
    parser.add_argument(
        "--input_fix_file", required=True, help="Path to the input FIX file."
    )
    parser.add_argument(
        "--output_csv_file", required=True, help="Path to the output CSV file."
    )
    args = parser.parse_args()

    convert_fix_to_csv(args.input_fix_file, args.output_csv_file)


if __name__ == "__main__":
    main()
