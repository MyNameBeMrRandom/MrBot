
def get_time(second):
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
			message += f'0{days}:'
		else:
			message += f'{days}:'
	else:
		message += '00:'
	if not hours == 0:
		if hours < 10:
			message += f'0{hours}:'
		else:
			message += f'{hours}:'
	else:
		message += '00:'
	if not minutes == 0:
		if minutes < 10:
			message += f'0{minutes}:'
		else:
			message += f'{minutes}:'
	else:
		message += '00:'
	if not seconds == 0:
		if seconds < 10:
			message += f'0{seconds}'
		else:
			message += f'{seconds}'
	else:
		message += '00'
	return message

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

def calculate_status_percentages(online_time, offline_time, idle_time, dnd_time):
	total = online_time + offline_time + idle_time + dnd_time
	online_p = online_time / total
	offline_p = offline_time / total
	idle_p = idle_time / total
	dnd_p = dnd_time / total
	online_percent = round(online_p * 100, 3)
	offline_percent = round(offline_p * 100, 3)
	idle_percent = round(idle_p * 100, 3)
	dnd_percent = round(dnd_p * 100, 3)
	total_percent = round(offline_percent + online_percent + idle_percent + dnd_percent, 3)
	return online_percent, offline_percent, idle_percent, dnd_percent, total_percent