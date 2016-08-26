from datetime import datetime
import json
import time
import math


import bs4
import pymongo

import utils
import settings

logger = utils.make_logger("sb_nation")

def get_all_blogs():

    sb_nation_blogs = []
    blogs = utils.get_response_from_target("http://www.sbnation.com/blogs")
    blogs_soup = bs4.BeautifulSoup(blogs.text, "html.parser")
    team_divs = blogs_soup.find("div", { "class" : "l-main-float" })

    sport_type = None

    for i, element in enumerate(team_divs):
        if type(element) == bs4.element.Tag:
            if element.name == "h2":
                sport_type = element.text
            elif element.name == "div":
                blog_info = element.find('a')
                url = blog_info['href']
                blog_name = blog_info.find("h3", { "class" : "m-sitedir__entry-title" }).text
                team_name = blog_info.find("div", { "class" : "m-sitedir__entry-desc" }).text

                blog_dict = {"blog_url":url,
                             "blog_name":blog_name,
                             "team_name":team_name,
                             "sport_type":sport_type,}

                sb_nation_blogs.append(blog_dict)

    return sb_nation_blogs


def get_blog_history(blog_url = "http://www.talkingchop.com/", start_year = 2016, end_year = 2016, debug = False):

    month_range = range(1,13)
    if debug == True:
        month_range = range(8,9)

    post_list = []
    for year in range(start_year,end_year+1):
        for month in month_range:
            utils.sleepy_time(factor = 1, min_sleep = 1, max_sleep = 3, log = False)
            target = "{}sbn_full_archive/entries_by_month?month={}&year={}".format(blog_url,month,year)

            posts = utils.get_response_from_target(target)

            posts_soup = bs4.BeautifulSoup(posts.text, "html.parser")
            posts = posts_soup.findAll("h3", { "class" : "m-full-archive__entry-title" })

            for post in posts:
                post_url =  post.find('a')['href']
                deets = post_url.split('/')
                year = int(deets[-5])
                month = int(deets[-4])
                day = int(deets[-3])
                post_id = int(deets[-2])
                post_text = deets[-1]

                post_date = datetime(year, month, day, 0, 0)

                post_summary = {"post_url":post_url,
                                "post_date":post_date,
                                "post_id":post_id,
                                "post_text":post_text
                                }

                post_list.append(post_summary)

    return post_list

def get_blog_comments(blog_url, post_list, debug = False):

    if debug == True:
        post_list = post_list[:10]

    comments_list = []
    for i, post in enumerate(post_list):
        utils.sleepy_time(factor = 1, min_sleep = 5, max_sleep = 10, log = False)
        comment_id = post["post_id"] - settings.SB_NATION_CONSTANT
        target = "{}comments/load_comments/{}".format(blog_url,comment_id)

        comments = utils.get_response_from_target(target)
        comments_json = json.loads(comments.text)
        post_comments = comments_json["comments"]
        comments_list += post_comments

        if i%100 == 0:
            logger.info("got comments for post {}".format(i+1))

    return comments_list


def get_blogs_by_sport(sb_nation_blogs, sport_type=["Baseball"]):
    blogs = [blog for blog in sb_nation_blogs if blog["sport_type"] in sport_type]
    return blogs

def download_blog_comments(blogs, start_year = 2016, end_year = 2016, debug = False):

    blog_posts = utils.get_mongo_collection("blog_posts")
    blog_posts.create_index([("post_id", pymongo.ASCENDING)], unique = True)

    comments = utils.get_mongo_collection("comments")
    comments.create_index([("id", pymongo.ASCENDING)], unique = True)

    for blog in blogs:

        blog_url = blog['blog_url']
        print blog_url
        logger.info("reading {}".format(blog['blog_url']))

        post_list = get_blog_history(blog_url, start_year, end_year, debug)
        logger.info("found {} posts".format(len(post_list)))

        #save the posts
        for post in post_list:
            try:
                blog_posts.insert(post)
            except pymongo.errors.DuplicateKeyError as e:
                pass


        comments_list = get_blog_comments(blog_url, post_list, debug)
        logger.info("found {} comments".format(len(comments_list)))

        #save the comments
        for comment in comments_list:
            try:
                comments.insert(comment)
            except pymongo.errors.DuplicateKeyError as e:
                pass
