#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# Example for output from agent (contents of /proc/mdstat):
# ---------------------------------------------------------
#    Personalities : [raid1]
#    md1 : active raid1 dm-19[0] dm-9[1]
#          20971456 blocks [2/2] [UU]
#          20971456 blocks super 1.2 [2/2] [UU]
#
#    md2 : active (auto-read-only) raid1 sda6[0] sdb6[1]
#          4200952 blocks super 1.0 [2/2] [UU]
#          bitmap: 0/9 pages [0KB], 256KB chunk
#
#          unused devices: <none>
# ---------------------------------------------------------

# Another example (with RAID 5 and spare disk (md2) and a RAID-0
# device (md3)
# ---------------------------------------------------------
# Personalities : [raid1] [raid6] [raid5] [raid4]
# md2 : active raid5 sde1[3](S) sdd1[0] sdg1[2] sdf1[1]
#       976767872 blocks level 5, 64k chunk, algorithm 2 [3/3] [UUU]
#
# md0 : active raid1 sdb1[1] sda1[0]
#       104320 blocks [2/2] [UU]
#
# md1 : active raid1 sdb3[1] sda3[0]
#       486239232 blocks [2/2] [UU]
#
# md4 : active (auto-read-only) raid1 sda6[0] sdb6[1]
#       4200952 blocks super 1.0 [2/2] [UU]
#         resync=PENDING
#       bitmap: 9/9 pages [36KB], 256KB chunk
#
# md3 : active raid0 sdb3[0] sda3[1]
#       16386048 blocks 64k chunks
#
# unused devices: <none>
# ---------------------------------------------------------

# Another example with RAID1 replacement gone wrong
# ---------------------------------------------------------
# Personalities : [raid1]
# md0 : active raid1 sdc3[3] sda3[2](F) sdb3[1]
#       48837528 blocks super 1.0 [2/2] [UU]
#
# md1 : active raid1 sdc4[3] sda4[2](F) sdb4[1]
#       193277940 blocks super 1.0 [2/2] [UU]
#
# unused devices: <none>
# ----------------------------------------------------------

# Another example with RAID5 being recovered
# ---------------------------------------------------------
# Personalities : [raid1] [raid6] [raid5] [raid4]
# md1 : active raid1 sdd1[1] sdc1[0]
#       10484668 blocks super 1.1 [2/2] [UU]
#       bitmap: 1/1 pages [4KB], 65536KB chunk
#
# md127 : active raid5 sda3[0] sdb3[1] sdd3[4] sdc3[2]
#       11686055424 blocks super 1.2 level 5, 512k chunk, algorithm 2 [4/3] [UUU_]
#       [======>..............]  recovery = 31.8% (1241578496/3895351808) finish=746.8min speed=59224K/sec
#
# md0 : active raid1 sdb1[1] sda1[0]
#       10485688 blocks super 1.0 [2/2] [UU]
#       bitmap: 0/1 pages [0KB], 65536KB chunk
#
# unused devices: <none>
# ----------------------------------------------------------

# Example of RAID5 being checked
# Personalities : [raid1] [raid6] [raid5] [raid4]
# md125 : active raid1 sdb2[0] sdd2[1]
#      182751552 blocks super 1.2 [2/2] [UU]
#      bitmap: 1/2 pages [4KB], 65536KB chunk
#
# md126 : active raid5 sdf1[5] sde1[2] sdc1[1] sdg1[3] sda1[0]
#      31255568384 blocks super 1.2 level 5, 512k chunk, algorithm 2 [5/5] [UUUUU]
#      [===============>.....]  check = 76.0% (5938607824/7813892096) finish=255.8min speed=122145K/sec
#      bitmap: 0/59 pages [0KB], 65536KB chunk
#
# md127 : active raid1 sdd1[1] sdb1[0]
#      67107840 blocks super 1.2 [2/2] [UU]
#      bitmap: 1/1 pages [4KB], 65536KB chunk

# And now for something completely different:
# ---------------------------------------------------------
# Personalities : [raid1] [raid10]
# md1 : active raid10 sdd6[3] sdb6[1] sda6[0]
#       1463055360 blocks 64K chunks 2 near-copies [4/3] [UU_U]
#
# md0 : active raid1 sdd1[3] sdb1[1] sda1[0]
#       104320 blocks [4/3] [UU_U]
#
# unused devices: <none>
# ---------------------------------------------------------

