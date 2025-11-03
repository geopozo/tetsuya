# tetsuya

tetsuya collects information and offers it up as JSON packets and pretty
print strings.

It's *very* easy to extend:

- Write a function (a *service*) that collects information from web/system.
  - It takes a `dataclass` as a *config* object (can be empty).
  - It returns another `dataclass` as a *report*.

tetsuya offers the *report* object to your user (and your user only) as a JSON
endpoint available via REST and command-line interface.

You will also define two functions on your *report* dataclass: `short()` and
`long()` which can pretty-print the JSON.

It does some helpful stuff automatically:

1. tetsuya can cache your new *service* for you and auto-refresh the cache: all
   tetsuya service configs have a cachelife integer and autorefresh boolean.

2. tetsuya will derive the default config from your `dataclass`, but will read a
   .toml if you want to change it.

3. tetsuya runs in a client-server model, with a background daemon doing the
   work, and a CLI interface for basic control.

Try `uvx tetsuya --help-tree=ascii` to see the whole interface.

## Installation

### Daemon on systemd

Theres a *tetsuya.service* file in the repository.

```bash
mkdir -p ~/.config/systemd/user

systemctl --user daemon-reload
systemctl --user enable --now "$(realpath ./tetsuya.service)"

loginctl enable-linger "$USER" # (allow it to start at boot even if logged out)

journalctl --user -u tetsuya -f
```

## Roadmap

- [ ] Some early modules:
  - [ ] Do a Basic 200 is it good thing
    - [ ] Check domains for email record
    - [ ] Check SLL
  - [ ] Active sessions on linux
  - [ ] Updates available
    - [ ] Changelog on kernel

    ```bash
    if which yay 1> /dev/null; then
      (
      set -e
      yay -Qu
      yay -Pw
      checkupdates
      )
    fi
    ```

- [ ] Any errors on systemd + --kernel
- [ ] Monarch Money from that guy? - MoneyFlown and redeploy
- [ ] Improve naming and arguments, flags, etc.
  - [ ] -> Services to Client
  - [ ] Names of services = arguments
  - [ ] Add help descriptions
  - [ ] Turn off options like --thing, --no-thing, if --no-thing is default?
  - [ ] Go back to CLI and do the formatting better
- [ ] Document throughout code
- [ ] If we want to instantiate multiple instances of one service class:
- [ ]  Inspect:
  - [ ] all instances of get_name()
  - [ ] how services are registered
  - [ ] Consider Dictionary Storage and Access Here:
    - [ ] `_config.config_data`
    - [ ] `_timer.timer_tasks`
    - [ ] `service manager.??` (Not written at this time)
  - [ ] Will have to pass both service obj + class to _config, _timer
  - [ ] Make room for customed name in config + `.get_name()`
  - [ ] Start will have change (calls a lot of this stuff)
- [ ] Don't enable service until it has a config
  - [ ] Allow per app config default generation
  - [ ] Upon reload, recalculate active services
  - [ ] Config API:
    - [ ] Separate Touch and Dump
- [ ] Create persistence:
  - [ ] Roundtrip reports upon registering (json and back)
  - [ ] Save reports upon running
  - [ ] Load reports upong starting
- [ ] Services can subscribe to changes of other services
- [ ] Importing modules dynamically from a subfoler

### Desired Modules

- [ ] Google drive auditor, google accounts/emails
- [ ] Check agreements (modules subscribed to other modules)
  - [ ] are we checking all domains that namecheap lists
  - [ ] does google list all
- [ ] Analytics summary + link

- [ ] Git status
- [ ] Scrape forum posts
- [ ] Firewall stats
- [ ] process accounting?
