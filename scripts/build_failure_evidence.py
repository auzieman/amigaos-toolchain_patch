"""Retain bounded apt acquisition evidence even when a long summary hides it."""
import collections,re

def archive_failures(path):
    found=collections.deque(maxlen=8)
    if not path.exists():return []
    with path.open(errors='replace') as stream:
        for line in stream:
            # sbuild may subsequently install dose to explain an original
            # dependency conflict. A network failure there is secondary.
            if line.startswith('E: Package installation failed'):
                break
            if re.search(r'^E: Failed to fetch |^Err:\d+ https?://|TooManyRequests|No healthy backends',line):
                found.append(line.strip()[:500])
    return list(found)
