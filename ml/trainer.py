import torch

from ml.loss import GainLoss
from ml.model import GainPredictor
from ml.optimizer import GainOptimizer


class Trainer:
    """Trains the gain prediction model."""

    def __init__(
        self,
        model: GainPredictor,
        optimizer: GainOptimizer,
        loss_function: GainLoss
    ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.loss_function = loss_function

    def train_epoch(
        self,
        train_loader
    ) -> float:
        """Train the model for one epoch."""

        self.model.train()

        total_loss = 0.0

        for features, targets in train_loader:
            predictions = self.model(features)

            loss = self.loss_function.calculate(
                predictions,
                targets
            )

            self.optimizer.zero_grad()

            loss.backward()

            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(train_loader)

    def validate(
        self,
        validation_loader
    ) -> float:
        """Calculate validation loss."""

        self.model.eval()

        total_loss = 0.0

        with torch.no_grad():
            for features, targets in validation_loader:
                predictions = self.model(features)

                loss = self.loss_function.calculate(
                    predictions,
                    targets
                )

                total_loss += loss.item()

        return total_loss / len(validation_loader)

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

            print(
                f"Epoch {epoch}/{epochs} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Validation Loss: {validation_loss:.4f}"
            )

    def validate(self, validation_loader) -> float:
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

    def test(self, test_loader) -> float:
        """Evaluate the trained model on the test dataset."""

        self.model.eval()

        total_loss = 0.0
        total_samples = 0

        with torch.no_grad():
            for features, targets in test_loader:
                predictions = self.model(features)

                loss = self.loss_function.calculate(
                    predictions,
                    targets
                )

                batch_size = features.size(0)

                total_loss += loss.item() * batch_size
                total_samples += batch_size

        return total_loss / total_samples