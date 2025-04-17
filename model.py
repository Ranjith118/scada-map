import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib

# Step 1: Preprocess Data
def preprocess_data(file_path):
    # Load the dataset
    data = pd.read_csv(file_path)

    # Encode categorical columns (e.g., IP, MAC addresses, event_type, device names)
    label_encoders = {}
    for column in data.columns:
        if data[column].dtype == 'object':  # Check if the column is non-numeric
            label_enc = LabelEncoder()
            data[column] = label_enc.fit_transform(data[column])
            label_encoders[column] = label_enc

    # Normalize the timestamp column if present
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'])  # Convert to datetime
        data['timestamp'] = data['timestamp'].astype('int64') / 10**9  # Convert to seconds

        scaler = MinMaxScaler()
        data[['timestamp']] = scaler.fit_transform(data[['timestamp']])

    return data

# Step 2: Train the Model
def train_model(processed_data):
    # Remove unnecessary columns like 'message'
    X = processed_data.drop(columns=['message'], errors='ignore')  # Keep only relevant features

    # Split the dataset into training and testing sets
    X_train, X_test = train_test_split(X, test_size=0.3, random_state=42)

    # Train the Isolation Forest model
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_train)

    # Save the trained model to a file for later use
    joblib.dump(model, "anomaly_model.pkl")
    print("Model saved as 'anomaly_model.pkl'")

    # Return the trained model and the test set
    return model, X_test

# Step 3: Evaluate the Model
def evaluate_model(model, X_test):
    # Use the model to predict anomalies in the test set
    predictions = model.predict(X_test)

    # Count anomalies (-1 indicates an anomaly, 1 indicates normal behavior)
    num_anomalies = (predictions == -1).sum()
    print(f"Anomalies detected in the test set: {num_anomalies}")

    return predictions

# Main Function to Train and Save the Model
if __name__ == "__main__":
    # Step 1: Load and preprocess the data
    file_path = "network_logs.csv"  # Path to your dataset
    processed_data = preprocess_data(file_path)

    # Step 2: Train the model
    model, X_test = train_model(processed_data)

    # Step 3: Evaluate the model
    evaluate_model(model, X_test)
