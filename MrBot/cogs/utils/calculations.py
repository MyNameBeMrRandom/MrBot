
def get_time(second):
    """
    Converts an amount of seconds into a readable format.
    """
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

def get_time_friendly(second):
    """
    Converts an amount of seconds into a readable format.
    """

    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    hours = round(hour)
    minutes = round(minute)
    seconds = round(second)
    days = round(day)
    message = ""
    if not days == 0:
        if days < 10:
            message += f'0{days}d, '
        else:
            message += f'{days}d, '
    else:
        message += '00d, '
    if not hours == 0:
        if hours < 10:
            message += f'0{hours}h, '
        else:
            message += f'{hours}h, '
    else:
        message += '00h, '
    if not minutes == 0:
        if minutes < 10:
            message += f'0{minutes}m, '
        else:
            message += f'{minutes}m, '
    else:
        message += '00m, '
    if not seconds == 0:
        if seconds < 10:
            message += f'0{seconds}s'
        else:
            message += f'{seconds}s'
    else:
        message += '00s'
    return message

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
