# Get it up on systemd

```bash
mkdir -p ~/.config/systemd/user

systemctl --user daemon-reload
systemctl --user enable --now "$(realpath tetsuya.service)"

loginctl enable-linger "$USER" # (allow it to start at boot)

journalctl --user -u tetsuya -f
```

## Roadmap

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
- [ ] process accounting?
