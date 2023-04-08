import requests

from poap.tasks.models import TaskUser


class BaseCheckMethod(object):
    def login(self, *args, **kwargs):
        raise NotImplementedError("login() must be implemented.")


class GithubLoginMixin:
    def login(self, *args, **kwargs):
        return True


class Github(GithubLoginMixin, BaseCheckMethod):
    def contributor(self, *args, **kwargs):
        return True


#
# def get_checker(site: int):
#     if site == TaskClass.SITE_GITHUB:
#         return Github
#     else:
#         raise ModuleNotFoundError


def get_checker(task_user: TaskUser):
    verification_url = task_user.task.verification_url
    resp = requests.get(verification_url, params={"wallet": task_user.user.address})
    return resp.status_code == 200
