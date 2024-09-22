# setting up the dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import socket
import pickle

# Function to check internet connectivity
def check_internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (Google's DNS)
    Port: 53/tcp
    Returns: True if internet is connected, False otherwise
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print("No internet connection.")
        return False

# Wait until the internet connection is back
def wait_for_internet():
    print("Checking internet connection...")
    while not check_internet():
        print("Waiting for internet connection...")
        time.sleep(5)
    print("Internet connected!")


# Read the poll data from the polls.txt file
with open('polls.txt', 'r') as file:
    polls = [line.strip() for line in file.readlines() if line.strip()]

#setting up the chrome driver path
service = Service(ChromeDriverManager().install())
options = Options()
options.headless = False  # Set to True if you want to run headless
driver = webdriver.Chrome(service=service, options=options)
# Ensure we have internet before proceeding
wait_for_internet()

# Load cookies if they exist
cookies_file = "linkedin_cookies.pkl"
if os.path.exists(cookies_file):
    driver.get("https://www.linkedin.com")
    with open(cookies_file, "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()
else:
    # No cookies found, prompt for username and password
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.linkedin.com/login")

    # input("Press Enter to close the browser and end the script...")

    driver.find_element(By.ID, "username").send_keys("")
    driver.find_element(By.ID, "password").send_keys("")

    # Click the login button
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Handle 2FA if prompted
    try:
        two_fa_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "input__phone_verification_pin"))
        )
        # Prompt the user to input the 2FA code in the terminal
        two_fa_code = input("Enter the 2FA code: ")

        # Enter the 2FA code into the input field
        two_fa_input.send_keys(two_fa_code)

        driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]").click()
        print("2FA code entered successfully!")
    except Exception as e:
        print("No 2FA required or could not locate 2FA input field.")   
    
    # Save cookies after successful login
    cookies = driver.get_cookies()
    with open(cookies_file, "wb") as file:
        pickle.dump(cookies, file)
    print("Cookies saved!")

try:
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'share-box-feed-entry')]"))
    )
    print("Successfully logged in!")
except Exception as e:
    print(f"Failed to log in. Exiting. {e}")
    driver.quit()
    exit()

# Load or create the Excel file for tracking polls
excel_file = 'poll_tracking.xlsx'
if os.path.exists(excel_file):
    tracking_df = pd.read_excel(excel_file)
else:
    tracking_df = pd.DataFrame(columns=['Poll', 'Status'])


try:
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))
    )
    close_button.click()
except:
    print("No pop-up to dismiss")


for poll_data in polls:
    if poll_data.strip() == "":
        continue

    # splitting the polls data by commas
    poll_parts = poll_data.split(',')
    question = poll_parts[0].strip()
    answers = [answer.strip() for answer in poll_parts[1:]]
    print(f"reading poll:  '{question}'  with answer: {answers}")

    if question in tracking_df['Poll'].values:
        continue  # Skip already posted polls

    print(f"Poll '{question}' with answers: {answers}")

    try:
        # Step 1:
        print("waiting for start a post button...")
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'artdeco-button') and contains(@class, 'share-box-feed-entry__trigger')]"))
        ).click()
        print("Clicked on 'Start a post' button successfully!")

        # Step 2: Click "For More" button
        print("Waiting for 'For More' button...")

        # Using WebDriverWait to locate the button with aria-label "More"
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='More' and contains(@class, 'share-promoted-detour-button')]"))
        ).click()
        print("Clicked on 'For More' button successfully!")


        # Step 3: Click "Create a poll" button
        print("Waiting for 'Create a poll' button...")

        # Using WebDriverWait to locate the button with aria-label "Create a poll"
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Create a poll' and contains(@class, 'share-promoted-detour-button')]"))
        ).click()

        print("Clicked on 'Create a poll' button successfully!")

        # Step 4: Fill in the poll data
        print("Waiting for the question input field...")

        # Locate the textarea input for the poll question
        question_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//textarea[contains(@class, 'polls-detour__question-field')]"))
        )

        # Clear the input field and enter the question
        question_input.clear()  # Clear the field first (if necessary)
        question_input.send_keys(question)
        print("Question written successfully")
        time.sleep(5)

        # Using a generalized XPath to find all input fields for poll answers
        answer_fields = driver.find_elements(By.XPATH, "//input[contains(@class, 'polls-detour__form-fields') and contains(@class, 'artdeco-text-input--input')]")

        # Debug: Print the number of input fields found
        print(f"Number of answer fields found: {len(answer_fields)}")

        
        # Fill in the poll answers
        for i in range(2):
            if i < len(answer_fields):
                answer_fields[i].send_keys(answers[i])
            else:
                print(f"Not enough input fields for all answers. Needed {len(answers)}, found {len(answer_fields)}.")

        # Now click "Add option" to add the third field and fill the third answer
        add_option_button = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div/form/div[4]/button/span")
        add_option_button.click()
        time.sleep(1)  # Short delay to ensure the option is added

        # Find the newly added field and fill in the third answer
        answer_fields = driver.find_elements(By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div/form/div[position()>1]/div[2]/div/input")
        answer_fields[2].send_keys(answers[2])

        # Click "Add option" again to add the fourth field and fill the fourth answer
        add_option_button.click()
        time.sleep(1)  # Short delay to ensure the option is added

        # Find the newly added field and fill in the fourth answer
        answer_fields = driver.find_elements(By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div/form/div[position()>1]/div[2]/div/input")
        answer_fields[3].send_keys(answers[3])

        # Step 5: Set poll duration to 2 weeks
        print("setting poll duration of 2 weeks")
        duration_dropdown = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div/form/select")
        duration_dropdown.click()
        time.sleep(1)
        duration_dropdown.find_element(By.XPATH, "//option[contains(text(), '2 weeks')]").click()
    
        print("duration set for the poll")

        # Step 6: Click Done and Post
        time.sleep(1)
        print("clicking the done button")

        done_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div/div/div/button[2]/span"))
        )
        done_button.click()
        print("Done button clicked")

        time.sleep(2)   

        post_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'artdeco-button--primary') and .//span[text()='Post']]"))
        )
        post_button.click()
        print("Post button clicked, poll posted successfully!")

        # Track the posted poll
        # Add the new row to the DataFrame using pd.concat
        new_row = pd.DataFrame({"Poll": [question], "Status": ["Posted"]})
        tracking_df = pd.concat([tracking_df, new_row], ignore_index=True)

        # Save the updated DataFrame to Excel
        tracking_df.to_excel(excel_file, index=False)

        print(f"Poll '{question}' posted successfully!")
        time.sleep(20)
    except Exception as e:
            print(f"An error occurred: {str(e)}")
            driver.quit()
            exit()