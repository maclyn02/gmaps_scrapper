from driver_conf import (
    BASE_URL,
    getChromeDriver,
    getChromeOptions,
    setBrowserIncognito,
    setHeadless,
    setIgnoreCertificateError,
)

from selenium.webdriver.common.keys import Keys
import pandas
import time
import json
from datetime import datetime

REPORT_PATH = "wishlist.json"


class GenerateReport:
    def __init__(self, results_dictionary):

        with open(REPORT_PATH, "w", encoding='utf8') as result_file:
            json.dump(results_dictionary, result_file, ensure_ascii=False)
        print(f"JSON file created at: ./{REPORT_PATH}")


class PlaceScrapper:
    def __init__(self, base_url):
        self.base_url = base_url
        options = getChromeOptions()
        setBrowserIncognito(options)
        setIgnoreCertificateError(options)
        self.driver = getChromeDriver(options)
        self.final_list = []

    def get_results_dict(self):
        return self.final_list

    def go_to_base_page(self):
        self.driver.get(self.base_url)

        frame = self.driver.find_element_by_css_selector("iframe.widget-consent-frame")
        self.driver.switch_to.frame(frame)
        self.driver.find_element_by_xpath("//span[text()='I agree']").click()
        self.driver.switch_to.default_content()

    def run(self, place):
        full_url, image_url, address, plus_code = self.search(place)

        wishlist = {}
        wishlist["place_name"] = place
        coordinates = full_url.split('/@')[1].split(',')
        wishlist["lat"] = float(coordinates[0])
        wishlist["lng"] = float(coordinates[1])
        wishlist["image_url"] = f"{image_url}"
        wishlist["address"] = address
        wishlist["plus_code"] = plus_code
        if plus_code != "N/A":
            wishlist["country"] = plus_code.split(", ")[-1].strip()
        elif address != "N/A":
            wishlist["country"] = address.split(", ")[-1].strip()
        else:
            wishlist["country"] = "N/A"

        self.final_list.append(wishlist)

    def search(self, place):

        search_box = self.driver.find_element_by_css_selector("input#searchboxinput")
        search_box.clear()
        search_box.send_keys(place)
        search_box.send_keys(Keys.ENTER)

        time.sleep(4)

        try:
            image = self.driver.find_element_by_css_selector(
                ".section-hero-header-image-hero-container img"
            )
            image_url = image.get_property("src")
        except Exception as e:
            image_url = "https://agrimerica-equip.com/wp-content/plugins/oem-showcase-inventory/assets/images/noimage-found.png"

        try:
            address = self.driver.find_element_by_css_selector(
                "button[data-item-id='address']"
            ).get_attribute("aria-label")
        except Exception as e:
            address = "N/A"

        try:
            plus_code = self.driver.find_element_by_css_selector(
                "button[data-item-id='oloc']"
            ).get_attribute("aria-label")
        except Exception as e:
            plus_code = "N/A"

        return self.driver.current_url, image_url, address, plus_code

    def quit_browser(self):
        self.driver.quit()


if __name__ == "__main__":
    scrapper = PlaceScrapper(BASE_URL)
    scrapper.go_to_base_page()

    wishlist = pandas.read_csv("Want to go.csv", index_col=False)
    shortened_wishlist = wishlist["Title"][728:880]

    try:
        for place in shortened_wishlist:
            scrapper.run(place)
    except Exception as e:
        print(f"Exception Occured: {e}")
    finally:
        scrapper.quit_browser()
        GenerateReport(scrapper.get_results_dict())
