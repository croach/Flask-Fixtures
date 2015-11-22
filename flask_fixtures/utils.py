"""
    flask.ext.fixtures.helpers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Helper functions.

    :copyright: (c) 2015 Christopher Roach <ask.croach@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import inspect
import os
import sys


def print_msg(msg, header, file=sys.stdout):
    """Prints a boardered message to the screen"""
    DEFAULT_MSG_BLOCK_WIDTH = 60

    # Calculate the length of the boarder on each side of the header and the
    # total length of the bottom boarder
    side_boarder_length = (DEFAULT_MSG_BLOCK_WIDTH - (len(header) + 2)) // 2
    msg_block_width = side_boarder_length * 2 + (len(header) + 2)

    # Create the top and bottom boarders
    side_boarder = '#' * side_boarder_length
    top_boarder = '{0} {1} {2}'.format(side_boarder, header, side_boarder)
    bottom_boarder = '#' * msg_block_width

    def pad(line, length):
        """Returns a string padded and centered by the given length"""
        padding_length = length - len(line)
        left_padding = ' ' * (padding_length//2)
        right_padding = ' ' * (padding_length - len(left_padding))
        return '{0} {1} {2}'.format(left_padding, line, right_padding)

    words = msg.split(' ')
    lines = []
    line = ''
    for word in words:
        if len(line + ' ' + word) <= msg_block_width - 4:
            line = (line + ' ' + word).strip()
        else:
            lines.append('#{0}#'.format(pad(line, msg_block_width - 4)))
            line = word
    lines.append('#{0}#'.format(pad(line, msg_block_width - 4)))

    # Print the full message
    print(file=file)
    print(top_boarder, file=file)
    print('#{0}#'.format(pad('', msg_block_width - 4)), file=file)
    for line in lines:
        print(line, file=file)
    print('#{0}#'.format(pad('', msg_block_width - 4)), file=file)
    print(bottom_boarder, file=file)
    print(file=file)

def print_info(msg):
    print_msg(msg, 'INFORMATION')

def can_persist_fixtures():
    """Returns True if it's possible to persist fixtures across tests.

    Flask-Fixtures uses the setUpClass and tearDownClass methods to persist
    fixtures across tests. These methods were added to unittest.TestCase in
    python 2.7. So, we can only persist fixtures when using python 2.7.
    However, the nose and py.test libraries add support for these methods
    regardless of what version of python we're running, so if we're running
    with either of those libraries, return True to persist fixtures.

    """
    # If we're running python 2.7 or greater, we're fine
    if sys.hexversion >= 0x02070000:
        return True

    # Otherwise, nose and py.test support the setUpClass and tearDownClass
    # methods, so if we're using either of those, go ahead and run the tests
    filename = inspect.stack()[-1][1]
    executable = os.path.split(filename)[1]
    return executable in ('py.test', 'nosetests')

