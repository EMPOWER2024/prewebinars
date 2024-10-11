
# EMPWR24 Datathon - Data Upload Instructions

## Overview
Welcome to the EMPWR24 Datathon! In this guide, you will find instructions for setting up AWS CLI, obtaining temporary credentials, and uploading your data to the EMPWR24 S3 bucket. 

⚠️ **Note**: The credentials provided are valid for only 60 minutes, so make sure to upload your compressed data promptly after setting up your AWS CLI.

## Requirements

Before you begin, ensure the following (actually just google aws cli download and it will take you to their website):

- **AWS CLI**: Installed on your system. If not, you can follow the [AWS CLI installation guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).
- **Curl**: Installed on your system (most Linux distributions should have `curl` pre-installed).

## Setup Instructions

### 1. Check AWS CLI Installation

To verify if AWS CLI is installed on your system, run the following command in your terminal:

```bash
aws --version
```

If AWS CLI is not installed, follow the instructions in the [AWS CLI installation guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

### 2. Check if Curl is Installed

Verify if `curl` is installed by running:

```bash
curl --version
```

If it's not installed, install it using your system's package manager. For Ubuntu, you can use:

```bash
sudo apt-get install curl
```

### 3. Obtain Temporary AWS Credentials

To obtain temporary credentials, run the following command in your terminal:

```bash
curl -X POST "https://don3jm22tg.execute-api.us-west-2.amazonaws.com/auth" -H "Content-Type: application/json" -d '{"username": "xxx", "password": "xxxx"}'
```

This will return a **JSON response** containing your credentials in the terminal, which looks like this:

```json
{
  "_metadata": {},
  "data": {
    "bucket": "empower-datathon-prod-empowerdata-bcucxkzr",
    "credentials": {
      "accessKeyId": "<access_key_id>",
      "expires": "2024-10-07T12:41:00.000Z",
      "secretAccessKey": "<secret_access_key>",
      "sessionToken": "<session_token>"
    }
  }
}
```

> **Note**: These credentials expire in **15 minutes**, so make sure to proceed promptly.

### 4. Configure AWS CLI with Temporary Credentials

After receiving the credentials, configure your AWS CLI by running the following commands:

```bash
aws configure set aws_access_key_id <access_key_id>
aws configure set aws_secret_access_key <secret_access_key>
aws configure set aws_session_token <session_token>
```

Replace `<access_key_id>`, `<secret_access_key>`, and `<session_token>` with the respective values from the JSON response.

### 5. Upload Your Data to S3

Once AWS CLI is configured, upload your compressed data to the S3 bucket using the following command:

```bash
aws s3 cp <local_file_path> s3://empower-datathon-prod-empowerdata-bcucxkzr/<destination_path>
```

- Replace `<local_file_path>` with the path to your local file (e.g., `/path/to/data.zip`).
- Replace `<destination_path>` with the desired path inside the S3 bucket (e.g., `uploads/data.zip`).

### Example

```bash
aws s3 cp /Users/yourname/Documents/data.zip s3://empower-datathon-prod-empowerdata-bcucxkzr/uploads/data.zip
```

## Troubleshooting

If you encounter any issues while uploading the data, make sure:

- You have copied and set the correct credentials.
- You upload within the 15-minute validity period of the credentials.
- Your AWS CLI is properly configured.

For more help, consult the [AWS CLI documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

## License

This repository and the instructions provided here are licensed under the [MIT License](./LICENSE).
