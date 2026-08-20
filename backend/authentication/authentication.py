# 

from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):

        print("========== JWT DEBUG ==========")
        print("COOKIES:", request.COOKIES)

        access_token = request.COOKIES.get("access_token")

        print("ACCESS TOKEN:", access_token)

        if not access_token:
            print("❌ ACCESS TOKEN NOT FOUND")
            print("================================")
            return None

        print("✅ ACCESS TOKEN FOUND")

        validated_token = self.get_validated_token(access_token)

        print("✅ TOKEN VALID")

        user = self.get_user(validated_token)

        print("✅ USER:", user)
        print("================================")

        return (
            user,
            validated_token,
        )