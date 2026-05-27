try:
    from Lumen_Garden.app import run
except ModuleNotFoundError as exc:
    if exc.name == "pygame":
        raise SystemExit("pygame is not installed. Run: python -m pip install -r requirements.txt")
    raise


if __name__ == "__main__":
    run()
