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
        click("1", "ctl00$MainContent$activityGroupsGrid$ctrl1$lnkListCommand")

        soup = BeautifulSoup(browser.html, "html.parser")
        slots = []
        for tag in soup.find_all("input", value=lambda x: x and x.lower().startswith(day.lower())):
            id = tag["id"]
            click("1", id)
            soup = BeautifulSoup(browser.html, "html.parser")
            h4 = soup.find_all('h4', recursive=True)
            tidy_h4_text = [h.get_text().strip() for h in h4]
            dates = list(filter(lambda a: a and a.lower().startswith(day.lower()), tidy_h4_text))
            slots += dates
            # go back
            browser.go(BOOKING_URL)
            click("1", "ctl00$MainContent$activityGroupsGrid$ctrl1$lnkListCommand")

        return sorted(slots)




def click(form_id, button_id):
    fill_value(form_id, button_id, "")
    browser.submit()

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
    click("1", "ctl00$MainContent$activityGroupsGrid$ctrl1$lnkListCommand")

    soup = BeautifulSoup(browser.html, "html.parser")
    slots = []
    for tag in soup.find_all("input", value=lambda x: x and x.startswith("Thurs")):
        id = tag["id"]
        click("1", id)
        soup = BeautifulSoup(browser.html, "html.parser")
        h4 = soup.find_all('h4', recursive=True)
        tidy_h4_text = [h.get_text().strip() for h in h4]
        dates = list(filter(lambda a: a and a.lower().startswith("thu"), tidy_h4_text))
        slots += dates
        # go back
        browser.go(BOOKING_URL)
        click("1", "ctl00$MainContent$activityGroupsGrid$ctrl1$lnkListCommand")

    print(sorted(slots))

    # print(page.text)