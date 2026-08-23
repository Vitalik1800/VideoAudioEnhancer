import torch

from ml.loss import GainLoss
from ml.model import GainPredictor
from ml.optimizer import GainOptimizer

from pathlib import Path


class Trainer:
    """Trains the gain prediction model."""

    def __init__(
            self,
            model: GainPredictor,
            optimizer: GainOptimizer,
            loss_function: GainLoss,
            model_path: str = "models/audio_gain_model.pth"
    ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.loss_function = loss_function
        self.model_path = Path(model_path)

        self.best_validation_loss = float("inf")
        self.best_epoch = 0

        self.train_history: list[float] = []
        self.validation_history: list[float] = []

    def train_epoch(
        self,
        train_loader
    ) -> float:
        """Train the model for one epoch."""

        self.model.train()

        total_loss = 0.0
        total_samples = 0

        for features, targets in train_loader:
            predictions = self.model(features)

            loss = self.loss_function.calculate(
                predictions,
                targets
            )

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            batch_size = features.size(0)

            total_loss += loss.item() * batch_size
            total_samples += batch_size

        return total_loss / total_samples

    def validate(
        self,
        validation_loader
    ) -> float:
        """Evaluate model on the validation dataset."""

        self.model.eval()

        total_loss = 0.0
        total_samples = 0

        with torch.no_grad():
            for features, targets in validation_loader:
                predictions = self.model(features)

                loss = self.loss_function.calculate(
                    predictions,
                    targets
                )

                batch_size = features.size(0)

                total_loss += loss.item() * batch_size
                total_samples += batch_size

        return total_loss / total_samples

    def calculate_metrics(
        self,
        data_loader
    ) -> tuple[float, float, float]:
        """
        Calculate MSE, MAE and RMSE on a dataset.
        """

        self.model.eval()

        squared_error = 0.0
        absolute_error = 0.0
        total_samples = 0

        with torch.no_grad():
            for features, targets in data_loader:
                predictions = self.model(features)

                errors = predictions - targets

                squared_error += torch.sum(
                    errors ** 2
                ).item()

                absolute_error += torch.sum(
                    torch.abs(errors)
                ).item()

                total_samples += features.size(0)

        mse = squared_error / total_samples
        mae = absolute_error / total_samples
        rmse = mse ** 0.5

        return mse, mae, rmse

    def save_best_model(self) -> None:
        """Save the model with the best validation loss."""

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        torch.save(
            self.model.state_dict(),
            self.model_path
        )

        print(
            f"Best model saved: "
            f"Validation Loss = {self.best_validation_loss:.4f}"
        )

    def fit(
        self,
        train_loader,
        validation_loader,
        epochs: int = 10
    ) -> None:
        """Train the model for multiple epochs."""

        for epoch in range(1, epochs + 1):
            train_loss = self.train_epoch(
                train_loader
            )

            validation_loss = self.validate(
                validation_loader
            )

            self.train_history.append(
                train_loss
            )

            self.validation_history.append(
                validation_loss
            )

            print(
                f"Epoch {epoch}/{epochs} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Validation Loss: {validation_loss:.4f}"
            )

            if validation_loss < self.best_validation_loss:
                self.best_validation_loss = validation_loss
                self.best_epoch = epoch

                self.save_best_model()

    def test(
        self,
        test_loader
    ) -> float:
        """Evaluate the trained model on the test dataset."""

        return self.validate(test_loader)
