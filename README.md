# Minecraft Package Manager

## Purpose

The *Minecaft Package Manager* (hence forth just `mpm`) is a tool inspired by common package managers found in
unix systems that brings some of thier features to the minecraft world.

Managing modpacks has always been troublesome for us, mostly because the minecraft modding community is organised
around a few website where modders publish their work without a standardised format. This tool is an attempt to
fill this gap and should enable seamless management and update of mods inside a modpack.

The `mpm` tool has a cli interface much like other package managers, the main difference is that mods are
installed in modpack projects and the index of the installed mod packages is kept separately for each modpack.
Further informations about `mpm` internals will be found in the developers wiki.

## Project Status

The project is still in early development stage, the architecture and features supported are likely to be changed.
Some of the features that we would like to support are:

- dependency handling
- mod update/install and version handling
- per modpack/instance management of mods
- GPG signatures for safer mod distribution
- integrated donations support with paypal/patreon links and ad.fly like urls.

## License

GPL v3, see license file distributed.


qwattash