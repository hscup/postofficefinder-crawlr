from random import randrange
from time import sleep
import logging

import requests
from lxml import html

from cutils.cutils import CsvHelper
from us_states import states

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'

logging.basicConfig(filename='crawlr.log', format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

class PofCrawler():
    def __init__(self, csv_writer=None, *args, **kwargs):
        self.csv_writer = csv_writer if csv_writer else CsvHelper()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def crawl(self, url):
        logging.info('Crawling {}'.format(url))
        # Store scraped office
        office_info = []
        # Addding state, city, county, zipcode
        split_url = url.split('/')
        for i in range(-6, -2):
            if i == -6:
                office_info.append(states.get(split_url[i].upper()))
                continue
            office_info.append(split_url[i].replace('-', ' ').title())

        headers = {'user-agent': USER_AGENT}
        try:
            sleep(randrange(1, 3))
            page = requests.get(url, headers=headers)
            if page.status_code != 200:
                logging.warn('Can not make request to {}, request return {}'.format(url, page.status_code))
                return
        except Exception as ex:
            return

        try:
            page = html.fromstring(page.content)
            body = page.xpath('//body')[0]

            header = ''.join(body.xpath(
                './/h1[@itemprop="name"]/text()')).strip()
            office_info.append(header)

            # Address
            address = ''.join(body.xpath(
                './/div[@class="post_office"]/div[@class="address_sec"]/p[@class="address"]/text()'))
            parking = ''.join(body.xpath(
                './/div[@class="post_office"]/div[@class="address_sec"]/p[@class="parking"]/text()'))

            office_info.append(address)
            office_info.append(parking)

            # Phones
            phones = body.xpath(
                './/div[@class="post_office"]/div[@class="phones"]/p')
            phone_info = []
            for phone in phones:
                phone_info.append(': '.join(phone.xpath('.//span/text()')))

            office_info.append(' | '.join(phone_info))

            # Retail hours
            retail_hours = body.xpath(
                './/div[@class="post_office"]/div[contains(@class, "retail_hours")]/descendant::li')
            retail_hour_info = []
            for retail_hour in retail_hours:
                retail_hour_info.append(
                    ': '.join(retail_hour.xpath('.//span/text()')))
            office_info.append(' | '.join(retail_hour_info))

            # Lobby Hours
            lobby_hours = body.xpath(
                './/div[@class="post_office"]/div[contains(@class, "lobby_hours")]/descendant::li')
            lobby_hour_info = []
            for lobby_hour in lobby_hours:
                lobby_hour_info.append(
                    ': '.join(lobby_hour.xpath('.//span/text()')))
            office_info.append(' | '.join(lobby_hour_info))

            # Last Collection Hours
            hour_nodes = body.xpath(
                './/div[@class="post_office"]/div[contains(@class, "last_collection_hours")]/descendant::li')
            hours = []
            for hour in hour_nodes:
                hours.append(': '.join(hour.xpath('.//span/text()')))
            office_info.append(' | '.join(hours))

            # Passport Photo Hours
            hour_nodes = body.xpath(
                './/div[@class="post_office"]/div[contains(@class, "passport_photo_hours")]/descendant::li')
            hours = []
            for hour in hour_nodes:
                hours.append(': '.join(hour.xpath('.//span/text()')))
            office_info.append(' | '.join(hours))

            # Carrier Facility Hours
            hour_nodes = body.xpath(
                './/div[@class="post_office"]/div[contains(@class, "carrier_facility_hours")]/descendant::li')
            hours = []
            for hour in hour_nodes:
                hours.append(': '.join(hour.xpath('.//span/text()')))
            office_info.append(' | '.join(hours))

            # PO Box Access Hours
            hour_nodes = body.xpath(
                './/div[@class="post_office"]/div[contains(@class, "po_box_access_hours")]/descendant::li')
            hours = []
            for hour in hour_nodes:
                hours.append(': '.join(hour.xpath('.//span/text()')))
            office_info.append(' | '.join(hours))

            # Pickup Services Hours
            hour_nodes = body.xpath(
                './/div[@class="post_office"]/div[contains(@class, "pickup_services_hours")]/descendant::li')
            hours = []
            for hour in hour_nodes:
                hours.append(': '.join(hour.xpath('.//span/text()')))
            office_info.append(' | '.join(hours))

            # Global Express Guaranteed Hours
            hour_nodes = body.xpath(
                './/div[@class="post_office"]/div[contains(@class, "global_express_guaranteed_hours")]/descendant::li')
            hours = []
            for hour in hour_nodes:
                hours.append(': '.join(hour.xpath('.//span/text()')))
            office_info.append(' | '.join(hours))

            # On-Site Services
            services = body.xpath(
                './/div[@class="post_office"]/div[contains(@class, "service_section on_site_services")]/descendant::li/text()')
            office_info.append(' | '.join(services))

        except Exception:
            pass
        finally:
            office_info = [
                ''.join([i if ord(i) < 128 else ' ' for i in text]) for text in office_info]
            if self.csv_writer:
                self.csv_writer.save_to_csv(office_info)


def main():
    print("""
        Ctrl + C -> Enter to quit
    """)

    urls = []
    with open('urls.txt', mode='r') as f:
        urls = f.read().splitlines()
        urls = [line.strip() for line in urls]

    # Set header fields
    headers = [
        "State",
        "County",
        "City",
        "Zipcode",
        "Title",
        "Address",
        "Parking",
        "Phones",
        "Retail Hours",
        "Lobby Hours",
        "Last Collection Hours",
        "Passport Photo Hours",
        "Carrier Facility Hours",
        "PO Box Access Hours",
        "Pickup Services Hours",
        "Global Express Guaranteed Hours",
        "On-Site Services"
    ]

    crawlr = PofCrawler()
    output_file = 'data.csv'
    crawlr.csv_writer = CsvHelper(output_file, mode='a', encoding='utf-8')
    crawlr.csv_writer.set_headers(headers)

    for url in urls:
        try:
            crawlr.crawl(url)
        except Exception:
            pass


if __name__ == '__main__':
    main()
