# Yang - GenAI Chat UI

<p align="center">
  <img width="200" height="200" alt="YangYang_Full_Merge" src="https://github.com/user-attachments/assets/32c60a01-62f4-4951-aea3-ef9e279d7e28" />
</p>
<h3><p align="center">Yang — A lightweight, extensible GenAI chat UI built for speed, simplicity, and seamless integration.</p></h3>

## Overview

Yang is a modern, feature-rich chat interface for Generative AI applications. Built with Streamlit, it provides a seamless experience for interacting with AI models through AWS Bedrock, with support for agents, tools, knowledge bases, and comprehensive user management.

## Features

- 🤖 **AI Assistant Interface** - Interactive chat interface with support for multiple AI models
- ⭐️ **Agent Management** - Create and manage AI agents with custom configurations
- 🧠 **LLM Integration** - Support for multiple LLM providers (Claude, Llama, GPT-OSS)
- 🛠️ **Tool Management** - Extend functionality with custom tools
- 🏷️ **Tag System** - Organize and categorize content with tags
- 👤 **User Management** - Role-based access control (Administrator, Maintainer, User)
- 🔐 **Authentication** - Secure JWT-based authentication with AWS Secret Manager
- 📊 **Feedback System** - Collect and track user feedback on AI responses
- 🎨 **Modern UI** - Clean, responsive interface built with Streamlit

## Tech Stack

### Frontend
- **Streamlit** - Web application framework
- **Extra Streamlit Components** - Enhanced UI components

### Backend
- **FastAPI** - RESTful API service
- **PyJWT** - JWT token handling
- **Requests** - HTTP client for API communication

### AWS Services
- **AWS Bedrock** - AI model hosting and inference
- **AWS Bedrock Knowledge Bases** - RAG (Retrieval-Augmented Generation) support
- **AWS Bedrock Guardrails** - Content safety and filtering
- **AWS Secrets Manager** - Secure credential storage
- **Boto3** - AWS SDK for Python

## Installation

### Prerequisites

- Python 3.8 or higher
- AWS Account with Bedrock access
- FastAPI backend service (separate repository)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YangYang-Research/yang-genai-chat-ui.git
   cd yang-genai-chat-ui
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate JWT secret key**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Generate API auth key**
   ```bash
   python -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode('utf-8'))"
   ```

6. **Configure AWS credentials**
   
   Ensure your AWS credentials are configured via:
   - AWS CLI: `aws configure`
   - Environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
   - IAM role (if running on EC2)

7. **Create AWS Secret Manager**

   ```bash
   aws secretsmanager create-secret --name yang-genai-chat-secret --secret-string '{"app_jwt_key": "your-generated-jwt-secret-key", "api_auth_key": "your-generated-api-auth-key-name", "db_username": "your-db-username", "db_password": "your-db-password"}' --region us-east-1
   ```

8. **Configure Yang-GenAI-Chat-Service**

   Follow the instructions in the [Yang-GenAI-Chat-Service](https://github.com/YangYang-Research/yang-genai-chat-service) repository to configure the service.

9. **Configure environment variables**
   
  Copy the `.env.example` file to `.env` and configure the environment variables.
  ```bash
  cp .env.example .env
  ```

  Configure the environment variables.
  ```env
  AWS_REGION=us-east-1
  AWS_SECRET_NAME=yang-genai-chat-secret
  API_SERVICE=http://localhost:8000/v1/ # Yang-GenAI-Chat-Service API service URL
  API_AUTH_KEY_NAME=api_auth_key
  APP_JWT_KEY_NAME=app_jwt_key
  
  ... other environment variables ...
  ```

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Login

- Username: administrator
- Password: The password is automatically generated when the first run yang-genai-chat-service. You can find the password in console output or the logs of yang-genai-chat-service.

*Note: Change the password after the first login.*

### User Roles

- **Administrator** - Full access to all features including user and role management
- **Maintainer** - Access to AI features and management tools
- **User** - Access to AI assistant interface only

## Configuration

### Supported Tools

- Arxiv
- DuckDuckGo
- Wikipedia
- Google Search
- Google Scholar
- Google Trends
- OpenWeather
- AskNews
- Reddit
- Searx

### Supported Models

- Claude (Anthropic)
- Llama (Meta)
- GPT-OSS (Open Source GPT)

## Security

- JWT-based authentication with secure token storage
- AWS Secrets Manager integration for sensitive credentials
- Role-based access control (RBAC)
- Password hashing with Argon2
- AWS Bedrock Guardrails for content safety

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
