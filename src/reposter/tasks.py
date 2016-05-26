# -- coding: utf-8 --
import time
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from constance import config

from vk.exceptions import VkException
from reposter.vk_api import vk_api

from conf.app_celery import app
from reposter.models import Post, Public


api = vk_api.get_api()


@app.task(name='repost_posts')
def repost_posts():
    for_repost = Post.objects.filter(is_repost=False).order_by('vk_id')
    auth_api = vk_api.get_authorized_api()

    for post in for_repost:
        kwargs = {
            'object': post.vk_obj_uri,
            'message': config.VK_REPOST_MESSAGE,
        }
        if config.VK_REPOST_TO:
            kwargs['group_id'] = get_group_id(config.VK_REPOST_TO)

        try:
            time.sleep(settings.VK_API_INTERVAL)
            auth_api.wall.repost(**kwargs)
        except VkException:
            time.sleep(settings.VK_API_INTERVAL * 60)
            auth_api = vk_api.get_authorized_api()
            auth_api.wall.repost(**kwargs)

        post.is_repost = True
        post.save()


def get_group_id(group_name_or_id):
    group = api.groups.getById(group_id=group_name_or_id)[0]
    return group['id']


@app.task(name='parse_posts')
def parse_posts():
    """ Запускает парс новых постов из пабликов
    :return:
    """
    for public in Public.objects.all():
        try:
            group = api.groups.getMembers(group_id=public.public_name, count=0)
            subscribers = group['count']
        except VkException:
            # если парсим не паблик группы, а пользовательский
            user = api.users.get(user_ids=public.public_name)[0]
            followers = api.users.getFollowers(user_id=user['uid'], count=0)
            subscribers = followers['count']

        public.subscriber_count = subscribers
        parse_new_posts(public)
        public.last_parse = timezone.now()
        public.save()


def parse_new_posts(public):
    """ Парсит новые посты из паблика
    :return:
    """
    offset = 0
    parsed_all_post = False
    posts = api.wall.get(domain=public.public_name,
                         count=settings.VK_POST_COUNT,
                         offset=offset)

    while not parsed_all_post:
        parsed_all_post = save_posts_and_check_exist(public, posts['items'])

        if not parsed_all_post:
            offset += settings.VK_POST_COUNT
            time.sleep(settings.VK_API_INTERVAL)
            posts = api.wall.get(domain=public.public_name,
                                 count=settings.VK_POST_COUNT,
                                 offset=offset)
            if not posts['items']:
                # если нет элементов дошли до конца
                parsed_all_post = True


def save_posts_and_check_exist(public, posts):
    """ Сохраняем посты в БД, пока не наткнёмся на дубликат
    :param public: паблик
    :param posts: посты
    :return: bool нашли уже сохранённый пост
    """
    parsed_all_post = False
    for data in posts:
        post = Post(
            public=public,
            vk_id=data['id'],
            owner_id=data['owner_id'],
            text=data['text'],
            like_count=data['likes']['count'],
            repost_count=data['reposts']['count'],
            subscriber_count=public.subscriber_count,
            publication_time=data['date']
        )

        if post.rating < config.VK_RATING_LIMIT:
            # пропускаем объявления с слишком высоким рейтингом
            try:
                Post.objects.get(public=public, vk_id=data['id'])
                # api возвращает объекты по порядку, если объект уже сохранён
                # в БД - дошли до последнего значит дальше пойдут уже
                # сохранённые объекты
                parsed_all_post = True
            except Post.DoesNotExist:
                try:
                    post.save()
                except IntegrityError:
                    pass

    return parsed_all_post
