import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

def preprocess_data(file_path):
    # Load dataset
    data = pd.read_csv(file_path)

    # Convert timestamps to numerical values
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['timestamp'] = data['timestamp'].astype('int64') / 10**9  # Convert to seconds

    # Encode categorical features (event_type, device_name)
    label_enc = LabelEncoder()
    data['event_type'] = label_enc.fit_transform(data['event_type'])
    data['device_name'] = label_enc.fit_transform(data['device_name'])

    # Scale numerical features (e.g., timestamp)
    scaler = MinMaxScaler()
    data[['timestamp']] = scaler.fit_transform(data[['timestamp']])

    # Drop unnecessary columns
    X = data.drop(columns=['message', 'ip_address', 'mac_address'], errors='ignore')

    return X

# Example usage
file_path = "network_logs.csv"  # Replace with your dataset path
processed_data = preprocess_data(file_path)
print(processed_data.head())
