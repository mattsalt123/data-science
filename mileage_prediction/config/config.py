"""Shared configuration for the mileage_prediction notebook pipeline.

Every notebook in this pipeline imports this file instead of retyping these
values, so a single change here (for example, a different valid-interval
window) is picked up by every notebook automatically.
"""

from pathlib import Path


def _find_project_root(start: Path) -> Path:
    """Walk upward from `start` until the folder holding the raw MOT extracts is found."""
    for candidate in [start, *start.parents]:
        if (candidate / 'dft_test_result_extracts_2020').exists():
            return candidate
    # Fall back to the starting directory if the anchor folder can't be found.
    return start


PROJECT_ROOT = _find_project_root(Path.cwd())
PROCESSED_DATA_DIR = PROJECT_ROOT / 'processed_data'

# The six-year period the whole pipeline is built around.
YEARS_TO_LOAD = [2020, 2021, 2022, 2023, 2024, 2025]

RAW_DATA_DIRS = {
    year: PROJECT_ROOT / f'dft_test_result_extracts_{year}' for year in YEARS_TO_LOAD
}

# Columns loaded from each raw CSV extract.
REQUIRED_COLUMNS = [
    'test_id', 'vehicle_id', 'test_date', 'test_mileage', 'make', 'model',
    'fuel_type', 'postcode_area', 'first_use_date', 'test_type', 'test_result',
    'test_class_id', 'completed_date',
]

# The main "valid interval" window used throughout the pipeline, in days.
MIN_INTERVAL_DAYS = 90
MAX_INTERVAL_DAYS = 15 * 30

# A vehicle's very first MOT test isn't due until 3 years after first use, so its
# "interval" (first_use_date to first test) is expected to be much longer than a normal
# 15-month gap without implying the vehicle sat SORN for a long stretch. MIN_INTERVAL_DAYS
# isn't applied to it either, since an early first test is still a genuine driven interval.
MAX_INTERVAL_DAYS_FIRST_TEST = 4 * 365 + 90

# PRS is a same-station remedial retest, not a separate driving period.
EXCLUDED_TEST_RESULTS = ['PRS']

# An annualised mileage above this is treated as implausible / a likely data error.
IMPLAUSIBLE_ANNUALISED_MILEAGE = 100_000

# Similar-vehicle (peer) group settings.
MIN_PEER_OBSERVATIONS = 50
AGE_BINS = [0, 3, 7, 12, 20, float('inf')]
AGE_LABELS = ['0-3', '4-7', '8-12', '13-20', '21+']

# Benchmark prediction settings.
RECENT_WEIGHTS = [1, 2, 3]
ERROR_THRESHOLDS_MILES = [1000, 2000]

# Year-to-year variation settings.
MIN_INTERVALS_FOR_VARIATION_PROFILE = 3
VARIATION_CHANGE_THRESHOLDS_MILES = [1000, 2000]
VARIATION_CHANGE_THRESHOLDS_PERCENT = [0.25, 0.50]

# A vehicle's consistency category is descriptive, not definitive; boundaries are on
# relative variation (interquartile range / median annualised mileage).
CONSISTENCY_CATEGORY_MAX_RELATIVE_VARIATION = {
    'Very consistent': 0.15,
    'Usually consistent': 0.35,
    # Anything above the highest threshold above is labelled 'Variable'.
}


def ensure_processed_data_dir() -> Path:
    """Create processed_data/ if it doesn't exist yet and return its path."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return PROCESSED_DATA_DIR