# import requests
# import base64
# import json
# import os

# from apscheduler.schedulers.blocking import BlockingScheduler

# APP = "gaid"
# KEY = os.environ.get('API_KEY')
# PROCESS = "worker"

# # Generate Base64 encoded API Key
# BASEKEY = base64.b64encode(":" + KEY)
# # Create headers for API call
# HEADERS = {
#     "Accept": "application/vnd.heroku+json; version=3",
#     "Authorization": BASEKEY
# }

# def scale(size: int) -> int:
#     try:
#         result = requests.patch(
#             f"https://api.heroku.com/apps/{APP}/formation/{PROCESS}",
#             headers=HEADERS, 
#             data=json.dumps(
#                 { 'quantity' : size }
#             )
#         )
#     except:
#         raise Exception(f"scale request failed")
#     if result.status_code == 200:
#         return 0
#     else:
#         return 1


# sched = BlockingScheduler()

# schedule = {
#     3  : 0,
#     10 : 1
# }

# for hour, amount in schedule.items():
#     func = lambda: scale(amount)
#     sched.scheduled_job(func, 'cron', hour=hour)

# sched.start()
