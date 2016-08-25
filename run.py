import sb_nation
import utils

logger = utils.make_logger("run")

sb_nation_blogs = sb_nation.get_all_blogs()
logger.info("Found {} SBNATION blogs".format(len(sb_nation_blogs)))

baseball_blogs = sb_nation.get_blogs_by_sport(sb_nation_blogs, sport_type=["Football","Soccer"])

for blog in baseball_blogs:
    print blog
    blog_url = blog['blog_url']

    post_list = sb_nation.get_blog_history(blog_url, 2016, 2016)
    print "{} posts in 2016".format(len(post_list))

    comments_list = sb_nation.get_blog_comments(blog_url, post_list, debug = True)
    print "{} comments in 2016".format(len(comments_list))
