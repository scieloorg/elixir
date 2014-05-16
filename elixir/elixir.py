import argparse
import requests

__version__ = '0.0.1'


def main(*args, **kwargs):
    print(kwargs['pid'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a article package from the legacy data")
    parser.add_argument(
        '--pid',
        '-p',
        default=None,
        help='Document ID, must be the PID number'
    )

    args = parser.parse_args()

    main(pid=args.pid)
