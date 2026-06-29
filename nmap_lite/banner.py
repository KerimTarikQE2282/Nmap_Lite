"""ASCII banner + legal/ethical warning shown on every run."""

BANNER = r"""


 _   _ __  __    _    ____     _    ___ _____ ___
| \ | |  \/  |  / \  |  _ \   | |  |_ _|_   _| __|
|  \| | |\/| | / _ \ | |_) |  | |   | |  | | |  _|
| |\  |  | | |/ ___ \|  __/   | |___| |  | | | |__
|_| \_|_|  |_/_/   \_\_|      |_____|___| |_|_____|

        N M A P - L I T E   //  consistency-checked scanner
"""

WARNING = """
==============================================================
  WARNING - READ BEFORE USE
==============================================================
  This tool is provided strictly for EDUCATIONAL PURPOSES and
  for use against systems you OWN or have EXPLICIT WRITTEN
  AUTHORIZATION to test.

  Scanning networks or hosts without permission may violate
  laws (e.g. the Computer Fraud and Abuse Act, the UK Computer
  Misuse Act, or local equivalents) and/or the target's terms
  of service.

  The author(s) of this tool assume NO liability and provide
  NO warranty for any use, misuse, or consequences arising
  from its use. Anything you do with this tool is entirely
  YOUR OWN RESPONSIBILITY.

  By continuing, you confirm you have authorization to scan
  the target(s) you provide.
==============================================================
"""


def print_intro():
    print(BANNER)
    print(WARNING)
