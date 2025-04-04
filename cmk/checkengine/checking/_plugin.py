#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Protocol

from cmk.utils.hostaddress import HostAddress, HostName
from cmk.utils.parameters import merge_parameters
from cmk.utils.servicename import Item, ServiceName

from cmk.checkengine.parameters import TimespecificParameters
from cmk.checkengine.plugins import CheckPluginName, ConfiguredService, ServiceID

__all__ = [
    "ServiceConfigurer",
    "merge_enforced_services",
    "AutocheckEntryProtocol",
]

type _DiscoveredLabels = Mapping[str, str]

type _Labels = Mapping[str, str]


class AutocheckEntryProtocol(Protocol):
    @property
    def check_plugin_name(self) -> CheckPluginName: ...

    @property
    def item(self) -> Item: ...

    @property
    def parameters(self) -> Mapping[str, object]: ...

    @property
    def service_labels(self) -> _DiscoveredLabels: ...


class ServiceConfigurer:
    def __init__(
        self,
        compute_check_parameters: Callable[
            [HostName, CheckPluginName, Item, _Labels, Mapping[str, object]],
            TimespecificParameters,
        ],
        get_service_description: Callable[[HostName, CheckPluginName, Item], ServiceName],
        get_effective_host: Callable[[HostName, ServiceName, _Labels], HostName],
        get_service_labels: Callable[[HostName, ServiceName, _DiscoveredLabels], _Labels],
    ) -> None:
        self._compute_check_parameters = compute_check_parameters
        self._get_service_description = get_service_description
        self._get_effective_host = get_effective_host
        self._get_service_labels = get_service_labels

    def _configure_autocheck(
        self,
        hostname: HostName,
        autocheck_entry: AutocheckEntryProtocol,
    ) -> ConfiguredService:
        # TODO: only call this function when we know "effective host" == hostname and simplify accordingly
        service_name = self._get_service_description(
            hostname, autocheck_entry.check_plugin_name, autocheck_entry.item
        )
        labels = self._get_service_labels(hostname, service_name, autocheck_entry.service_labels)

        return ConfiguredService(
            check_plugin_name=autocheck_entry.check_plugin_name,
            item=autocheck_entry.item,
            description=service_name,
            parameters=self._compute_check_parameters(
                self._get_effective_host(hostname, service_name, labels),
                autocheck_entry.check_plugin_name,
                autocheck_entry.item,
                labels,
                autocheck_entry.parameters,
            ),
            discovered_parameters=autocheck_entry.parameters,
            labels=labels,
            discovered_labels=autocheck_entry.service_labels,
            is_enforced=False,
        )

    def configure_autochecks(
        self,
        hostname: HostName,
        autocheck_entries: Iterable[AutocheckEntryProtocol],
    ) -> Sequence[ConfiguredService]:
        return [self._configure_autocheck(hostname, entry) for entry in autocheck_entries]


def merge_enforced_services(
    services: Mapping[HostAddress, Mapping[ServiceID, tuple[object, ConfiguredService]]],
    appears_on_cluster: Callable[[HostAddress, ServiceName, _DiscoveredLabels], bool],
    labels_of_service: Callable[[ServiceName, _DiscoveredLabels], _Labels],
) -> Iterable[ConfiguredService]:
    """Aggregate services from multiple nodes"""
    entries_by_id: dict[ServiceID, list[ConfiguredService]] = defaultdict(list)
    for node, node_services in services.items():
        for sid, (_, service) in node_services.items():
            if appears_on_cluster(node, service.description, service.discovered_labels):
                entries_by_id[sid].append(service)

    return [
        ConfiguredService(
            check_plugin_name=sid[0],
            item=sid[1],
            description=entries[0].description,
            parameters=TimespecificParameters(
                [ps for entry in entries for ps in entry.parameters.entries]
            ),
            # For consistency we also merge `discovered_{parameters,labels}`.
            # At the time of writing, they are always empty for enforced services.
            discovered_parameters=merge_parameters([e.discovered_parameters for e in entries], {}),
            discovered_labels=(
                discovered_labels := merge_parameters([e.discovered_labels for e in entries], {})
            ),
            labels=labels_of_service(entries[0].description, discovered_labels),
            is_enforced=True,
        )
        for sid, entries in entries_by_id.items()
    ]
