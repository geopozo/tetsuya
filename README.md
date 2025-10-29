# Get it up on systemd

```
mkdir -p ~/.config/systemd/user

systemctl --user daemon-reload
systemctl --user enable --now "$(realpath tetsuya.service)"

loginctl enable-linger "$USER" # (allow it to start at boot)

journalctl --user -u tetsuya -f
```

## Desired modules

- [ ] Active sessions on linux
- [ ] Updates available
- [ ] Uptime
- [ ] Any errors on systemd + --kernel
- [ ] Changelog on kernel
- [ ] Domains status (email and everything)
- [ ] Websites ok
- [ ] Google drive auditor, google accounts
- [ ] Analytics summary + link
- [ ] Personal directory status
- [ ] Git status
- [ ] Some finance information
- [ ] Do scraping and notification of forums and such (subscribe, itll be an onslaught)
- [ ] Github helper with auditor
- [ ] Git checker
- [ ] Firewall stats
- [ ] process accounting?

- [ ] Connect to other services and get their JSON?

