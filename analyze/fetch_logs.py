#!/usr/bin/env python3
# vim:se sts=4 sw=4 et fenc=utf-8 ft=python:
import os
import re
import sys
import urllib.parse
from urllib.parse import parse_qs, urlparse

import requests

push_url = sys.argv[1]
output_dir = sys.argv[2]

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
}


def url(path, treeherder=True):
    base = (
        "https://treeherder.mozilla.org/api/"
        if treeherder
        else "https://firefox-ci-tc.services.mozilla.com/api/queue/v1/"
    )
    return base + path


def get(url):
    return requests.get(url, headers=headers)


def fetch_log(url, filename):
    output_path = os.path.join(output_dir, filename)
    print(output_path)

    result = requests.get(url)
    with open(output_path, "wb") as fh:
        fh.write(result.content)


path_re = re.compile(r".*/(?P<basename>.*)\.(?P<ext>.*?)$")

query = parse_qs(urlparse(push_url.replace("/#/", "/")).query)

(commit_id,) = query["revision"]

push_url = "project/try/push/?revision=%s" % commit_id
push_data = get(url(push_url)).json()

push_id = push_data["results"][0]["id"]

jobs_url = "project/try/jobs/?push_id=%s&count=2000&return_type=list" % push_id
job_data = get(url(jobs_url)).json()

jobs = []
for result in job_data["results"]:
    job = {}
    for i, key in enumerate(job_data["job_property_names"]):
        job[key] = result[i]

    if (
        job["state"] == "completed"
        and job["result"] == "testfailed"
        and job["job_group_symbol"] == "M-fis"
        and "linux" in job["platform"]
    ):
        jobs.append(job)

raw_logs = []
for job in jobs:
    detail_url = "task/%s/runs/%s/artifacts" % (job["task_id"], job["retry_id"])

    safe_guid = re.sub(r"/.*", "", job["job_guid"])

    for artifact in get(url(detail_url, False)).json()["artifacts"]:
        if artifact["name"].endswith("_raw.log"):
            artifact_url = url(detail_url + "/" + artifact["name"], False)
            m = path_re.match(urlparse(artifact_url).path)

            filename = "%s_%s-%s_%s.%s" % (
                m["basename"],
                job["platform"],
                job["platform_option"],
                safe_guid,
                m["ext"],
            )

            fetch_log(artifact_url, filename)
