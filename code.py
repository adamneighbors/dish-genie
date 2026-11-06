# CircuitPython entrypoint. Keep imports lazy so `import code` (stdlib / pytest /
# pdb) does not pull in device-only modules when running tests from this repo.
def _run():
    from dish_genie_device import DishGenie

    DishGenie()


if __name__ == '__main__':
    _run()
