"""Match primary apt download failures to exact frozen native archive requests."""
import re
from urllib.parse import unquote
from debian.deb822 import Packages
from build_failure_evidence import archive_failures

def requests_for_failure(log, native_index, repositories):
    # Never retry compiler, packaging or coinstallation failures as downloads.
    with log.open(errors='replace') as stream:
        stages = [line.partition(':')[2].strip() for line in stream if line.startswith('Fail-Stage:')]
    if not stages or stages[-1] != 'install-deps':
        return []
    urls = []
    for line in archive_failures(log):
        match = re.match(r'^E: Failed to fetch (https?://\S+)', line)
        if match:
            urls.append(unquote(match[1].split('?', 1)[0]))
    paths = set()
    for url in urls:
        for repo in repositories:
            prefix = repo['url'].rstrip('/') + '/'
            if url.startswith(prefix):
                paths.add(url[len(prefix):])
    if not paths:
        return []
    requests = set()
    with native_index.open() as stream:
        for entry in Packages.iter_paragraphs(stream):
            if entry.get('Architecture') in ['amd64', 'all'] and entry.get('Filename') in paths:
                requests.add(entry['Package'] + '=' + entry['Version'])
    return sorted(requests)
