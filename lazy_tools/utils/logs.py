def write_log(log_msg):
    with open(
        r"C:\Users\udtre\Projects\krita-plugin\krita-lazy-tools\lazy_tools\logs\log.txt",
        "a",
        encoding="utf-8",
    ) as f:
        f.write(log_msg + "\n")
