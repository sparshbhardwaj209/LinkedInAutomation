# LinkedIn Poll Automation Script

This Python script automates the process of creating and posting polls on LinkedIn using Selenium WebDriver. It handles everything from logging in, creating polls with multiple choice answers, setting poll durations, and tracking posted polls in an Excel file.

## Features

- **Automated Poll Creation**: Automatically creates and posts polls on LinkedIn.
- **2FA Login Support**: Handles LinkedIn Two-Factor Authentication (2FA).
- **Poll Tracking**: Keeps track of posted polls and saves the status in an Excel file.
- **Set Poll Duration**: Automatically sets the poll duration to 2 weeks.

## Requirements

- Python 3.7+
- Google Chrome browser
- ChromeDriver (automatically managed by `webdriver-manager`)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sparshbhardwaj209/linkedin-poll-automation.git

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Create Poll Data File**: Create a file named `polls.txt` in the root directory of your project. This file should contain your poll questions and answers in the following format:

   ```text
   Which front-end framework do you prefer?,React,Angular,Vue.js,Svelte
   What is your favorite back-end framework?,Node.js,Django,Flask,Spring Boot

2. **Run the Script**:
    ```bash
    python automation.py
    ```
    The script will:
    - Open LinkedIn and log in.
    - Pause for you to enter your 2FA code (if needed).
    - Create and post each poll from the `polls` list.
    - Track posted polls in an Excel file called `poll_tracking.xlsx`.

## 2FA (Two-Factor Authentication)
If your LinkedIn account uses 2FA, the script will pause and prompt you to enter the authentication code manually. Once you've entered the code, the script will continue logging in and posting the polls.

## Example
If you want to post two polls:

1. **Poll 1**: "Which front-end framework do you prefer?"
   - Options: React, Angular, Vue.js, Svelte
2. **Poll 2**: "What is your favorite back-end framework?"
   - Options: Node.js, Django, Flask, Spring Boot

Update the `polls` list in `polls.txt`:

```python
    "Which front-end framework do you prefer?,React,Angular,Vue.js,Svelte",
    "What is your favorite back-end framework?,Node.js,Django,Flask,Spring Boot"
