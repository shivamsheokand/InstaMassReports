import contextlib
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import pickle
from pathlib import Path
from files.helper import illegal, scam, pretend_me, pretend_someone

# Types of reports and choosing one
reports = {"illegal": illegal, "scam": scam, "pretend_me": pretend_me, "pretend_someone": pretend_someone}
report_username = input("Enter a report username: ")
for x in reports:
    print(x)
report_type = input("Enter one of the report types: ").lower().strip()
report_function = reports.get(report_type)

# Function to automate the report
def run(playwright: Playwright, session) -> None:
    # Making fake user_agent and launching context
    iphone_12 = playwright.devices['iPhone 12']
    browser = playwright.chromium.launch(headless=False, slow_mo=2000)
    context = browser.new_context(**iphone_12)
    # Make new page and load session
    page = context.new_page()

    page.goto("https://www.instagram.com/")
    context.add_cookies(cookies=session)
    time.sleep(2)
    page.goto("https://www.instagram.com/")
    # Just for safety
    with contextlib.suppress(Exception):
        page.get_by_role("button", name="Turn On").click()
    page.goto(f"https://www.instagram.com/{report_username}/")
    page.wait_for_url(f"https://www.instagram.com/{report_username}/")

    page.get_by_role("button", name="Options").click()

    page.get_by_role("button", name="Report").click()

    page.locator("button").filter(has_text="Report accountchevron").click()

    # Select report type and submit report
    if report_type not in ["illegal", "scam"]:
        page.locator("button").filter(has_text="It's pretending to be someone elsechevron").click()
        # Fill out report form
        if report_function:
            report_function(page)
        # Submit report
        page.click("text=Submit Report")
    else:
        page.locator("button").filter(has_text="It's posting content that shouldn't be on Instagramchevron").click()
        # Fill out report form
        if report_function:
            report_function(page)
        # Submit report
        page.click("text=Submit Report")

    # Close and exit the browser
    context.close()
    browser.close()

# Function to schedule reports at specified times
def schedule_reports(playwright: Playwright, session, report_times: list):
    for minute in report_times:
        current_time = time.localtime()
        target_time = time.struct_time((current_time.tm_year, current_time.tm_mon, current_time.tm_mday, current_time.tm_hour, minute, 0, current_time.tm_wday, current_time.tm_yday, current_time.tm_isdst))
        while time.mktime(current_time) < time.mktime(target_time):
            time.sleep(60)
            current_time = time.localtime()
        try:
            run(playwright, session)
        except Exception as e:
            print(f"An error occurred: {e}")

# Start the script
def start_script(playwright: Playwright):
    file_path = Path().cwd() / 'files' / "accounts"
    all_sessions = [x.name for x in file_path.iterdir()]

    for session_ in all_sessions:
        session_ = str(Path().cwd() / "files" / "accounts" / session_)
        if 'init' in session_:
            continue
        session = pickle.load(open(session_, "rb"))
        report_times = []
        while True:
            try:
                num_reports = int(input("Enter the number of reports to schedule: "))
                if num_reports <= 0:
                    print("Invalid input. Please enter a positive integer.")
                    continue
                minute = int(input("Enter the minute (0-59) to schedule the report: "))
                if not 0 <= minute <= 59:
                    print("Invalid input. Please enter a minute between 0 and 59.")
                    continue
                report_times.extend([minute] * num_reports)
                break
            except ValueError:
                print("Invalid input. Please enter valid integers.")

        schedule_reports(playwright, session, report_times)

with sync_playwright() as playwright:
    start_script(playwright)
