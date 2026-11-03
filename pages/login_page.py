from playwright.sync_api import Page

from config.config import UI_BASE


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.locator("#userEmail")
        self.password_input = page.locator("#userPassword")
        self.login_button = page.get_by_role("button", name="login")

    def load(self):
        self.page.goto(UI_BASE)

    def login(self, email, password):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()
