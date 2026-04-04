from locust import HttpUser, task, between

class HackathonUser(HttpUser):
    # Each user waits between 1 and 5 seconds between tasks
    wait_time = between(1, 5)

    @task
    def view_users(self):
        self.client.get("/users")

    @task
    def health_check(self):
        self.client.get("/health")
