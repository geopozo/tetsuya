- [ ] Add in dynamic modules
- [ ] Review logs and do systemd logs
- [ ] Add caching to logs
- [ ] Add a cache status manager
- [ ] document cache rules
  - autorefresh will run cache)
  - what does 0 do? never cache? forever cache. Never cache, right?
- [ ] I think maybe a better command structure

Later todo
  - [ ] Add checking if git dirty or not pushed
  - [ ] Add some log statistics
  - [ ] Add some firewall statistics
  - [ ] Add updates
  - [ ] Add changelog (linux)
  - [ ] Add news, linux, hackernews?
  - [ ] Add website status check
  - [ ] Add google analytics check
  - [ ] But also constant ingress and event push (tetsuya)
  - [ ] Add something that checks on any request
  - [ ] Check itself


# Get it up on systemd

```
mkdir -p ~/.config/systemd/user

systemctl --user daemon-reload
systemctl --user enable --now "$(realpath tetsuya.service)"

loginctl enable-linger "$USER" # (allow it to start at boot)

journalctl --user -u tetsuya -f
```
