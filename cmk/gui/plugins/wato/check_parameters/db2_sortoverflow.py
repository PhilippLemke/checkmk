#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Percentage,
    TextAscii,
    Tuple,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)


def _item_spec_db2_sortoverflow():
    return TextAscii(title=_("Instance"),
                     help=_("DB2 instance followed by database name, e.g db2taddm:CMDBS1"))


def _parameter_valuespec_db2_sortoverflow():
    return Dictionary(
        help=_("This rule allows you to set percentual limits for sort overflows."),
        elements=[
            (
                "levels_perc",
                Tuple(
                    title=_("Overflows"),
                    elements=[
                        Percentage(title=_("Warning at"), unit=_("%"), default_value=2.0),
                        Percentage(title=_("Critical at"), unit=_("%"), default_value=4.0),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="db2_sortoverflow",
        group=RulespecGroupCheckParametersApplications,
        item_spec=_item_spec_db2_sortoverflow,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_db2_sortoverflow,
        title=lambda: _("DB2 Sort Overflow"),
    ))
