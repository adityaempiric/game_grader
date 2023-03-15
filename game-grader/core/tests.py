from django.test import Client, TestCase, RequestFactory
from .models import User,TeamDetail
from django.urls import reverse
from .views import NewteamView
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile

class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
    def test_get_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signin.html')
        
    def test_post_view_with_valid_credentials(self):
        response = self.client.post(
            reverse('login'),
            {'user_name': 'testuser', 'pass_word': 'testpassword'}
        )
        self.assertRedirects(response, '/home/')
        
    def test_post_view_with_invalid_credentials(self):
        response = self.client.post(
            reverse('login'),
            {'user_name': 'testuser', 'pass_word': 'incorrectpassword'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signin.html')
        self.assertContains(response, "Error: Invalide Login Credential...")


class NewteamViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', email='testuser@email.com', password='secret')

    def test_post_request(self):
        cover_pic = SimpleUploadedFile("/home/empiric19/Documents/game-grader/static/img/pexels-andrea-piacquadio-3779760.jpg", b"file_content", content_type="image/jpeg")
        icon_pic = SimpleUploadedFile("/home/empiric19/Documents/game-grader/static/img/pexels-andrea-piacquadio-3779760.jpg", b"file_content", content_type="image/jpeg")

        request = self.factory.post('/newteam/', {
            'new_team_name': 'Test Team',
            'new_team_desc': 'Test description',
            'sport': 'Soccer',
        }, format='multipart')
        request.user = self.user
        request.FILES['cover-pic'] = cover_pic
        request.FILES['icon-pic'] = icon_pic

        response = NewteamView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        # Check if a new team is created
        team_code = str(uuid.uuid4().hex[:8])
        team = TeamDetail.objects.get(team_code=team_code)
        self.assertEqual(team.team_name, 'Test Team')
        self.assertEqual(team.team_description, 'Test description')
        self.assertEqual(team.sport, 'Soccer')
