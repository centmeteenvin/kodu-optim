import optuna

optuna.create_study(
    study_name="test",
    direction="minimize",
    storage="postgresql://admin:admin@localhost:10000/optuna",
)
