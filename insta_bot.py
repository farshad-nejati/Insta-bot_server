import logging
import os
import sys
import os
from PIL import Image
from image_processing.image_processor import ImageProcessor
from instagram_uploader.uploader import InstagramUploader
from image_processing.excel_processor import ExcelProcessor


logger_dir_path = os.path.dirname(os.path.realpath(__file__))
logger_filename = os.path.join(logger_dir_path, 'server_log.log')

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(logger_filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


def do_logging(msg):
    logger.info(msg)



output_prefix = "output"
credential_file = "credentials.txt"
dir_path = os.path.abspath(os.path.dirname(__file__))


def geneateImage():
    do_logging('generating image...')
    # Example usage:
    image_processor = ImageProcessor(dir_path, output_prefix)
    excel_processor = ExcelProcessor(dir_path)
    output_image_path = image_processor.generate_image_from_excel(excel_processor)
    do_logging('generate image successfull')
    do_logging(f"Image saved at: {output_image_path}")


def createInstaPost(post_caption):
    do_logging("Login to Instagram...")

    uploader = InstagramUploader(dir_path, credential_file)
    
    # account_info = uploader.login_and_get_account_info()
    uploader.login_and_get_account_info()
    do_logging('login successful...')

    do_logging('Uploadng image...')
    uploaded_media_info = uploader.upload_image_to_instagram(post_caption, output_prefix)
    # print(account_info)
    # print(uploaded_media_info)
    do_logging('file uploaded successfully...')



if __name__ == '__main__':
    do_logging('\n')

     # Check if there is an argument
    if len(sys.argv) < 2:
        print("Failed to run. Usage: python3 /<file-path>/insta_bot.py '[caption]'")
        do_logging("Failed to run. Usage: python3 /<file-path>/insta_bot.py '[caption]'")
    else:
        # Get the caption from the command line argument
        post_caption = sys.argv[1]

        geneateImage()
        createInstaPost(post_caption)



