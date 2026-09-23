# Mileage Prediction Configuration

This folder contains the shared settings for the staged mileage-prediction
notebooks. Edit [config.py](config.py) when changing an analysis assumption.
The notebooks import the `config` package so that the same values are used
throughout the pipeline.

## How Settings Affect the Pipeline

### Paths and input data

| Setting              |                     Current value | Purpose and effect                                                                                                                                                                                                            |
| -------------------- | --------------------------------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PROJECT_ROOT`       |          Discovered automatically | Walks upward from the notebook's working directory until `dft_test_result_extracts_2020/` is found. This is the base for all raw and processed-data paths.                                                                    |
| `PROCESSED_DATA_DIR` | `PROJECT_ROOT / 'processed_data'` | Location for Parquet tables and JSON quality summaries produced by the notebooks. Changing it moves the pipeline outputs.                                                                                                     |
| `YEARS_TO_LOAD`      |             `2020` through `2025` | Controls which annual raw-data folders are loaded. It affects the available tests, intervals, histories, predictions, and evaluation periods. Every selected year needs a matching `dft_test_result_extracts_<year>/` folder. |
| `RAW_DATA_DIRS`      |        One path per selected year | Derived mapping from each year to its raw-data folder. Usually change `YEARS_TO_LOAD` rather than editing this directly.                                                                                                      |
| `REQUIRED_COLUMNS`   |   MOT fields used by the pipeline | Controls which columns are requested from raw CSV files. Add a field here before using it downstream. Removing a field can break cleaning, grouping, or traceability.                                                         |

`PROJECT_ROOT` falls back to the starting directory if the anchor folder is
not found. A fallback can result in missing-data errors, so run notebooks with
the project directory as their working directory when possible.

### Interval and data-quality rules

| Setting                          |          Current value | Purpose and effect                                                                                                                                                          |
| -------------------------------- | ---------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MIN_INTERVAL_DAYS`              |              `90` days | Shortest MOT-to-MOT interval considered valid for the main analysis. This excludes likely retests or mismatched pairs while retaining more coverage than a 9-month minimum. |
| `MAX_INTERVAL_DAYS`              | `15 * 30` = `450` days | Longest interval considered valid for the main analysis. Decreasing it selects more consistently annual intervals but excludes vehicles with longer gaps.                   |
| `MAX_INTERVAL_DAYS_FIRST_TEST`   |    `4 * 365 + 90` days | Longer maximum allowed for a vehicle's first-use-to-first-MOT interval, because the first MOT is normally due after three years.                                            |
| `IMPLAUSIBLE_ANNUALISED_MILEAGE` |   `100_000` miles/year | Annualised mileage above this value is flagged as suspicious, following the DfT-style cleaning rule for likely odometer or matching errors.                                 |
| `EXCLUDED_TEST_RESULTS`          |              `['PRS']` | Test results excluded before pairing. PRS is a remedial retest and should not become a vehicle's previous test or interrupt the genuine MOT sequence.                       |

The interval calculation is:

```text
annualised_mileage = miles_driven * 365.25 / days_between_tests
```

Intervals outside the configured range, decreasing or zero odometer movement,
and implausibly high annualised mileage should be flagged by the interval stage,
not silently treated as normal observations. PRS records are counted and
excluded before the interval sequence is constructed.

### Peer-group settings

| Setting                 |                            Current value | Purpose and effect                                                                                                                                                                                                                                 |
| ----------------------- | ---------------------------------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MIN_PEER_OBSERVATIONS` |                                     `50` | Minimum historical observations needed for a peer group. Increasing it makes peer statistics more stable but causes more fallback to broader groups or the overall population. Lowering it gives more specific groups but less reliable estimates. |
| `AGE_BINS`              |                 `[0, 3, 7, 12, 20, inf]` | Boundaries for vehicle-age bands used in peer matching and age-based evaluation. The resulting bands are approximately `0-3`, `4-7`, `8-12`, `13-20`, and `21+` years.                                                                             |
| `AGE_LABELS`            | `['0-3', '4-7', '8-12', '13-20', '21+']` | Names displayed for the age bands. Keep this list aligned with `AGE_BINS`; changing labels changes presentation, while changing bins changes membership.                                                                                           |

Peer statistics must use only observations available before each prediction
date. The peer fallback level should be recorded whenever a broader group is
used.

### Prediction and evaluation settings

| Setting                  |  Current value | Purpose and effect                                                                                                                                                                                                              |
| ------------------------ | -------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RECENT_WEIGHTS`         |    `[1, 2, 3]` | Weights historical intervals from oldest to newest for the recent-weighted vehicle prediction. The newest interval receives the greatest weight. Larger recent weights make predictions respond more quickly to changing usage. |
| `ERROR_THRESHOLDS_MILES` | `[1000, 2000]` | Absolute-error thresholds used for metrics such as percentage within 1,000 or 2,000 miles. These change how accuracy is reported, not the predictions themselves.                                                               |

For three intervals, the current recent-weighted calculation is:

```text
(1 * oldest + 2 * middle + 3 * newest) / 6
```

The weights should be positive and have one value for each historical interval
supported by the implementation. If the weighting approach changes, update
the explanation in the prediction notebook as well.

### Variation analysis settings

| Setting                               |  Current value | Purpose and effect                                                                                                                                                |
| ------------------------------------- | -------------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MIN_INTERVALS_FOR_VARIATION_PROFILE` |            `3` | Minimum valid intervals needed for a vehicle-level consistency profile. Increasing it improves the reliability of variation estimates but excludes more vehicles. |
| `VARIATION_CHANGE_THRESHOLDS_MILES`   | `[1000, 2000]` | Absolute year-to-year change thresholds. The variation analysis reports the share of changes exceeding each threshold.                                            |
| `VARIATION_CHANGE_THRESHOLDS_PERCENT` | `[0.25, 0.50]` | Relative change thresholds, representing 25% and 50%. Relative thresholds make changes comparable across low- and high-mileage vehicles.                          |

These settings affect which vehicles receive profiles and how variation is
summarised. They do not change the underlying interval values.

## Output Directory Helper

`ensure_processed_data_dir()` creates `processed_data/` and returns its
`Path`. It is a convenience for notebooks; it does not change any analysis
setting.

## Safe Change Checklist

1. Change one setting at a time and record the reason.
2. Check that every year in `YEARS_TO_LOAD` has its raw-data folder and files.
3. Keep `AGE_LABELS` aligned with `AGE_BINS`.
4. Re-run the affected notebook and all downstream notebooks, because earlier
   settings can change their input rows.
5. Compare record counts, history counts, peer fallback levels, and evaluation
   coverage before comparing accuracy.

The settings with the broadest effect are `YEARS_TO_LOAD`, the interval-day
limits, `IMPLAUSIBLE_ANNUALISED_MILEAGE`, `MIN_PEER_OBSERVATIONS`, and
`MIN_INTERVALS_FOR_VARIATION_PROFILE`.
