import requests
import base64
import zipfile
import io
import pandas as pd


def prepare_url(base_url, owner_slug, dataset_slug, dataset_version):
    return f"{base_url}/datasets/download/{owner_slug}/{dataset_slug}?datasetVersionNumber={dataset_version}"


def encode_credentials(username, key):
    creds = base64.b64encode(
        bytes(f"{username}:{key}", "ISO-8859-1")).decode("ascii")
    return {
        "Authorization": f"Basic {creds}"
    }


def send_request(url, headers):
    return requests.get(url, headers=headers)


def main():
    # 1: Preparing the URL.
    base_url = "https://www.kaggle.com/api/v1"
    owner_slug = "rohanrao"
    dataset_slug = "formula-1-world-championship-1950-2020"
    dataset_version = "22"

    url = prepare_url(base_url, owner_slug, dataset_slug, dataset_version)

    # 2: Encoding the credentials and preparing the request header.
    username = "charanvengatesh"
    key = "0af2f27b7c80e104843ed766e4606dc4"
    headers = encode_credentials(username, key)

    # 3: Sending a GET request to the URL with the encoded credentials.
    response = send_request(url, headers)

    # 4: Loading the response as a file via io and opening it via zipfile.
    zf = zipfile.ZipFile(io.BytesIO(response.content)) 
    
    # 5: Reading the CSV from the zip file and converting it to a dataframe.
    file_name = "circuits.csv"
    df = pd.read_csv(zf.open(file_name))

    # 6: convert the dataframe to a JSON object.
    json_data = df.to_json(orient="records")

    # 7: write the JSON object to a file called "races.json".
    with open("circuit.json", mode="+w") as f:
        f.write(json_data)

if __name__ == "__main__":
    main()


