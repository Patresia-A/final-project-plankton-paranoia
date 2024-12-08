import re


def parse_bpm(bpm_str):
    try:
        bpm = int(bpm_str)
        if bpm < 0:
            raise ValueError("BPM cannot be negative")
        return bpm
    except ValueError:
        raise ValueError("Invalid BPM value")


def parseBPM(bpm_str):
    bpm_str = bpm_str.strip()

    match = re.search(r'(\d+)\s*-\s*(\d+)|(\d+)', bpm_str)
    if match:
        if match.group(1) and match.group(2):
            return {
                "lower": match.group(1).strip(),
                "higher": match.group(2).strip()
            }
        else:
            return {
                "lower": match.group(3).strip(),
                "higher": match.group(3).strip()
            }
    else:
        raise ValueError("Invalid BPM format")
