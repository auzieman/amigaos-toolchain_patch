#!/usr/bin/env python3
"""Replica-local: express a project series.json as source_patch + extra_patches (git apply; may touch debian/)."""
import json, sys
spec, project, series = sys.argv[1:4]
s = json.load(open(spec)); r = json.load(open(project + '/' + series)); s.pop('quilt_patch_series', None)
first, *rest = r['patches']
s['source_patch'] = {'path': first['path'], 'sha256': first['sha256'], 'version': r['version'], 'preserve_debian_version': True,
                     'changelog_entry': 'Apply ' + series + ' (' + str(len(r['patches'])) + ' patches).', 'extra_patches': rest}
json.dump(s, open(spec, 'w'), indent=2)
