import torch

from torch.utils.data import DataLoader, random_split

from ml.dataset import AudioDataset


class AudioDataLoaders:
    """Creates train, validation and test data loaders."""

    TRAIN_RATIO = 0.8
    VALIDATION_RATIO = 0.1
    TEST_RATIO = 0.1

    def __init__(
        self,
        dataset_path: str,
        batch_size: int = 32,
        seed: int = 42
    ) -> None:
        self.dataset = AudioDataset(
            dataset_path
        )

        self.batch_size = batch_size
        self.seed = seed

    def create(
        self
    ) -> tuple[
        DataLoader,
        DataLoader,
        DataLoader
    ]:
        """Create train, validation and test loaders."""

        total_size = len(self.dataset)

        train_size = int(
            total_size * self.TRAIN_RATIO
        )

        validation_size = int(
            total_size * self.VALIDATION_RATIO
        )

        test_size = (
            total_size
            - train_size
            - validation_size
        )

        generator = torch.Generator().manual_seed(
            self.seed
        )

        train_dataset, validation_dataset, test_dataset = (
            random_split(
                self.dataset,
                [
                    train_size,
                    validation_size,
                    test_size
                ],
                generator=generator
            )
        )

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True
        )

        validation_loader = DataLoader(
            validation_dataset,
            batch_size=self.batch_size,
            shuffle=False
        )

        test_loader = DataLoader(
            test_dataset,
            batch_size=self.batch_size,
            shuffle=False
        )

        return (
            train_loader,
            validation_loader,
            test_loader
        )
    