from locust import HttpUser, task, between
import random


class QuickstartUser(HttpUser):
    wait_time = between(10, 25)

    @task
    def backtest(self):
        API = f"/api/v1/stocks/historical_performance/value:country;US,range:ps;{random.randint(0,100)};{random.randint(100,1000)}&01-01-2010"
        self.client.get(API)

    # @task
    # def screening(self):
    #     API = f"/api/v1/stocks/tickers_with_criteria/value:country;US,range:pe;{random.randint(0,100)};{random.randint(100,1000)}&0&10"
    #     self.client.get(API)
