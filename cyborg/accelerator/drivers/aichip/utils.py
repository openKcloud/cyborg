# Copyright 2025 Electronics and Telecommunications Research Institute.
#
# This software was supported by the Institute of Information & Communications
# Technology Planning & Evaluation(IITP) grant funded by the Korea government
# (MSIT) (No.RS-2025-02263869, Development of AI Semiconductor Cloud Platform
# Establishment and Optimization Technology)
#
# Modifications Copyright (C) 2021 ZTE Corporation
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Utils for AICHIP driver.
"""
from oslo_concurrency import processutils
from oslo_log import log as logging

import re

import cyborg.conf
import cyborg.privsep

LOG = logging.getLogger(__name__)

AICHIP_FLAGS = ["Processing accelerators"]
AICHIP_INFO_PATTERN = re.compile(
    r"(?P<devices>[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:"
    r"[0-9a-fA-F]{2}\.[0-9a-fA-F]) "
    r"(?P<controller>.*) [\[].*]: (?P<model>.*) .*"
    r"[\[](?P<vendor_id>[0-9a-fA-F]"
    r"{4}):(?P<product_id>[0-9a-fA-F]{4})].*"
)

VENDOR_MAPS = {"1ed2": "furiosa", "1eff": "rebellions"}


@cyborg.privsep.sys_admin_pctxt.entrypoint
def lspci_privileged():
    cmd = ["lspci", "-nn", "-D"]
    return processutils.execute(*cmd)


def get_pci_devices(pci_flags, vendor_id=None):
    device_for_vendor_out = []
    all_device_out = []
    lspci_out = lspci_privileged()[0].split("\n")
    for pci in lspci_out:
        if any(x in pci for x in pci_flags):
            all_device_out.append(pci)
            if vendor_id and vendor_id in pci:
                device_for_vendor_out.append(pci)
    return device_for_vendor_out if vendor_id else all_device_out


def discover_vendors():
    vendors = set()
    aichips = get_pci_devices(AICHIP_FLAGS)
    for aichip in aichips:
        m = AICHIP_INFO_PATTERN.match(aichip)
        if m:
            vendor_id = m.groupdict().get("vendor_id")
            vendors.add(vendor_id)
    return vendors
