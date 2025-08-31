from merlindb.cli import app as cli
from merlindb.logging import log  # noqa


def main():
    log.info("Starting merlin...")
    cli()


if __name__ == "__main__":
    main()
