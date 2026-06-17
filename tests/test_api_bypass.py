import pytest
from playwright.sync_api import Page, expect
from core.settings import config
from pages.inventory_page import InventoryPage

def test_direct_inventory_access(authenticated_page: Page, inventory_page: InventoryPage):
    """Тест, который проверяет мгновенный доступ к инвентарю без UI-логина."""
    
    # 1. Мы сразу переходим на внутреннюю страницу, логин не нужен!
    authenticated_page.goto(f"{config.BASE_URL}inventory.html")
    
    # 2. Проверяем, что нас не выкинуло на страницу логина
    expect(inventory_page.title).to_have_text("Products")