import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # not really necessary but I will keep it, just au cas ou

from .config import Config
from .cookbook import DjeliaCookbook


def main():
    config = Config.load()
    cookbook = DjeliaCookbook(config)
    cookbook.run()


if __name__ == "__main__":
    main()
