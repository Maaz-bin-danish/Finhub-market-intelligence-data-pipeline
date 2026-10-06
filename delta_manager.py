from pathlib import Path
import pandas as pd


DELTA_DIR = Path("data/delta")
DELTA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def detect_new_records(
    new_data,
    endpoint,
    unique_columns
):

    if not new_data:
        return []



    new_df = pd.DataFrame(new_data)

    for column in unique_columns:

        new_df[column] = (
            new_df[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

    # -----------------------------
    # DELTA HISTORY FILE
    # -----------------------------

    existing_file = (
        DELTA_DIR / f"{endpoint}.csv"
    )

    # -----------------------------
    # FIRST RUN
    # -----------------------------

    if not existing_file.exists():

        new_df.to_csv(
            existing_file,
            index=False
        )

        print(
            f"[DELTA] First run: "
            f"{len(new_df)} records stored."
        )

        return new_data

    # -----------------------------
    # LOAD EXISTING DATA
    # -----------------------------

    existing_df = pd.read_csv(
        existing_file,
        dtype=str,
        keep_default_na=False
    )

    # -----------------------------
    # NORMALIZE EXISTING KEYS
    # -----------------------------

    for column in unique_columns:

        existing_df[column] = (
            existing_df[column]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    # -----------------------------
    # FIND NEW RECORDS
    # -----------------------------

    comparison = new_df.merge(
        existing_df[unique_columns]
            .drop_duplicates(),

        on=unique_columns,

        how="left",

        indicator=True
    )

    new_records_df = comparison[
        comparison["_merge"] == "left_only"
    ].drop(
        columns=["_merge"]
    )

    # -----------------------------
    # NOTHING NEW
    # -----------------------------

    if new_records_df.empty:

        print(
            "[DELTA] No new records found."
        )

        return []

    # -----------------------------
    # UPDATE DELTA HISTORY
    # -----------------------------

    updated_df = pd.concat(
        [
            existing_df,
            new_records_df
        ],
        ignore_index=True
    )

    updated_df.drop_duplicates(
        subset=unique_columns,
        inplace=True
    )

    updated_df.to_csv(
        existing_file,
        index=False
    )

    print(
        f"[DELTA] "
        f"{len(new_records_df)} new records found."
    )

    return new_records_df.to_dict(
        orient="records"
    )