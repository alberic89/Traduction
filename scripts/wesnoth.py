# -*- coding: UTF-8 -*-

"""
Auto correct translation according to the rules etablished by the French
BFW traduction team.
It include unbreakable spaces, hyphen (…), apostrophe, extra spaces (option).

inspired from other sieves
@author: alberic89 <alberic89@gmx.com>
@license: GPLv3"""

import re

from typing import List
from pology import _, n_
from pology.report import report
from pology.sieve import add_param_filter


def setup_sieve(p):
    p.set_desc(
        _("@info sieve description", "Correct message according to BFW french standard")
    )

    p.add_param(
        "quiet",
        bool,
        defval=False,
        desc=_(
            "@info sieve parameter description",
            "Do not show summary (for script usage)",
        ),
    )

    # ~ p.add_param(
        # ~ "level",
        # ~ list,
        # ~ defval=[],
        # ~ desc=_(
            # ~ "@info sieve parameter description",
            # ~ "Set level of correction (1, 2 and 3). You can use mutliple levels, for example level:12",
        # ~ ),
    # ~ )

    p.add_param(
        "extra_spaces",
        list,
        defval=[],
        desc=_(
            "@info sieve parameter description",
            "Replace all extra spaces by punctuation space on the message of the numero given. You can specify multiple message with comma-separated list.",
        ),
    )

    p.add_param(
        "ellipses3points",
        bool,
        defval=False,
        desc=_(
            "@info sieve parameter description",
            "Replace all Unicode ellipsis (…) by three point (...)",
        ),
    )

    p.add_param(
        "ellipsesUnicode",
        bool,
        defval=False,
        desc=_(
            "@info sieve parameter description",
            "Replace all three point (...) by a Unicode ellipsis (…)",
        ),
    )


class SpecialFilter:
    """A special filter who disable normal correction work"""

    def __init__(self, name, value, action):
        """action should be a function with the text in argument"""
        self.name = name
        self.value = value
        self.action = action

    def __eq__(self, y):
        return y == self.value

    def __repr__(self):
        return f"{self.name} : {self.value} : {self.action}"


class Sieve(object):
    """Correct traduction according to BFW french standard"""

    # apostrophe typographique "’" : \u2019
    # espace insécable " " : \u00A0
    # espace insécable fine " " : \u202F

    def __init__(self, params):
        self.nmatch = 0
        self.p = params
        # ~ print(params.extra_spaces)
        nums = [0]
        for _ in params.extra_spaces:
            if _.isdigit():
                nums.append(nums.pop()*10+int(_))
            else:
                nums.append(0)
        if nums[-1] == 0:
            nums.pop()
        # ~ print(nums)
        self.nums = nums
        self.space_start = re.compile(r"^ +")
        self.space_end = re.compile(r" +$")
        self.regex_replacements = (
            (re.compile(r"(?<==')([^\\']*(\b\\'\b))*([^\\']*)(?=')"), lambda m: _replace_group(m,2,"\u2019")),
            (re.compile(r"\b(')(?=$|\s?\b|\s[:;!?]|[.,])"), "\u2019"), # '
            (re.compile(r"(?<=\d)(\s+)(?=%(?=$| |\.|,))"), "\u00A0"),  # %
            (re.compile(r"\b(\s+)(?=:|»)"), "\u00A0"),  # : »
            (re.compile(r"(?<=«)(\s+)\b"), "\u00A0"),  # «
            (re.compile(r"\b(\s+)(?=;|!|\?)"), "\u202F"),  # ; ! ?
            (re.compile(r"\b(  )\b"), " "), # double space
            # \b ([\.,]) remove space before point and virgule
        )
        self.replacements = (
            # ~ ("\\'", "’"),  # escaped '
            # ~ ("'", "’"),
        )
        self.filters = (
            SpecialFilter(
                "extra_spaces",
                params.extra_spaces,
                self.replace_extra_spaces,
            ),
            SpecialFilter(
                "ellipses3points",
                params.ellipses3points,
                lambda text: text.replace("…", "..."),
            ),
            SpecialFilter(
                "ellipsesUnicode",
                params.ellipsesUnicode,
                lambda text: text.replace("...", "…"),
            ),
        )  # in future, add other specials filters
        self.used_filters = [_ for _ in self.filters if _.value]

    def process(self, msg, cat):
        oldcount = msg.modcount
        # ~ if msg.refentry in self.nums:
            # ~ print(f"#{msg.refentry}:{msg.msgstr}")
        # ~ if len(msg.msgstr)!= 1:
            # ~ print(msg.msgstr)
        for i in range(len(msg.msgstr)):
            if self.used_filters:
                for _ in self.used_filters:
                    if _.value and msg.refentry in self.nums:
                        msg.msgstr[i] = _.action(msg.msgstr[i])
                # ~ if self.p.correct:
                    # ~ msg.msgstr[i] = self.correctTypo(msg.msgstr[i])
            # ~ else:
            msg.msgstr[i] = self.correctTypo(msg.msgstr[i])

        if oldcount < msg.modcount:
            self.nmatch += 1

    def finalize(self):
        if self.nmatch > 0 and not self.p.quiet:
            report(
                n_(
                    "@info",
                    "Typo updated in %(num)d message.",
                    "Typo updated in %(num)d messages.",
                    num=self.nmatch,
                )
            )


    def correctTypo(self, text):
        """Set correct typo"""

        for _ in self.replacements:
            text = text.replace(_[0], _[1])
        for _ in self.regex_replacements:
            text = _[0].sub(_[1], text)

        return text

    def replace_extra_spaces(self, text):
        """Replace space at start and end by punctuation space"""
        # punctuation space " " : \u2008
        match_start = re.search(self.space_start, text)
        match_end = re.search(self.space_end, text)

        if match_start:
            text = re.sub(self.space_start, "\u2008" * len(match_start[0]), text)

        if match_end:
            text = re.sub(self.space_end, "\u2008" * len(match_end[0]), text)

        return text

    # ~ def replace_ellipses(self, text):
    # ~ """Replace all three point (...) by a Unicode ellipsis (…)"""
    # ~ # ellipsis "…" : \u2026
    # ~ return text.replace("...", "\u2026")

def _replace_group(match,group,replacement):
    if (groupn:=match.group(group)):
        return match.group().replace(groupn, replacement)
    else:
        return match.group()
