"""
.. include:: ../README.md
   :start-line: 2
   :end-before: Contribution
"""

import logging
import os

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "DEBUG"))