# Example of a raid with a single disk
# ---------------------------------------------------------
# md1 : active raid1 nvme4n1p2[1] nvme5n1p2[0] nvme2n1p2[2] nvme1n1p2[3] nvme3n1p2[5] nvme0n1p2[4]
#       25977152 blocks super 1.2 [6/6] [UUUUUU]
#
# md0 : active raid1 nvme6n1[0]
#       7501333824 blocks super 1.2 [1/1] [U]
#       bitmap: 4/56 pages [16KB], 65536KB chunk
#
# unused devices: <none>
# ---------------------------------------------------------


# mypy: disable-error-code="var-annotated"

from cmk.agent_based.legacy.v0_unstable import LegacyCheckDefinition

check_info = {}


def parse_md(string_table):
    parsed = {}
    instance = {}
    for line in (l for l in string_table if l):
        if len(line) >= 5 and line[0].startswith("md") and line[1] == ":":
            if line[3].startswith("(") and line[3].endswith(")"):
                raid_state = line[2] + line[3]
                raid_name = line[4]
                disk_list = line[5:]
            else:
                raid_state = line[2]
                raid_name = line[3]
                disk_list = line[4:]

            spare_disks = len([x for x in disk_list if x.endswith("(S)")])
            failed_disks = len([x for x in disk_list if x.endswith("(F)")])

            instance = parsed.setdefault(
                line[0],
                {
                    "raid_name": raid_name,
                    "raid_state": raid_state,
                    "spare_disks": spare_disks,
                    "failed_disks": failed_disks,
                    "active_disks": len(disk_list) - spare_disks - failed_disks,
                },
            )

        elif instance:
            if line[0].startswith("resync="):
                k, v = line[0].split("=")
                instance["%s_state" % k] = v
                continue

            if len(line) >= 2 and line[0].startswith("[") and line[0].endswith("]"):
                for idx, e in enumerate(line[1:]):
                    if e.startswith("finish=") or e.startswith("speed="):
                        k, v = e.split("=")
                        instance[k] = v
                    elif e in ["recovery", "resync", "check"]:
                        instance["%s_values" % e] = line[idx + 3]
                continue

            if line[-1].startswith("[") and line[-1].endswith("]"):
                instance["working_disks"] = line[-1][1:-1]

            if len(line) >= 2 and line[-2].startswith("[") and line[-2].endswith("]"):
                for key, value in zip(["num_disks", "expected_disks"], line[-2][1:-1].split("/")):
                    try:
                        instance[key] = int(value)
                    except ValueError:
                        pass
    return parsed


def inventory_md(parsed):
    for device, attrs in parsed.items():
        if attrs["raid_name"] != "raid0":
            yield device, None


def check_md(item, _no_params, parsed):
    data = parsed.get(item)
    if data is None:
        return

    raid_state = data["raid_state"]
    infotext = "Status: %s" % raid_state
    if raid_state in {"active", "active(auto-read-only)"}:
        state = 0
    else:
        infotext += " (should be 'active')"
        state = 2
    yield state, infotext

    spare_disks = data["spare_disks"]
    failed_disks = data["failed_disks"]
    active_disks = data["active_disks"]
    yield 0, f"Spare: {spare_disks}, Failed: {failed_disks}, Active: {active_disks}"

    num_disks = data.get("num_disks")
    expected_disks = data.get("expected_disks")
    working_disks = data.get("working_disks")
    if num_disks is not None and expected_disks is not None and working_disks is not None:
        infotext = f"Status: {num_disks}/{expected_disks}, {working_disks}"
        if num_disks == expected_disks and active_disks == working_disks.count("U"):
            yield 0, infotext
        else:
            yield 2, infotext

    header = "[Resync/Recovery]"
    infotexts = []
    if "resync_state" in data:
        header = "[Resync]"
        infotexts.append("Status: %s" % data["resync_state"])

    if "resync_values" in data:
        header = "[Resync]"
        infotexts.append(data["resync_values"])

    if "recovery_values" in data:
        header = "[Recovery]"
        infotexts.append(data["recovery_values"])

    if "finish" in data:
        infotexts.append("Finish: %s" % data["finish"])

    if "speed" in data:
        infotexts.append("Speed: %s" % data["speed"])

    if "check_values" in data:
        header = "[Check]"
        infotexts.append("Status: %s" % data["check_values"])
        yield 0, "{} {}".format(header, ", ".join(infotexts))

    elif infotexts:
        yield 1, "{} {}".format(header, ", ".join(infotexts))


check_info["md"] = LegacyCheckDefinition(
    name="md",
    parse_function=parse_md,
    service_name="MD Softraid %s",
    discovery_function=inventory_md,
    check_function=check_md,
    check_ruleset_name="raid",
)
