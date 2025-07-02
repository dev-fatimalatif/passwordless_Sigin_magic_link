# passwordless_Sigin_magic_link
Here is a sample `README.md` file for your **Passwordless Sign-Up with AWS Cognito using a Magic Link**, including CDK-based infrastructure, Lambda triggers, and a testing function:

---

```markdown
# 🔐 Passwordless Sign-Up with AWS Cognito (Magic Link)

This project implements a secure **passwordless sign-up and sign-in flow using AWS Cognito** and **magic links**. It uses **AWS CDK (Infrastructure as Code)** to provision the Cognito User Pool and associated Lambda triggers.

---

## 📌 Features

- ✅ **Passwordless authentication** using signed magic links
- 🔁 **Custom Cognito authentication flow** using Lambda triggers:
  - `CreateAuthChallenge`
  - `DefineAuthChallenge`
  - `VerifyAuthChallenge`
  - `PreSignUp`
  - `PostConfirmation`
- 🛠️ **CDK deployment** for Cognito resources and all Lambda triggers
- ✉️ **Magic link email** is sent via **Amazon SES**
- 🧪 Includes a **testing Lambda function** to initiate the magic link flow and verify the challenge

---

## 🚀 Getting Started

### 1. Prerequisites

- Node.js and npm or Python (for CDK)
- AWS CLI configured
- AWS CDK v2 installed (`npm install -g aws-cdk`)
- Verified SES email identity for sending emails

---

### 2. Deploy Infrastructure

```bash
cd cdk
cdk deploy
````

This will provision:

* A Cognito User Pool with custom authentication flow
* User Pool Client
* All necessary Lambda triggers (as specified)

---

### 3. How It Works

1. A user provides their **email address**
2. Cognito triggers the **`CreateAuthChallenge`** Lambda

   * This Lambda generates a signed magic link and emails it to the user via SES
3. The user clicks the link, which contains a **signed token**
4. A frontend (or test function) extracts the token and calls Cognito's **`RespondToAuthChallenge`**
5. Cognito triggers the **`VerifyAuthChallenge`** Lambda to validate the token
6. If valid, Cognito returns **tokens (ID, access, refresh)** for the user

---

### 4. Test the Flow

You can test the complete flow by invoking the test Lambda function with an email:

#### Example Input:

```json
{
  "method": "passwordless",
  "email": "your-email@example.com"
}
```

This will:

* Initiate the `CUSTOM_AUTH` flow
* Log the session and token
* Optionally call `RespondToAuthChallenge` to simulate verification (for test use)

---

## 🧠 Lambda Functions Overview

| Function Name         | Purpose                                       |
| --------------------- | --------------------------------------------- |
| `CreateAuthChallenge` | Generates magic link and emails to user       |
| `DefineAuthChallenge` | Determines if tokens should be issued         |
| `VerifyAuthChallenge` | Verifies token sent back by user              |
| `PreSignUp`           | Optional logic before user is created         |
| `PostConfirmation`    | Optional logic after user is confirmed        |
| `TestMagicLink`       | Programmatically triggers and tests auth flow |

---

## 📧 Email Magic Link Example

```
https://your-cloudfront-domain.com?token=<Base64SignedToken>
```

---

## 🛡️ Security

* Magic tokens are **HMAC signed** using a secret key
* Tokens are **time-limited** (e.g., 15 minutes)
* SES ensures **trusted email delivery**
* AWS Cognito ensures **robust token management**

---

## 🧪 Notes

* Make sure your **SES sender email is verified**
* You can use **CloudFront + S3** or Amplify to host the frontend that captures and verifies the token

---

## 📜 License

MIT License – Use this project freely for learning or in production (at your own risk!)

---

## ✨ Credits

Built with ❤️ using AWS CDK, Cognito, SES, and Python

```
