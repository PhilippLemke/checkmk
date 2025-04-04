#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.plugins.hp_msa.server_side_calls.special_agent import special_agent_hp_msa
from cmk.server_side_calls.v1 import HostConfig, IPv4Config, Secret, SpecialAgentCommand


def test_command_creation() -> None:
    assert list(
        special_agent_hp_msa(
            {
                "username": "user",
                "password": Secret(1),
            },
            HostConfig(
                name="hostname",
                ipv4_config=IPv4Config(address="1.2.3.4"),
            ),
        )
    ) == [
        SpecialAgentCommand(
            command_arguments=[
                "-u",
                "user",
                "-p",
                Secret(id=1, format="%s", pass_safely=False),
                "1.2.3.4",
            ]
        )
    ]
