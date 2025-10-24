import hashlib
import json
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import PasswordResetToken, User


class PasswordResetFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='alice',
            password=make_password('old-password'),
            role='tutor',
            email='alice@example.com',
            status=User.STATUS_ACTIVE,
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_request_creates_token_and_sends_email(self):
        response = self.client.post(
            '/api/auth/password/reset',
            data=json.dumps({'email': self.user.email}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        tokens = PasswordResetToken.objects.filter(user=self.user)
        self.assertEqual(tokens.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body
        self.assertIn('reset', email_body.lower())
        self.assertIn('token=', email_body)

    def test_confirm_with_valid_token_updates_password(self):
        raw_token = 'sample-token-value'
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        PasswordResetToken.objects.create(
            user=self.user,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(minutes=30),
        )
        response = self.client.post(
            '/api/auth/password/reset/confirm',
            data=json.dumps({'token': raw_token, 'newPassword': 'new-strong-pass'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(check_password('new-strong-pass', self.user.password))
        token_entry = PasswordResetToken.objects.get(user=self.user)
        self.assertIsNotNone(token_entry.used_at)

    def test_confirm_with_invalid_token_fails(self):
        response = self.client.post(
            '/api/auth/password/reset/confirm',
            data=json.dumps({'token': 'bad', 'newPassword': 'newpass123'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
