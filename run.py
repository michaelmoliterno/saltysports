import sb_nation
import utils
import settings

logger = utils.make_logger("run")

sb_nation_blogs = sb_nation.get_all_blogs()
blogs = sb_nation.get_blogs_by_sport(sb_nation_blogs, settings.SPORT_TYPES)

logger.info("about to look for posts and comments from {} blogs".format(len(blogs)))
sb_nation.download_blog_comments(blogs, 2016, 2016, False)
