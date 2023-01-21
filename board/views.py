import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from board.models import Post, Attachment
from crawlers.crawler import crawler_factory


@csrf_exempt
def get(request):
    if request.method == "POST":
        data = json.loads(request.body)

        parsed_data = get_post(data['url'])
        return HttpResponse(parsed_data)


def get_post(url):
    crawler = crawler_factory(url)

    site_ids: dict = crawler.get_target_site_ids()
    site_ids2 = list(site_ids.keys())
    # 중복 post 체크
    duplicate_posts = duplicate_check(crawler.site, site_ids.keys())

    # 리스트 중 중복이 아닌것만 남기기
    for post in duplicate_posts.values('site_id'):
        if post['site_id'] in site_ids:
            del site_ids[post['site_id']]

    # 새 post 가져오기
    posts = crawler.get_posts(site_ids)

    # 저장
    for post in posts:
        p = Post(url=post['url'],
                 title=post['title'],
                 body=post['body'],
                 published_datetime=post['published_datetime'],
                 site=post['site'],
                 site_id=post['site_id']
                 )
        p.save()

        for attachment in post['attachment_list']:
            att = Attachment(file_name=attachment, post=p)
            att.save()

    return Post.objects.filter(site=crawler.site, site_id__in=site_ids2)


def duplicate_check(site, site_ids):
    return Post.objects.filter(site=site,
                               site_id__in=site_ids)
