from flask_jwt_extended import create_refresh_token, get_jti

from api import app
from api.models import User


class TestLogin:
    path = '/login'

    @classmethod
    def setup_class(cls):
        u = User('214', 'qwe')
        u.save()
        cls.user = User('qwe', 'qwe')
        cls.user.save()

    def test_login_get(self, client):
        response = client.get(self.path)
        assert response.status_code == 405

    def test_login_post_non_json(self, client):
        response = client.post(self.path)

        assert response.status_code == 400

    def test_login_post_empty(self, client):
        data = {}
        response = client.post(self.path, json=data)

        assert response.status_code == 401

    def test_login_user_not_exist(self, client):
        data = {'username': 'qwe1234',
                'password': 'qwe'}
        response = client.post(self.path, json=data)
        json = response.get_json()

        assert response.status_code == 401
        assert json['message'] == 'Bad username or password'

    def test_login_user_wrong_password(self, client):
        data = {'username': 'qwe',
                'password': 'qwe1234'}
        response = client.post(self.path, json=data)
        json = response.get_json()

        assert response.status_code == 401
        assert json['message'] == 'Bad username or password'

    def test_login_post(self, client):
        data = {'username': 'qwe',
                'password': 'qwe'}
        response = client.post(self.path, json=data)
        json = response.get_json()

        assert response.status_code == 200
        assert 'access_token' in json
        assert 'refresh_token' in json


class TestRefresh:
    path = '/refresh'

    @classmethod
    def setup_class(cls):
        u = User('qwe', 'qwe')
        u.save()
        cls.user = User.query.filter_by(username='qwe').one()
        with app.app_context():
            cls.refresh_token = create_refresh_token(identity=cls.user)
            cls.user.refresh_token = get_jti(cls.refresh_token)
        cls.user.save()

    def test_refresh_get(self, client):
        response = client.get(self.path)
        assert response.status_code == 405

    def test_refresh_post_empty(self, client):
        response = client.post(self.path, )

        assert response.status_code == 401

    def test_refresh_post(self, client):
        headers = {
            'Authorization': f'Bearer {self.refresh_token}'
        }
        response = client.post(self.path, headers=headers)
        assert response.status_code == 200
        assert 'access_token' in response.get_json()
