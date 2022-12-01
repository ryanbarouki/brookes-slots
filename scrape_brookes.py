from bs4 import BeautifulSoup
from twill import browser
from twill.commands import fv as fill_value
from datetime import datetime


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
            dates = self.get_dates(day)
            for i in range(len(dates)):
                button_id = f"ctl00_MainContent_ClassStatus_ctrl{i}_btnAvaliable"
                availability = self.get_availability(button_id)
                slot = {"id": id, "button_id": button_id, "date": dates[i], "status": availability}
                slots.append(slot)
            # go back
            browser.back() 
            # browser.go(BrookesScraper.BOOKING_URL)
            # click("1", "ctl00$MainContent$activityGroupsGrid$ctrl1$lnkListCommand")

        return sorted(slots, key=lambda x: x['date'])

    def get_dates(self, day):
        soup = BeautifulSoup(browser.html, "html.parser")
        h4 = soup.find_all('h4', recursive=True)
        tidy_h4_text = [h.get_text().strip() for h in h4]
        # add year to string
        dates = list(filter(lambda a: a and a.lower().startswith(day.lower()), tidy_h4_text))
        return [self.add_year(date) for date in dates]
    
    def add_year(self, date_str):
        slot_date = datetime.strptime(date_str, f"%a %d %b, %H:%M")
        if slot_date.month < datetime.now().month:
            year = datetime.now().year + 1
        else:
            year = datetime.now().year
        slot_date = slot_date.replace(year=year)
        return datetime.strftime(slot_date, f"%a %d %b %Y, %H:%M")

    def get_availability(self, button_id):
        soup = BeautifulSoup(browser.html, "html.parser")
        status = soup.find('input', id=button_id)['value'].split(" ")
        if len(status) < 3:
            raise Exception("Could not find text in button")
        return int(status[0]) if status[0].lower() != "class" else 0

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
        day = slot['date'].split(" ")[0]
        dates = self.get_dates(day)
        if slot['date'] not in dates:
            return 0
        spaces_remaining = self.get_availability(slot['button_id'])
        return spaces_remaining