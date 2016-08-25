import requests
from datetime import date
import json

import requests_cache
import bs4

import utils
import settings

# expire_after = 30 days
requests_cache.install_cache(expire_after=2592000)
logger = utils.make_logger("get_data")

def get_sb_nation_blogs():

    sb_nation_blogs = []

    blogs = requests.get("http://www.sbnation.com/blogs")
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


def get_sb_nation_blog_history(blog_url = "http://www.talkingchop.com/", start_year = 2016, end_year = 2016):

    post_list = []
    for year in range(start_year,end_year+1):
        for month in range(1,13):
            target = "{}sbn_full_archive/entries_by_month?month={}&year={}".format(blog_url,month,year)
            posts = requests.get(target)
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
        comment_id = post["post_id"] - settings.SB_NATION_CONSTANT
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

    return comments_list


def get_blogs_by_sport(sb_nation_blogs, sport_type="Baseball"):
    blogs = [blog for blog in sb_nation_blogs if blog["sport_type"] == sport_type]
    return blogs

def main():
    sb_nation_blogs = get_sb_nation_blogs()
    logger.info("Found {} SBNATION blogs".format(len(sb_nation_blogs)))

    baseball_blogs = get_blogs_by_sport(sb_nation_blogs, sport_type="Baseball")

    for blog in baseball_blogs:
        print blog
        blog_url = blog['blog_url']

        post_list = get_sb_nation_blog_history(blog_url, 2016, 2016)
        print "{} posts in 2016".format(len(post_list))

        comments_list = get_blog_comments(blog_url, post_list, debug = True)
        print "{} comments in 2016".format(len(comments_list))

main()
