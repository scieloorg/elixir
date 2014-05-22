import argparse
import logging

from elixir import feedstock

__version__ = '0.0.1'


def pack_document(*args, **kwargs):

    logging.info('Starting to pack a document')
    if feedstock.is_valid_pid(kwargs['pid']):
        xml = feedstock.loadXML(kwargs['pid'])
        raw_data = feedstock.load_rawdata(kwargs['pid'])
        article = feedstock.Article(kwargs['pid'], xml, raw_data, kwargs['source_dir'])

        article_htmls = article.images


def main():
    parser = argparse.ArgumentParser(
        description="Create a article package from the legacy data")
    parser.add_argument(
        '--pid',
        '-p',
        default=None,
        help='Document ID, must be the PID number'
    )
    parser.add_argument(
        '--source_dir',
        '-s',
        default='.',
        help='Source directory where the pdf, images and html\'s cold be fetched'
    )

    parser.add_argument(
        '--logging_file',
        '-o',
        default=None,
        help='File to record all logging data, if None the log will be send to the standard out.'
    )

    parser.add_argument(
        '--logging_level',
        '-l',
        default=logging.DEBUG,
        help='File to record all logging data, if None the log will be send to the standard out.'
    )

    args = parser.parse_args()

    logging_config = {'level': args.logging_level, 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}

    if args.logging_file:
        logging_config['filename'] = args.logging_file

    logging.basicConfig(**logging_config)

    pack_document(pid=args.pid, source_dir=args.source_dir)

if __name__ == "__main__":

    main()
