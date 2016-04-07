import time


def adaptive_sleeper(lower, rate, upper):
	sleep_time = lower

	def adaptive_sleep(reset=False):
		nonlocal sleep_time
		if reset:
			sleep_time = lower
		else:
			time.sleep(sleep_time)
			sleep_time *= rate
			if sleep_time > upper:
				sleep_time = upper

	return adaptive_sleep