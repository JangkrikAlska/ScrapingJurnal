import requests
from bs4 import BeautifulSoup
import time


class Walker:
    def __init__(self, url, q):
        self.url = url
        self.q = q

    def get_pagination(self, soup):
        try:
            pagination = soup.find_all('div', class_='text-center pagination-text')
            num_pagination_text = pagination[0].get_text()
            num_split = num_pagination_text.split()
            num_pagination = num_split[3]

            return num_pagination

        except Exception as e:
            print("Aborted, Keyword Not Found!!!")
            exit()

    def find_journal_name_and_link(self, soup):
        journal_name_selector = soup.find_all('div', class_='affil-name mb-3')
        link = []
        link_text = []
        for item in journal_name_selector:
            href = item.find(href=True)
            href_text = item.text.strip()
            link.append(href['href'])
            link_text.append(href_text.upper())

        return link_text, link

    def find_journal_detail_selector(self, soup):
        journal_detail_selector = soup.find_all('div', class_='affil-abbrev')
        gs = []
        web = []
        editor_url = []
        detail_selector = []

        for item in journal_detail_selector:
            href = item.find_all('a', href=True)
            links = [item['href'] for item in href]
            detail_selector.append(links)

        for dt in detail_selector:
            for d in range(len(dt)):
                _gs = dt[0]
                _web = dt[1]
                _edt = dt[2]

            gs.append(_gs)
            web.append(_web)
            editor_url.append(_edt)

        return gs, web, editor_url

    def find_journal_affiliation_name_and_link(self, soup):
        journal_aff_selector = soup.find_all('div', class_='affil-loc mt-2')
        aff = []
        aff_link = []

        for item in journal_aff_selector:
            href = item.find(href=True)
            href_text = item.text.strip()
            aff_link.append(href['href'])
            aff.append(href_text.upper())

        return aff, aff_link

    def find_accreditation(self, soup):
        journal_accr_selector = soup.find_all('span', class_='num-stat accredited')
        accr = []

        for accr_ in journal_accr_selector:
            accr_split = accr_.text.split()
            accr.append(accr_split[0])

        return accr

    def store_to_csv(self, data):
        import csv
        import time

        timestr = time.strftime("%Y%m%d-%H%M%S")
        timestr_tgl = time.strftime("%Y%m%d")
        header_info = [{'1': 'Nama Jurnal', '2': 'Link Jurnal', '3': 'Google Scholar', '4': 'Website',
                        '5': 'Editor URL', '6': 'Nama Afiliasi', '7': 'Link Afiliasi', '8': 'Akreditasi'}]
        filename = timestr_tgl + '-sinta_dump-' + self.q + '.csv'

        with open(filename, 'a', encoding='UTF8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys(), delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            if not csvfile.tell():
                writer.writeheader()

            writer.writerows(data)

    def run(self):
        __url = self.url
        __kw = self.q
        num_of_page = 1  
        url_parse = f"{__url}?q={__kw}"
        page = requests.get(url_parse)
        soup = BeautifulSoup(page.content, 'html.parser')
        gp = self.get_pagination(soup)
        num_idx = int(gp)

        for num in range(1, num_idx + 1):
            url_parse = f"{__url}?page={num}&q={__kw}"
            page = requests.get(url_parse)
            soup = BeautifulSoup(page.content, 'html.parser')
            print(url_parse)

            jn, jl = self.find_journal_name_and_link(soup)
            jgs, jweb, jeditor = self.find_journal_detail_selector(soup)
            jan, jal = self.find_journal_affiliation_name_and_link(soup)
            accr = self.find_accreditation(soup)
            time.sleep(5)
            profile = [{'Nama Jurnal': jn, 'Link Jurnal': jl, 'Google Scholar': jgs, 'Website': jweb,
                        'Editor URL': jeditor, 'Nama Afiliasi': jan, 'Link Afiliasi': jal, 'Akreditasi': accr}
                       for jn, jl, jgs, jweb, jeditor, jan, jal, accr in zip(jn, jl, jgs, jweb, jeditor, jan,
                                                                        jal, accr)]
            self.store_to_csv(profile)
        print('Selesai!')


_url = "https://sinta.kemdikbud.go.id/journals/"
_kw = "teknologi informasi"
walker = Walker(_url, _kw)

try:
    walker.run()
except Exception as e:
    print(e)