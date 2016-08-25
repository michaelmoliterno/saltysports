import requests
import requests_cache
from bs4 import BeautifulSoup
from datetime import date
import json
import logging

logger = logging.getLogger("get_data")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("get_data.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

SB_NATION_CONSTANT = 235959
# expire_after = 30 days
requests_cache.install_cache(expire_after=2592000)

def get_sb_nation_blogs():
    blogs = requests.get("http://www.sbnation.com/blogs")
    blogs_soup = BeautifulSoup(blogs.text, "html.parser")
    team_divs = blogs_soup.findAll("div", { "class" : "m-sitedir__entry" })

    sb_nation_blogs = {}
    for div in team_divs:

        blog_info = div.find('a')
        url = blog_info['href']
        blog_name = blog_info.find("h3", { "class" : "m-sitedir__entry-title" }).text
        team_name = blog_info.find("div", { "class" : "m-sitedir__entry-desc" }).text

        sb_nation_blogs[url] = {"blog_name":blog_name, "team_name":team_name}

    return sb_nation_blogs


def get_sb_nation_blog_history(blog_url = "http://www.talkingchop.com/", start_year = 2016, end_year = 2016):

    post_list = []
    for year in range(start_year,end_year+1):
        for month in range(1,13):
            target = "{}sbn_full_archive/entries_by_month?month={}&year={}".format(blog_url,month,year)
            posts = requests.get(target)
            posts_soup = BeautifulSoup(posts.text, "html.parser")
            posts = posts_soup.findAll("h3", { "class" : "m-full-archive__entry-title" })

            for post in posts:
                post_url =  post.find('a')['href']
                deets = post_url.split('/')
                year = int(deets[-5])
                month = int(deets[-4])
                day = int(deets[-3])
                post_id = int(deets[-2])
                post_text = deets[-1]

                post_date = date(year, month, day)

                post_summary = {"post_url":post_url,
                                "post_date":post_date,
                                "post_id":post_id,
                                "post_text":post_text
                                }

                post_list.append(post_summary)

    return post_list

def get_blog_comments(blog_url, post_list, debug = False):
    comments_list = []

    if debug == True:
        post_list = post_list[:10]

    for post in post_list:
        comment_id = post["post_id"] - SB_NATION_CONSTANT
        target = "{}comments/load_comments/{}".format(blog_url,comment_id)


        try:
            comments = requests.get(target)
        except requests.exceptions.ConnectionError as e:
            logger.error(e.message)
            logger.error("SKIPPING COMMENTS FOR {}".format(post["post_url"]))

        if comments.status_code == 200:
            comments_json = json.loads(comments.text)
            post_comments = comments_json["comments"]
            comments_list += post_comments

        else:
            logger.error("{} returned non-200 status_code {}".format(target,comments.status_code))


    if debug == True:
        if len(comments_list) > 0:
            print comments_list[0]["title"] + comments_list[0]["body"]

    return comments_list

def main():
    sb_nation_blogs = get_sb_nation_blogs()
    logger.info("Found {} SBNATION blogs".format(len(sb_nation_blogs)))

    for blog_url, blog_info in sb_nation_blogs.iteritems():
        print blog_url, blog_info["team_name"]

        post_list = get_sb_nation_blog_history(blog_url, 2016, 2016)
        print "{} posts in 2016".format(len(post_list))

        comments_list = get_blog_comments(blog_url, post_list, debug = True)
        print "{} comments in 2016".format(len(comments_list))
