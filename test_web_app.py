import pytest
import os
from Web_App import app
from selenium.webdriver.common.by import By


def test_homepage_load(dash_duo):
    dash_duo.start_server(app)

    intro_content = dash_duo.find_element("#introduction-text")
    assert "Users can choose their required boroughs and crime with" in intro_content.text

    screenshot_dir = r"D:\Pythonpro\CW1\Pytest Screenshot"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    screenshot_path = os.path.join(screenshot_dir, "tab1-screenshot.png")
    dash_duo.driver.save_screenshot(screenshot_path)

def test_line_chart_interaction(dash_duo):
    dash_duo.start_server(app)

    tab2 = dash_duo.driver.find_element(By.XPATH, "//a[text()='Crime Change in Time']")
    tab2.click()
    dash_duo.select_dcc_dropdown("#Location", "BARNET")
    dash_duo.select_dcc_dropdown("#Crime-Types", "arson")
    dash_duo.wait_for_element("#line-chart", timeout=10)
    line_chart = dash_duo.find_element("#line-chart")
    assert "11" in line_chart.get_attribute("innerHTML")

    screenshot_dir = r"D:\Pythonpro\CW1\Pytest Screenshot"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    screenshot_path = os.path.join(screenshot_dir, "tab2-screenshot.png")
    dash_duo.driver.save_screenshot(screenshot_path)

def test_pie_chart_interaction(dash_duo):
    dash_duo.start_server(app)

    tab3 = dash_duo.driver.find_element(By.XPATH, "//a[text()='Crime Distribution']")
    tab3.click()

    dash_duo.wait_for_element("#allocation_pie_chart", timeout=15)
    serial_table = dash_duo.find_element("#serial-table")
    assert "HACKNEY" in serial_table.get_attribute("innerHTML")


    screenshot_dir = r"D:\Pythonpro\CW1\Pytest Screenshot"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    screenshot_path = os.path.join(screenshot_dir, "tab3-screenshot.png")
    dash_duo.driver.save_screenshot(screenshot_path)

def test_search_tab_callback(dash_duo):
    dash_duo.start_server(app)

    tab5 = dash_duo.driver.find_element(By.XPATH, "//a[text()='Search']")
    tab5.click()

    dash_duo.wait_for_element("#year-input", timeout=15)
    year_input = dash_duo.find_element("#year-input")
    year_input.clear()
    year_input.send_keys("2019")

    dash_duo.wait_for_element("#crime-input", timeout=15)
    crime_input = dash_duo.find_element("#crime-input")
    crime_input.clear()
    crime_input.send_keys("trafficking of drugs")

    dash_duo.find_element("#borough-input").click()

    dash_duo.wait_for_element("table", timeout=10)

    xpath_expr = "//table//tr/td[4][contains(., 'trafficking of drugs')]"
    cells = dash_duo.driver.find_elements(By.XPATH, xpath_expr)

    assert len(cells) > 0

    screenshot_dir = r"D:\Pythonpro\CW1\Pytest Screenshot"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    screenshot_path = os.path.join(screenshot_dir, "tab5-screenshot.png")
    dash_duo.driver.save_screenshot(screenshot_path)
