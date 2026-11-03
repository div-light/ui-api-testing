import re

from playwright.sync_api import Page, expect

from config.config import UI_BASE


def test_authenticated_user(authenticated_page: Page):
    authenticated_page.goto(f"{UI_BASE}/dashboard/dash")
    expect(authenticated_page).to_have_url(re.compile(r".*/dashboard/.*"))
