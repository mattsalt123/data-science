# Mileage Analysis

This project contains a Jupyter notebook that analyses 2025 vehicle test data and estimates annualised mileage as a lifetime proxy:

```text
annual_mileage = test_mileage / vehicle_age_years
```

The notebook reports percentile-filtered mileage summaries by postcode area and vehicle age band.

## Requirements

- macOS, or another system with Python 3.14 available
- VS Code with the Python and Jupyter extensions
- The 2025 CSV extracts in `dft_test_result_extracts_2025/`

## Setup From Scratch

Open a terminal in this project directory:

```bash
cd "/Users/matthewsalter/Documents/Development/eVED work/data-science"
```

Create a project virtual environment:

```bash
python3 -m venv .venvdatascience
```

Install the notebook dependencies:

```bash
.venvdatascience/bin/python -m pip install --upgrade pip
.venvdatascience/bin/python -m pip install ipykernel pandas numpy
```

This installs packages into the project environment and does not modify system Python packages.

## Configure VS Code

1. Open `mileage_analysis_percentile.ipynb` in VS Code.
2. Select the notebook kernel in the top-right corner.
3. Choose the interpreter from `.venvdatascience`.
4. Run the cells from top to bottom.

The environment does not need to be activated for the notebook. For terminal work, activate it with:

```bash
source .venvdatascience/bin/activate
```

A prompt beginning with `(.venvdatascience)` confirms that it is active. To leave it, run:

```bash
deactivate
```

## Data Layout

The project should contain the notebook and the 2025 extracts like this:

```text
.
├── mileage_analysis_percentile.ipynb
└── dft_test_result_extracts_2025/
    ├── dft_test_result_extract_202501.csv
    ├── dft_test_result_extract_202502.csv
    ├── ...
    └── dft_test_result_extract_202512.csv
```

The current notebook configuration looks for the CSV files in its working directory. Because the extracts are stored in `dft_test_result_extracts_2025/`, set the `data_dir` value in the configuration cell to:

```python
data_dir = Path(os.getcwd()) / "dft_test_result_extracts_2025"
```

Run the notebook with the project folder as its working directory so that the relative paths resolve correctly.

## Current Configuration

The notebook currently uses:

- 5th percentile lower mileage cutoff
- No upper percentile cutoff
- Minimum vehicle age of 0.5 years
- Minimum postcode group size of 100 tests

These values can be changed in the configuration cell.

## Troubleshooting

### `ModuleNotFoundError: No module named 'pandas'`

Make sure the notebook is using the `.venvdatascience` kernel. Then install the packages again from the project directory:

```bash
.venvdatascience/bin/python -m pip install ipykernel pandas numpy
```

### `source: no such file or directory`

Run the activation command from the project directory, or use the full path:

```bash
source "/Users/matthewsalter/Documents/Development/eVED work/data-science/.venvdatascience/bin/activate"
```

### `python: command not found`

Use the environment's Python directly:

```bash
.venvdatascience/bin/python --version
```

### Missing CSV file errors

Check that all twelve 2025 files are present in `dft_test_result_extracts_2025/` and that the notebook's `data_dir` points to that folder.
