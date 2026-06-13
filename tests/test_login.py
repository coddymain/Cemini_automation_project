import pytest
from playwright.sync_api import  Page, expect
from core.settings import config
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage



def test_successful_login(page: Page, login_page: LoginPage, inventory_page: InventoryPage):
    login_page.open(config.BASE_URL)
    login_page.login(config.STANDARD_USER, config.VALID_PASSWORD)
    expect(page).to_have_url(f"{config.BASE_URL}inventory.html")
    expect(inventory_page.title).to_have_text("Products")

def test_locked_out_user(page: Page, login_page: LoginPage):
    login_page.open(config.BASE_URL)
    login_page.login(config.LOCKED_OUT_USER, config.VALID_PASSWORD)
    expect(login_page.error_message).to_be_visible()
    expect(login_page.error_message).to_have_text("Epic sadface: Sorry, this user has been locked out.")

def test_invalid_password(page: Page, login_page: LoginPage):
    login_page.open(config.BASE_URL)
    login_page.login(config.STANDARD_USER, "wrong_password_123")
    expect(login_page.error_message).to_be_visible()
    expect(login_page.error_message).to_have_text("Epic sadface: Username and password do not match any user in this service")
                                                  



