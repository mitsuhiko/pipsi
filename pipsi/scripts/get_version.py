import sys, pkg_resources
pkg = sys.argv[1]
dist = pkg_resources.get_distribution(pkg)
print(dist.version)
