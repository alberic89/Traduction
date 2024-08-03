# -*- coding: UTF-8 -*-

"""
Auto correct translation according to the rules etablished by the French
BFW traduction team.
It include unbreakable spaces, hyphen (…), apostrophe, extra spaces (option).

inspired from other sieves
@author: alberic89 <alberic89@gmx.com>
@license: GPLv3"""

import re

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

    p.add_param(
        "correct",
        bool,
        defval=False,
        desc=_(
            "@info sieve parameter description",
            "Enforces correction even if another parameter disables it",
        ),
    )

    p.add_param(
        "extra_spaces",
        bool,
        defval=False,
        desc=_(
            "@info sieve parameter description",
            "Replace all extra spaces by punctuation space rather than correct typo",
        ),
    )

    p.add_param(
        "ellipses",
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
    """Correct according to BFW french standard"""

    # apostrophe typographique "’" : \u2019
    # espace insécable " " : \u00A0
    # espace insécable fine " " : \u202F

    def __init__(self, params):
        self.nmatch = 0
        self.p = params
        self.space_start = re.compile(r"^ +")
        self.space_end = re.compile(r" +$")
        self.regex_replacements = (
            (re.compile("=('[^']*)\\\\'([^']*')"), "=\\1\u2019\\2"),
            (re.compile("\b'(?!=[^']*'[^']*')"), "\u2019"),
            (re.compile("(\s+)(?=%(?=$| |\.|,))"), "\u00A0"),  # %
            (re.compile("(\s+)(?=:|»)"), "\u00A0"),  # : »
            (re.compile("(?<=«)(\s+)"), "\u00A0"),  # «
            (re.compile("(\s+)(?=;|!|\?)"), "\u202F"),  # ; ! ?
            # ~ (re.compile("=’([^’]+)’"), r"='\1'"),
        )
        self.filters = (
            SpecialFilter(
                "extra_spaces",
                params.extra_spaces,
                self.replace_extra_spaces,
            ),
            SpecialFilter(
                "ellipses",
                params.ellipses,
                self.replace_ellipses,
            ),
        )  # in future, add other specials filters
        self.used_filters = [_ for _ in self.filters if _.value]

    def process(self, msg, cat):
        oldcount = msg.modcount

        for i in range(len(msg.msgstr)):
            if self.used_filters:
                for _ in self.used_filters:
                    if _.value:
                        msg.msgstr[i] = _.action(msg.msgstr[i])
                if self.p.correct:
                    msg.msgstr[i] = self.correctTypo(msg.msgstr[i])
            else:
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
        replacements = (
            # ~ ("\\'", "’"),  # escaped '
            # ~ ("'", "’"),
        )

        for _ in replacements:
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

    def replace_ellipses(self, text):
        """Replace all three point (...) by a Unicode ellipsis (…)"""
        # ellipsis "…" : \u2026
        return text.replace("...", "\u2026")
