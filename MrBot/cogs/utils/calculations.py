def calculate_status_times(times):
	minute, second = divmod(times, 60)
	hour, minute = divmod(minute, 60)
	day, hour = divmod(hour, 24)
	days = round(day)
	hours = round(hour)
	minutes = round(minute)
	seconds = round(second)
	return f'{days}d, {hours}h, {minutes}m, {seconds}s'

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