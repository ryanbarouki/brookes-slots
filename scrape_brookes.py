from bs4 import BeautifulSoup
from twill import browser
from twill.commands import fv as fill_value
from dotenv import load_dotenv
import os


def click(form_id, button_id):
    fill_value(form_id, button_id, "")
    browser.submit()
class BrookesScraper:
    LOGIN_URL = "https://brookessport.leisurecloud.net/Book/mrmLogin.aspx"
    BOOKING_URL = "https://brookessport.leisurecloud.net/Book/mrmselectActivityGroup.aspx"

    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

    def get_slots_for_day(self, day):
        self.login()

        # essentially click "Make a Booking"
        browser.go(BrookesScraper.BOOKING_URL)
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

            for i in range(len(dates)):
                button_id = f"ctl00_MainContent_ClassStatus_ctrl{i}_btnAvaliable"
                status = soup.find('input', id=button_id)['value'].split(" ")
                if len(status) < 3:
                    raise Exception("Could not find text in button")
                if status[0].lower() == "class":
                    availability = status[2]
                else:
                    availability = status[0]
                
                slot = {"id": id, "button_id": button_id, "date": dates[i], "status": availability}
                slots.append(slot)
            # go back
            browser.go(BrookesScraper.BOOKING_URL)
            click("1", "ctl00$MainContent$activityGroupsGrid$ctrl1$lnkListCommand")

        return sorted(slots, key=lambda x: x['date'])

    def login(self):
        browser.go(BrookesScraper.LOGIN_URL)
        fill_value("1", "ctl00$MainContent$InputLogin", self.username)
        fill_value("1", "ctl00$MainContent$InputPassword", self.password)
        browser.submit()

    def get_space_count_for_slot(self, slot):
        self.login()

        # essentially click "Make a Booking"
        browser.go(BrookesScraper.BOOKING_URL)
        # click "Headington Climb"
        click("1", "ctl00$MainContent$activityGroupsGrid$ctrl1$lnkListCommand")
        click("1", slot['id'])
        soup = BeautifulSoup(browser.html, "html.parser")
        spaces_remaining = soup.find('input', id=slot['button_id'])['value']
        return spaces_remaining