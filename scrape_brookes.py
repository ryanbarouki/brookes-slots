from bs4 import BeautifulSoup
from twill import browser
from twill.commands import fv as fill_value
from dotenv import load_dotenv
import os

class BrookesScraper:
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

    def get_slots_for_day(self, day):
        LOGIN_URL = "https://brookessport.leisurecloud.net/Book/mrmLogin.aspx"
        BOOKING_URL = "https://brookessport.leisurecloud.net/Book/mrmselectActivityGroup.aspx"

        # login
        browser.go(LOGIN_URL)
        fill_value("1", "ctl00$MainContent$InputLogin", self.username)
        fill_value("1", "ctl00$MainContent$InputPassword", self.password)
        browser.submit()

        # essentially click "Make a Booking"
        browser.go(BOOKING_URL)

        # click "Headington Climb"
        fill_value("1", "ctl00$MainContent$activityGroupsGrid$ctrl1$lnkListCommand", "")
        browser.submit()

        soup = BeautifulSoup(browser.html, "html.parser")
        return [tag["value"] for tag in soup.find_all("input", value=lambda x: x and x.startswith(day))]





if __name__ == "__main__":
    load_dotenv()
    # load environment variables from .env file
    USER = os.getenv("BROOKES-USERNAME")
    PASSWORD = os.getenv("BROOKES-PASSWORD")

    LOGIN_URL = "https://brookessport.leisurecloud.net/Book/mrmLogin.aspx"
    BOOKING_URL = "https://brookessport.leisurecloud.net/Book/mrmselectActivityGroup.aspx"

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
    print([tag["value"] for tag in soup.find_all("input", value=lambda x: x and x.startswith("Thurs"))])

    # print(page.text)