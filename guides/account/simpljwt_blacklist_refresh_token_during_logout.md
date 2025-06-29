# How to resolve?

✅ **(Enable Blacklist)**:

1️⃣ **Add `'rest_framework_simplejwt.token_blacklist'` to `INSTALLED_APPS`:**

```python
INSTALLED_APPS = [
    # ...
    'rest_framework_simplejwt.token_blacklist',
]
```
2️⃣ **Then run migrations:**
```sh
python manage.py migrate
```

3️⃣ **Enable blacklist in `SIMPLE_JWT`:**
```python
SIMPLE_JWT = {
    'BLACKLIST_AFTER_ROTATION': True,
}
```

# example
```python

class UserLogoutView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'errors': {'refresh': 'this field is required!'}},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'message': 'Logout successful. Token blacklisted.'},
                            status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({'errors': {"non_field_erros": [str(e)]}},
                            status=status.HTTP_400_BAD_REQUEST)
```
