# setting up the dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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


# Define batch size and calculate the number of batches
batch_size = 3
# schedule_date = datetime.now() + timedelta(days=1)  # Start scheduling from tomorrow
num_batches = (len(polls) + batch_size - 1) // batch_size  # Ceiling division


# Added print for total number of batches for debugging
print(f"Total Batches: {num_batches}")

for batch_index in range(num_batches):
    start_index = batch_index * batch_size
    end_index = min(start_index + batch_size, len(polls))
    batch_polls = polls[start_index:end_index]

    # Calculate the scheduling date for the batch
    schedule_date = datetime.now() + timedelta(days=batch_index + 1)
    date_str = schedule_date.strftime("%m/%d/%Y")
    print(f"Scheduling batch {batch_index + 1} on date {date_str}")

    for poll_index, poll_data in enumerate(batch_polls):
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
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'artdeco-button') and contains(@class, 'share-box-feed-entry__trigger')]"))
            ).click()
            print("Clicked on 'Start a post' button successfully!")
            
            # Step 2: Click "For More" button (assuming this step is needed)
            print("Waiting for 'For More' button...")
            # Using WebDriverWait to locate the button with aria-label "More"
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='More' and contains(@class, 'share-promoted-detour-button')]"))
            ).click()
            print("Clicked on 'For More' button successfully!")



            # Step 3: Click "Create a poll" button
            print("waiting for create a poll button..")
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Create a poll' and contains(@class, 'share-promoted-detour-button')]"))
            ).click()

            print("Clicked on 'Create a poll' button successfully!")

            # Step 4: Fill in the poll data
            # Locate the question input field using a dynamic XPath
            question_input = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div/form/div[1]/div/div/textarea")
            question_input.clear()  # Clear the field first (if necessary)
            question_input.send_keys(question)
            print("Question written successfully")
            time.sleep(2)

            # Generalized XPath to match both input fields
            answer_fields = driver.find_elements(By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div/form/div[position()>1]/div[2]/div/input")

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
            
            # here is the code to schedult the post
            print("Clicking the 'Schedule Post' button")
            schedule_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Schedule post']"))  # Update this XPath if necessary
            )
            schedule_button.click()
            time.sleep(1)

            print("Clicked the 'Schedule Post' button successfully!")

            # Step 1: Set the date for tomorrow or day after tomorrow
            print("Setting the scheduled date")
            date_picker = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Date']"))  # Locate the date picker input field
            )
            date_picker.click()
            time.sleep(2)
            # Calculate tomorrow's or day after tomorrow's date
            schedule_date = datetime.now() + timedelta(days=1)  # Change days=2 for day after tomorrow
            date_str = schedule_date.strftime("%m/%d/%Y")  # Format as needed

            # Enter the date in the date picker input
            date_picker.clear()
            date_picker.send_keys(date_str)
            print(f"Scheduled date set to {date_str}")

            # Step 2: Click the 'Cancel' button using the provided XPath
            cancel_button_xpath = "/html/body/div[3]/div/div/div/div[2]/div[1]/form/div[1]/div[2]/section/div/footer/button[2]"

            # Wait until the cancel button is visible and clickable
            cancel_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, cancel_button_xpath))
            )
            # Click the cancel button
            cancel_button.click()
            print("Cancel button clicked to close the date picker dialog box")
            print("Date picker fully closed")
            date_picker.send_keys(Keys.TAB)
            time.sleep(2)

            # Step 2: Set the time to 10:00 AM
            print("Setting the scheduled time to 10:00 AM")
            time_picker = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div[1]/form/div[2]/div/div[1]/div/input"))
            )
            # Use JavaScript to set the time value directly
            time_script = """arguments[0].value = '10:00 AM';"""
            driver.execute_script(time_script, time_picker)
        
            print("Scheduled time set to 10:00 AM using JavaScript")
            time_picker.click()
            time.sleep(2)

            # Enter the time as 10:00 AM (adjust format if needed)
            time_picker.clear()
            time_picker.send_keys("10:00 AM")
            print("Scheduled time set to 10:00 AM")
            time.sleep(2)
            # time_picker.send_keys(Keys.TAB)
            sched_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div/div/div[1]/div/h2"))  # Adjust XPath if needed
            )
            sched_button.click()

            # Wait a moment before proceeding
            time.sleep(3)
            
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div[2]/div/button[2]/span"))  # Adjust XPath if needed
            )
            next_button.click()
            print("Next button clicked")

            time.sleep(2)  
            
            # Wait for scheduling to complete

            # Wait for the "Schedule" button to be clickable
            schedule_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div/div/div[2]/div/div/div[2]/div[4]/div/div[2]/button/span"))  # Adjust XPath if needed
            )
            schedule_button.click()
            print("Schedule button clicked")

            time.sleep(3)  # Wait for scheduling to complete


            # Track the posted poll
            # Add the new row to the DataFrame using pd.concat
            new_row = pd.DataFrame({"Poll": [question], "Status": ["Scheduled"]})
            tracking_df = pd.concat([tracking_df, new_row], ignore_index=True)



            # Save the updated DataFrame to Excel
            tracking_df.to_excel(excel_file, index=False)

            # print(f"Poll '{question}' posted successfully!")
            time.sleep(3)
        except Exception as e:
                print(f"An error occurred: {str(e)}")
                driver.quit()
                exit()
        # After processing each batch of 3 polls, increment the schedule date for the next batch
        schedule_date += timedelta(days=1)

