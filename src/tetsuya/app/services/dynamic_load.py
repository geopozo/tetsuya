import platformdirs
import importlib.util


module_dir = platformdirs.user_data_dir("tetsuya", "pikulgroup") / "modules"

py_files  = moudle_dir.glob("*.py")

for f in py_files:
    if f.stem.startswith("_"):
        # untested
        continue
    spec  = importlib.util.spec_from_file_location(f.stem, str(f))
    if spec is None:
        raise FileNotFoudnError(f"Couldn't import spec for {f!s}")

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    # think it would be better to do this in a new interpreter, 3.14 for the win
    # the server has no way to restart w/ same state after an error
    # better hierarchy and stuff

    # this needs to be a cli




# How do we undo them? Keep a separate list?
