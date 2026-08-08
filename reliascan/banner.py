"""ASCII banner + legal/ethical warning shown on every run."""

BANNER = r"""


 ____  _____ _     ___    _    ____   ____    _    _   _
|  _ \| ____| |   |_ _|  / \  / ___| / ___|  / \  | \ | |
| |_) |  _| | |    | |  / _ \ \___ \| |     / _ \ |  \| |
|  _ <| |___| |___ | | / ___ \ ___) | |___ / ___ \| |\  |
|_| \_\_____|_____|___/_/   \_\____/ \____/_/   \_\_| \_|

        R E L I A S C A N   //  consistency-checked scanner
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
