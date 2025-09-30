from tetsuya.cli import register

# called with -m tetsuyah, sort of a weird way to access cli
if __name__ == "__main__":
    for watcher in tuple(f() for f in register()):
        watcher.do()
