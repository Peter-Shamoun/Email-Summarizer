# Email Summarizer

A web application that summarizes your Gmail inbox from the last 24 hours using AI. The application uses React for the frontend, Flask for the backend, and integrates with Gmail API and OpenAI's GPT-4 for email summarization.

## Features

- Gmail integration with OAuth2 authentication
- Summarizes last 24 hours of primary inbox emails
- AI-powered summarization using GPT-4
- Clean, modern UI with responsive design
- Markdown rendering for summary output

## Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- Gmail Account
- OpenAI API Key
- Google Cloud Project with Gmail API enabled

## Setup

### Backend Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```  
2. Run app:
   ```bash
   python app.py
   ```  

### Frontend Setup

run `npm install` to install dependencies and `npm start` to run the frontend.

## Usage

1. Run the backend server.
2. Run the frontend server.
3. Authorize the application to access your Gmail account. Through clicking the "Get Email Summary" button. This will redirect you to a Google login page. After authorization, you have to refresh the page to continue.
4. View your summarized emails by clicking the "Get Email Summary" button.
