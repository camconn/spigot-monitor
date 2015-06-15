
# Spigot Monitor

A Python 3 Spigot wrapper.

The goal of this project is to create a free (as in freedom) wrapper around
[Spigot](http://spigotmc.org/).

Spigot monitor is built with the [bottle.py](http://github.com/bottlepy/bottle)
microframework.

## Features
**Implemented**
- Lightweight Web console UI
- Do anything you could with console access - (It's only a console at this point though)

**Planned**
- Player list
- Ability to modify server configuration
- API for sending commands and monitoring game state

## Deployment

    # install pip dependencies
    pip3 install psutil bottle

    # fetch source
    git clone https://github.com/camconn/spigot-monitor.git
    cd spigot-monitor
    mkdir spigot
    # copy spigot.jar into the spigot/ folder

    ./monitor.py
    # now open http://127.0.0.1:25564 in your browser

## FAQ

**Q**: Why make this when other, *better* server wrappers already exist?
**A**: All the other server wrappers are either written with PHP (too heavy for being
simply a wrapper IMO), Node.js (pulls in too many dependencies), or Java (eww, Java!).

**Q**: Does this support CraftBukkit/Bukkit?
**A**: It should. I named project *Spigot Monitor* because it will primarily be built to
integrate with Spigot. In the future, I'll formalize the CraftBukkit support.

**Q**: Implement feature `<x>`!
**A**: This project is pretty early in development, maybe later.

**Q**: I want to help!
**A**: Great! Don't worry about sticking to PEP8 too much. Try to write idiomatic code
that looks good. Submit a PR and I'll see what I can do.

**Q**: Port to Python 2!
**A**: Why? Python 2 is *old*. Submit a Pull Request, argue with me, and maybe you'll
convince me otherwise.

## License
This project is licensed under the GNU Affero Public License, Version 3 or Later. See
`LICENSE` for a copy.
