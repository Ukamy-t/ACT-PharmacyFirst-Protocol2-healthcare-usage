from datetime import date

start = date(2022, 2, 1)
end = date(2026, 3, 31)

def month_range(start, end):
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return dates