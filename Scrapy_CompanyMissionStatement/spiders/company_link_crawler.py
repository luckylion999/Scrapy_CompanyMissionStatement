import scrapy
import xlrd
from Scrapy_CompanyMissionStatement.items import CompanyItem
from urllib.parse import urlparse


class CompanyCrawler(scrapy.Spider):
    name = 'company_link_crawler'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/67.0.3396.99 Safari/537.36',
    }
    search_url = 'https://www.google.com/search?q={}'
    allowed_domains = ['google.com']

    def start_requests(self):
        company_list = []
        type_list = []
        # file = xlrd.open_workbook("Current Customers for FinEd.xlsx")
        file = xlrd.open_workbook("FinEd prospects_2_ST (1).xlsx")
        sheet = file.sheet_by_index(0)
        # for k in range(1, sheet.nrows):
        #     company_list.append(str(sheet.row_values(k)[1]))
        #     type_list.append(str(sheet.row_values(k)[2]))
        for k in range(1, sheet.nrows):
            company_list.append(str(sheet.row_values(k)[0]))

        for i in range(len(company_list)):
            # word = company_list[i] + ' ' + type_list[i]
            word = company_list[i]
            item = CompanyItem()
            item['company_name'] = company_list[i]
            yield scrapy.Request(
                url=self.search_url.format(word).replace('&', '%26'),
                callback=self.parse,
                headers=self.headers,
                meta={'item': item},
            )

        # item = CompanyItem()
        # item['company_name'] = 'BBVA Compass'
        # yield scrapy.Request(
        #     url=self.search_url.format('F&M Bank Iowa').replace('&', '%26'),
        #     callback=self.parse,
        #     headers=self.headers,
        #     meta={'item': item},
        # )

    def parse(self, response):
        item = response.meta.get('item')
        domain = response.xpath('//cite')[0].xpath('.//text()').extract()
        if domain:
            domain = ''.join(domain)
            if 'http' not in domain:
                domain = 'http://' + domain
            if '›' in domain:
                domain = domain.split('›')[0].strip()
            parsed_uri = urlparse(domain)
            item['company_link'] = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            if '..' in item['company_link']:
                print('error')
        else:
            item['company_link'] = None
        yield item
