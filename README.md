# Kodu-Optim

Kodu-Optim is a distributed system designed to leverage [Optuna](https://optuna.org/) for hyperparameter optimization across multiple compute nodes. It enables efficient and scalable optimization for machine learning models and other computational tasks.

## Features

- Distributed hyperparameter optimization using Optuna.
- Scalable architecture for large-scale experiments.
- Easy integration with existing machine learning workflows.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kodu-optim.git
   cd kodu-optim
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the distributed system:
   ```bash
   python start_distributed.py
   ```

2. Define your Optuna study and objective function in your script:
   ```python
   import optuna

   def objective(trial):
       x = trial.suggest_float("x", -10, 10)
       return x ** 2

   study = optuna.create_study(direction="minimize")
   study.optimize(objective, n_trials=100)
   ```

3. Run your optimization script across the distributed nodes.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
