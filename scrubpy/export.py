import os

def save_dataset(df, dataset):
    base_name = f"cleaned_{dataset}"
    counter = 1
    file_name = base_name

    while os.path.exists(file_name):
        file_name = f"{base_name.split('.')[0]}_{counter}.csv"
        counter += 1

    df.to_csv(file_name, index=False)
    print(f"✅ Cleaned data saved as {file_name}!")
    return df
