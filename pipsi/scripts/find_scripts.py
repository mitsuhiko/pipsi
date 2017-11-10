import os
import sys
import pkg_resources
pkg = sys.argv[1]
prefix = sys.argv[2]
dist = pkg_resources.get_distribution(pkg)
if dist.has_metadata('RECORD'):
    for line in dist.get_metadata_lines('RECORD'):
        print(os.path.join(dist.location, line.split(',')[0]))
elif dist.has_metadata('installed-files.txt'):
    for line in dist.get_metadata_lines('installed-files.txt'):
        print(os.path.join(dist.egg_info, line.split(',')[0]))
elif dist.has_metadata('entry_points.txt'):
    try:
        from ConfigParser import SafeConfigParser
        from StringIO import StringIO
    except ImportError:
        from configparser import SafeConfigParser
        from io import StringIO
    parser = SafeConfigParser()
    parser.readfp(StringIO(
        '\n'.join(dist.get_metadata_lines('entry_points.txt'))))
    if parser.has_section('console_scripts'):
        for name, _ in parser.items('console_scripts'):
            print(os.path.join(prefix, name))
