from locust import HttpUser, task, between, TaskSet
import json


class UserBehavior(TaskSet):

    def __init__(self, parent):
        super(UserBehavior, self).__init__(parent)

        self.token = ""
        self.headers = {}

    def on_start(self):
        self.token = self.login()
        print('🛑🛑', self.token)

        self.headers = {'Authorization': 'JWT ' + self.token}

    def login(self):
        response = self.client.post(
            "/auth/jwt/create/", data={'username': 'Gaurav', 'password': 'ilovedjango'})
        print('🛑🛑', response)
        return response['access']
        # return json.loads(response.content)['acess']


class WebsiteUser(HttpUser):
    task_set = UserBehavior
    wait_time = between(1, 7)

    # viewing posts:

    @task(2)
    def view_posts(self):
        self.client.get(
            f'/post/',
            name='all posts'
        )

    @task(4)
    def toggle_like(self):
        self.client.post(
            f'/post/like/',
            name='like/dislike post',
            json={  # to send the data
                'post_id': 1,
            }
        )
