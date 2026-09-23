"""Convert one large or several partitioned extracts into monthly CSV files."""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


csv.field_size_limit(sys.maxsize)


OUTPUT_COLUMNS = [
    "test_id",
    "vehicle_id",
    "test_date",
    "test_class_id",
    "test_type",
    "test_result",
    "test_mileage",
    "postcode_area",
    "make",
    "model",
    "colour",
    "fuel_type",
    "cylinder_capacity",
    "first_use_date",
    "completed_date",
]


def convert_files(input_paths: list[Path], output_dir: Path, delimiter: str) -> Counter:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    counts = Counter()

    try:
        for input_path in input_paths:
            with input_path.open("r", encoding="utf-8-sig", newline="") as source:
                reader = csv.reader(source, delimiter=delimiter)
                source_header = next(reader)

                if source_header != OUTPUT_COLUMNS[:-1]:
                    raise ValueError(
                        f"Unexpected columns in {input_path}. Expected: "
                        + delimiter.join(OUTPUT_COLUMNS[:-1])
                    )

                for row_number, raw_line in enumerate(source, start=2):
                    # A 2020 record contains a backslash-escaped quote; normalise it before parsing.
                    row = next(csv.reader([raw_line.replace(r'\"', '""')], delimiter=delimiter))
                    if len(row) != len(source_header):
                        raise ValueError(
                            f"{input_path}, row {row_number} has {len(row)} fields; "
                            f"expected {len(source_header)}"
                        )

                    month = row[2][:7]
                    if len(month) != 7 or month[4] != "-":
                        raise ValueError(
                            f"{input_path}, row {row_number} has an invalid test_date: {row[2]!r}"
                        )

                    if month not in files:
                        output_path = output_dir / f"dft_test_result_extract_{month.replace('-', '')}.csv"
                        handle = output_path.open("w", encoding="utf-8", newline="")
                        writer = csv.writer(handle, lineterminator="\n")
                        writer.writerow(OUTPUT_COLUMNS)
                        files[month] = (handle, writer)

                    files[month][1].writerow(row + [""])
                    counts[month] += 1
    finally:
        for handle, _ in files.values():
            handle.close()

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert one or more MOT extracts into monthly CSV files."
    )
    parser.add_argument("input", type=Path, help="Path to a CSV file or folder of CSV files")
    parser.add_argument("output_dir", type=Path, help="Directory for monthly CSV files")
    args = parser.parse_args()

    if args.input.is_dir():
        input_paths = sorted(args.input.glob("*.csv"))
        if not input_paths:
            raise ValueError(f"No CSV files found in {args.input}")
        delimiter = ","
    else:
        input_paths = [args.input]
        delimiter = "|"

    counts = convert_files(input_paths, args.output_dir, delimiter)
    total = sum(counts.values())
    print(f"Converted {total:,} data rows into {len(counts)} monthly files.")
    for month in sorted(counts):
        print(f"{month}: {counts[month]:,} rows")


if __name__ == "__main__":
    main()