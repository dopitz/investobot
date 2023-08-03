#!/usr/bin/env python3

import sys

from tools.complete import Complete
from tools.backup import Backup
from tools.docimport import Docimport
from tools.alias import Alias
from tools.track import Track
from tools.stats import Stats
from tools.intrinsicvalue import IntrinsicValue

import model.estimate_provision

tools = {
    'backup': Backup(),
    'docimport': Docimport(),
    'alias': Alias(),
    'track': Track(),
    'stats': Stats(),
    'intrinsic-value': IntrinsicValue(),
}

if len(sys.argv) >= 2:

    if sys.argv[1] == 'complete':
        Complete().run(tools)
        exit()

    if sys.argv[1] in tools:
        tools[sys.argv[1]].run()
        exit()

print("help")
exit()