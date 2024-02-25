#!/usr/bin/env python3

import argparse
import json
import urllib.request

try:
    import config

    config.serial
    config.auth_jwt
except:
    print("config.py is invalid: see comments in config.py.in.")
    raise


BASE_URL = "https://cloud.alphaess.com/api/base/"


def request(url_suffix):
    url = BASE_URL + url_suffix
    req = urllib.request.Request(
        url,
        headers={
            "Authority": "cloud.alphaess.com",
            "Authorization": config.auth_jwt,
            "Accept": "application/json",
            "Referer": "https://cloud.alphaess.com/index/index",
        },
    )
    return urllib.request.urlopen(req)


def direction(num, inward, nil, outward):
    if int(num) == 0:
        return nil
    elif num < 0:
        return inward
    else:
        return outward


def get_last_power(opts):
    resp = request(f"energyStorage/getLastPowerData?sysSn={config.serial}&stationId=")
    js = json.load(resp)
    data = js["data"]

    batstate = direction(data["pbat"], "charging", "", "discharging")
    gridstate = direction(data["pgrid"], "export", "", "import")

    if opts.format == "json":
        print(json.dumps(js))
    elif opts.format == "text":
        print(
            f"""
Solar:   {data['ppv']:g}W
Battery: {data['pbat']:g}W {batstate}
Load:    {data['pload']:g}W
Grid:    {data['pgrid']:g}W {gridstate}

Battery charge: {data['soc']:g}%
"""
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", "-f", choices=["json", "text"], default="json")
    subp = ap.add_subparsers(required=True, dest="func")

    cp = subp.add_parser(
        "get-last-power",
        help="Get latest instantaneous power data from the getLastPowerData endpoint.",
    )
    cp.set_defaults(func=get_last_power)

    opts = ap.parse_args()
    opts.func(opts)
