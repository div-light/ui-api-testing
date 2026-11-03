import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage


@pytest.mark.parametrize(
    "email, password",
    [
        ("testuserf427036@user.com", ""),
        ("", "Test76@!"),
        ("testuserf427036@user.com", "Test76@!"),
        ("testuseuse@test.com", "Test25@!"),
        ("", ""),
    ],
    ids=[
        "empty password",
        "empty_username",
        "wrong_password",
        "wrong_email",
        "empty_credentials",
    ],
)
def test_negative_cases(page: Page, email, password):
    lp = LoginPage(page)
    lp.load()
    lp.login(email, password)
    expect(page).not_to_have_url("**/dashboard/**")
