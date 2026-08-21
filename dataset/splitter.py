from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


class DatasetSplitter:
    """Splits dataset into train, validation and test sets."""

    TRAIN_RATIO = 0.70
    VALIDATION_RATIO = 0.15
    TEST_RATIO = 0.15

    def split_by_source(
        self,
        input_path: str,
        output_dir: str
    ) -> None:
        """Split dataset without leaking variants of the same source."""

        input_file = Path(input_path)
        output_directory = Path(output_dir)

        data = pd.read_csv(input_file)

        if data.empty:
            raise ValueError("Dataset is empty.")

        source_files = data["filename"].str.replace(
            r"_\d+db$",
            "",
            regex=True
        )

        unique_sources = source_files.unique()

        train_sources, temp_sources = train_test_split(
            unique_sources,
            test_size=0.30,
            random_state=42,
            shuffle=True
        )

        validation_sources, test_sources = train_test_split(
            temp_sources,
            test_size=0.50,
            random_state=42,
            shuffle=True
        )

        train = data[
            source_files.isin(train_sources)
        ]

        validation = data[
            source_files.isin(validation_sources)
        ]

        test = data[
            source_files.isin(test_sources)
        ]

        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        train.to_csv(
            output_directory / "train.csv",
            index=False
        )

        validation.to_csv(
            output_directory / "validation.csv",
            index=False
        )

        test.to_csv(
            output_directory / "test.csv",
            index=False
        )
