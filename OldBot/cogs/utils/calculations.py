import random

def get_time(second):

    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    days = round(day)
    hours = round(hour)
    minutes = round(minute)
    seconds = round(second)
    if minutes == 0:
        return f"{seconds}s"
    if hours == 0:
        return "%02d:%02d" % (minutes, seconds)
    if days == 0:
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
    return "%02d:%02d:%02d:%02d" % (days, hours, minutes, seconds)

def get_time_friendly(second):

    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    days = round(day)
    hours = round(hour)
    minutes = round(minute)
    seconds = round(second)
    if minutes == 0:
        return f"%02ds" % seconds
    if hours == 0:
        return "%02dm %02ds" % (minutes, seconds)
    if days == 0:
        return "%02dh %02dm %02ds" % (hours, minutes, seconds)
    return "%02dd %02dh %02dm %02ds" % (days, hours, minutes, seconds)

def calculate_percentages(numbers, decimal):
    """
    Takes a list of numbers and calculate the percatage of each one out the total.
    """

    # Define a list called percentages.
    percentages = []
    # Calculate the total of the numbers in the list.
    total = sum(numbers)
    # Calculate the percent out the total and add it to the list
    for number in numbers:
        percent = round(number / total * 100, decimal)
        percentages.append(percent)
    # Calaculate the total percent and add it to the list
    total_percent = round(sum(percentages), decimal)
    percentages.append(total_percent)
    # Return the list
    return percentages

def random_colour():
    r = lambda: random.randint(0, 255)
    return '%02X%02X%02X' % (r(), r(), r())

