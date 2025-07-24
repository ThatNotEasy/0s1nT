from modules.args_parser import parse_args
from modules.socmed import SOCMED
from modules.banners import banners
import sys

if __name__ == '__main__':
    banners()
    try:
        args, logger = parse_args()
        socmed = SOCMED(logger=logger)
        socmed.input = args.input
        socmed.output = args.output  # This can be None now
        socmed.threads = args.threads
        socmed.instagram_checker()
        socmed.facebook_checker()
        socmed.tiktok_checker()
        socmed.x_checker()
        socmed.telegram_checker()
        socmed.lemon8_checker()
        socmed.threads_checker()
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        sys.exit(1)