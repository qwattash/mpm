# -*- coding: utf-8 -*-

import argparse
import six

parser = argparse.ArgumentParser(description="Minecraft Package Manager")

sub = parser.add_subparsers(help="command help")

# package commands
sync_parser = sub.add_parser("sync",
                             description="Synchronize local mod archive.",
                             help="sync --help")
show_parser = sub.add_parser("show",
                             description="Show mod informations.",
                             help="show --help")
search_parser = sub.add_parser("search",
                               description="Search mod archive.",
                               help="search --help")
update_parser = sub.add_parser("update",
                               description="Update mods.",
                               help="update --help")
install_parser = sub.add_parser("install",
                                description="Install mods.",
                                help="install --help")
remove_parser = sub.add_parser("remove",
                               description="Remove mods.",
                               help="remove --help")

# repo commands
repo_add_parser = sub.add_parser("addrepo",
                                 description="Add mod repository.",
                                 help="addrepo --help")
repo_del_parser = sub.add_parser("rmrepo",
                                 description="Remove mod repository.",
                                 help="rmrepo --help")
repo_show_parser = sub.add_parser("lsrepo",
                                  description="Show mod repository informations.",
                                  help="lsrepo --help")



if __name__ == "__main__":
    cmd = parser.parse_args()
    six.print_("Done")
