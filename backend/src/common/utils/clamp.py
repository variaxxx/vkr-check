def clamp(num: int, l: int, r: int) -> int:
    if not isinstance(num, int):
        return num
    return max(l, min(num, r))
