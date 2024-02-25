#!/usr/bin/env python3

import argparse
import datetime
import json
import sys
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


def get_daily_power_histogram(opts, output=sys.stdout):
    resp = request(f"power/staticsByDay?date={opts.date}&userId=&sysSn={config.serial}")
    js = json.load(resp)

    _output_histogram(opts, js, output=output)


def _output_histogram(opts, js, output=sys.stdout):
    data = js["data"]

    def _table(sep, output):
        def W(kw):
            return "%g" % (kw * 1000)

        print(
            sep.join(
                ["Time", "Battery %", "Solar W", "Export W", "Import W", "Home Usage W"]
            ),
            file=output,
        )
        for i, time in enumerate(data["time"]):
            print(
                sep.join(
                    [
                        time,
                        "%g%%" % data["cbat"][i],
                        W(data["ppv"][i]),
                        W(data["feedIn"][i]),
                        W(data["gridCharge"][i]),
                        W(data["homePower"][i]),
                    ]
                ),
                file=output,
            )

    if opts.format == "json":
        print(json.dumps(js), file=output)
    elif opts.format == "text":
        print(
            f"""
Peak instantaneous solar:  {data['maxPpv']:g}kW
Peak instantaneous export: {data['maxFeedIn']:g}kW
Peak instantaneous import: {data['maxGridCharge']:g}kW
Peak instantaneous usage:  {data['maxUsePower']:g}kW

Total solar:   {data['epvtoday']:g}kWh
Total export:  {data['efeedIn']:g}kWh
Total import:  {data['einput']:g}kWh
Total usage:   {data['eload']:g}kWh
""",
            file=output,
        )

        _table("\t", output)
    elif opts.format == "csv":
        _table(",", output)


def format_daily_power_histogram(opts):
    js = json.load(opts.file)
    _output_histogram(opts, js)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", "-f", choices=["json", "text", "csv"], default="json")
    subp = ap.add_subparsers(required=True, dest="func")

    cp = subp.add_parser(
        "get-last-power",
        help="Get latest instantaneous power data from the getLastPowerData endpoint.",
    )
    cp.set_defaults(func=get_last_power)

    cp = subp.add_parser(
        "get-daily-power-histogram",
        help="Get a daily power histogram from the staticsByDay endpoint.",
    )
    cp.add_argument(
        "date",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
        help="Date, in the format 2024-02-25.",
    )
    cp.set_defaults(func=get_daily_power_histogram)

    cp = subp.add_parser(
        "format-daily-power-histogram",
        help="Take a JSON-format output file from `get-daily-power-histogram` and turn it into another format",
    )
    cp.add_argument("file", type=argparse.FileType("r"))
    cp.set_defaults(func=format_daily_power_histogram)

    opts = ap.parse_args()
    opts.func(opts)
