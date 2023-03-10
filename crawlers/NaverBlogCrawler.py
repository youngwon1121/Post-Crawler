import json
import re
import zoneinfo
from datetime import timedelta
from typing import List
from urllib.parse import urlparse, parse_qsl, unquote

from bs4 import BeautifulSoup
from django.utils import timezone

from crawlers.BaseCrawler import RequestCrawler


class NaverBlogCrawler(RequestCrawler[str]):

    def __init__(self, url):
        super().__init__(url)
        self.site = "NAVERBLOG"
        self.parsed_url = urlparse(url)

    def _parse_index(self, data) -> List[str]:
        urls = []

        url = self.parsed_url
        data = unquote(data).replace("\\", "").replace("\'", "")
        data = json.loads(data, strict=False)
        query = dict(parse_qsl(self.parsed_url.query))
        for post_data in data['postList'][:10]:
            query['logNo'] = post_data['logNo']
            q = "&".join([f"{k}={v}" for k, v in query.items()])
            urls.append(str(url._replace(path='/PostView.nhn', query=q).geturl()))
        return urls

    def _parse_post(self, html, data: str):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.select_one(".se-title-text span").get_text(strip=True)
        body = soup.find(class_="se-main-container")
        published_datetime = soup.find(class_="se_publishDate").get_text(strip=True)
        attachment_list = [item.get_text(strip=True) for item in soup.find_all(class_="se-file-name-container")]
        published_datetime = self._parse_datetime(published_datetime)
        return {
            'title': title,
            'body': str(body),
            'published_datetime': published_datetime,
            'attachment_list': attachment_list
        }

    def site_id_from_data(self, data) -> str:
        """
        url로 부터 unique한 siteid 생성
        """
        data = urlparse(data)
        query = dict(parse_qsl(data.query))
        return 'blogId=' + str(query.get('blogId')) + "&" + 'logNo=' + str(query.get('logNo'))

    def _parse_datetime(self, dt):
        if r := re.search(r'(\d+)(?=분 전)', dt):
            return timezone.now() - timedelta(minutes=int(r.group()))

        elif r := re.search(r'(\d+)(?=시간 전)', dt):
            return timezone.now() - timedelta(hours=int(r.group()))

        else:
            return timezone.datetime.strptime(dt, '%Y. %m. %d. %H:%M').replace(tzinfo=zoneinfo.ZoneInfo("Asia/Seoul"))

    def get_listing_url(self):
        query = dict(parse_qsl(self.parsed_url.query))
        query['currentPage'] = '1'
        query['countPerPage'] = '10'
        query = "&".join([f"{k}={v}" for k, v in query.items()])
        return self.parsed_url._replace(path='/PostTitleListAsync.naver', query=query).geturl()

    def url_from_data(self, data: str):
        return data
