import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
import json
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

EVAL_THRESHOLD = 0.70


def train(
    params: dict,
    data_path: str = "data/train_phase1.csv",
    eval_path: str = "data/eval.csv",
) -> float:
    """
    Huan luyen mo hinh va ghi nhan ket qua vao MLflow.

    Tham so:
        params     : dict chua cac sieu tham so cho RandomForestClassifier.
        data_path  : duong dan den file du lieu huan luyen.
        eval_path  : duong dan den file du lieu danh gia.

    Tra ve:
        accuracy (float): do chinh xac tren tap danh gia.
    """

    # TODO 1: Doc du lieu huan luyen va danh gia
    df_train = pd.read_csv(data_path)
    df_eval = pd.read_csv(eval_path)

    # TODO 2: Tach dac trung (X) va nhan (y)
    X_train = df_train.drop(columns=["target"])
    y_train = df_train["target"]
    X_eval = df_eval.drop(columns=["target"])
    y_eval = df_eval["target"]

    # Bonus 5: Check Label Distribution
    dist = y_train.value_counts(normalize=True)
    print("\n[Bonus 5] Label Distribution:")
    for label, ratio in dist.items():
        print(f"  Class {label}: {ratio:.2%}")
        if ratio < 0.10:
            print(f"  WARNING: Class {label} is below 10% (Data Drift/Imbalance)!")

    with mlflow.start_run():
        # Bonus 2: Model Selection
        model_type = params.get("model_type", "random_forest")
        mlflow.log_param("model_type", model_type)
        mlflow.log_params(params)

        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=params.get("n_estimators", 100),
                max_depth=params.get("max_depth"),
                min_samples_split=params.get("min_samples_split", 2),
                random_state=42
            )
        elif model_type == "gradient_boosting":
            from sklearn.ensemble import GradientBoostingClassifier
            model = GradientBoostingClassifier(
                n_estimators=params.get("n_estimators", 100),
                learning_rate=params.get("learning_rate", 0.1),
                max_depth=params.get("max_depth", 3),
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        model.fit(X_train, y_train)

        # TODO 5: Du doan tren tap danh gia va tinh chi so
        preds = model.predict(X_eval)
        acc = accuracy_score(y_eval, preds)
        f1 = f1_score(y_eval, preds, average="weighted")

        # TODO 6: Ghi nhan chi so vao MLflow
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(model, "model")

        # TODO 7: In ket qua ra man hinh
        print(f"Accuracy: {acc:.4f} | F1: {f1:.4f}")

        # Bonus 3: Detailed Report
        from sklearn.metrics import classification_report, confusion_matrix
        report_text = classification_report(y_eval, preds)
        matrix = confusion_matrix(y_eval, preds)
        
        with open("outputs/report.txt", "w") as f:
            f.write("=== MLOPS PERFORMANCE REPORT ===\n")
            f.write(f"Model Type: {model_type}\n")
            f.write(f"Accuracy: {acc:.4f}\n")
            f.write(f"F1 Score: {f1:.4f}\n\n")
            f.write("Classification Report:\n")
            f.write(report_text)
            f.write("\nConfusion Matrix:\n")
            f.write(str(matrix))

        # TODO 8: Luu metrics ra file outputs/metrics.json
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/metrics.json", "w") as f:
            json.dump({"accuracy": acc, "f1_score": f1}, f)

        # TODO 9: Luu mo hinh ra file models/model.pkl
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")

    # TODO 10: Tra ve acc
    return acc


if __name__ == "__main__":
    with open("params.yaml") as f:
        params = yaml.safe_load(f)
    train(params)
