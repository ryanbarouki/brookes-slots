from bs4 import BeautifulSoup
from twill import browser
from twill.commands import fv as fill_value
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    LOGIN_URL = "https://brookessport.leisurecloud.net/Book/mrmLogin.aspx"
    BOOKING_URL = "https://brookessport.leisurecloud.net/Book/mrmselectActivityGroup.aspx"
    USER = os.getenv("BROOKES-USERNAME")
    PASSWORD = os.getenv("BROOKES-PASSWORD")
    # login
    browser.go(LOGIN_URL)
    fill_value("1", "ctl00$MainContent$InputLogin", USER)
    fill_value("1", "ctl00$MainContent$InputPassword", PASSWORD)
    browser.submit()

    # essentially click "Make a Booking"
    browser.go(BOOKING_URL)
    # click "Headington Climb"
    fill_value("1", "ctl00$MainContent$activityGroupsGrid$ctrl1$lnkListCommand", "")
    browser.submit()

    soup = BeautifulSoup(browser.html, "html.parser")
    print([tag["id"] for tag in soup.find_all("input", value=lambda x: x and x.startswith("Thurs"))])

    # print(page.text)