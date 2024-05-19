from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class UsageAnonRateThrottle(AnonRateThrottle):
    THROTTLE_RATES = {"anon": "10/1min"}

class UsageUserRateThrottle(UserRateThrottle):
    THROTTLE_RATES = {"user": "20/min"}