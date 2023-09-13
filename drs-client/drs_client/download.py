import subprocess


def download_file(drs_url, drs_id):
    """Download file data and metadata from DRS server.

    Currently, just calls through to our modified version of the GA4GH
    client.
    """
    command = [
        "drs", "get", "-d", drs_url, drs_id
    ]
    subprocess.run(command, check=True)
