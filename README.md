# Get it up on systemd

```bash
mkdir -p ~/.config/systemd/user

systemctl --user daemon-reload
systemctl --user enable --now "$(realpath tetsuya.service)"

loginctl enable-linger "$USER" # (allow it to start at boot)

journalctl --user -u tetsuya -f
```

## Roadmap

- [ ] Fix API
  - [ ] Pull back in cli-tree
  - [ ] Reorganize folders
    - [ ] Should there be a globals? Should it pull from server/client or...?
  - [ ] Make execute take a config (get rid of the stuff you hate)
  - [ ] Organize commands into server/slient subcommands
  - [ ] Improve naming and arguments and stuff
    - [ ] Add help descriptions
    - [ ] Turn off options like --thing, --no-thing, if --no-thing is default?
    - [ ] Go back to CLI and do the formatting better
  - [ ] Add logging for caches services/start stop
    - [ ] Make service start stop an object
  - [ ] Add a server command for actual start and stop service
  - [ ] Make a cache/timer state tracker
  - [ ] Config improvements
    - [ ] Show config of one unit
    - [ ] Does default overwrite? Can default overwrite for one unit?
    - [ ] Single unit config operations.
  - [ ] Create import module service
  - [ ] Create cache status service
  - [ ] Docs on writing a service
  - [ ] Subscribed Services (subscribe to changes)
    - [ ] A diff function
    - [ ] New reports optionally take old reports

### Desired Modules

- [ ] Do a Basic 200 is it good thing
  - [ ] What about domain name stuff
  - [ ] What about server stuff
  - [ ] Email
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
- [ ] Analytics summary + link

- [ ] Google drive auditor, google accounts
- [ ] Git status
- [ ] Some finance information
- [ ] Scrape forum posts
- [ ] Firewall stats
- [ ] Process accounting?
