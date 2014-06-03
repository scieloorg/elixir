import argparse
import logging

import feedstock

__version__ = '0.0.1'


def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    logging_config = {
        'level': allowed_levels.get(logging_level, 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }

    if logging_file:
        logging_config['filename'] = logging_file

    logging.basicConfig(**logging_config)


def main(pid, source_dir='.', logging_level='Info', logging_file=None, deposit_dir=None):

    _config_logging(logging_level, logging_file)

    logging.info('Starting to pack a document')

    if feedstock.is_valid_pid(pid):
        xml = feedstock.loadXML(pid)
        raw_data = feedstock.load_rawdata(pid)
        article = feedstock.Article(pid, xml, raw_data, source_dir, deposit_dir)

        article.wrap_document()


def argp():
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
        help='File to record all logging data, if None the log will be send to the standard out'
    )

    parser.add_argument(
        '--logging_level',
        '-l',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='File to record all logging data, if None the log will be send to the standard out'
    )

    parser.add_argument(
        '--deposit_dir',
        '-d',
        default=None,
        help='Directory to receive the packages'
    )

    args = parser.parse_args()

    main(
        args.pid,
        source_dir=args.source_dir,
        logging_level=args.logging_level,
        logging_file=args.logging_file,
        deposit_dir=args.deposit_dir
    )

if __name__ == "__main__":

    argp()
