
def is_power_of_2(n: int):
    if n == 0:
        return False
    return (n & (n - 1)) == 0
