import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from movies.models import Movie, Rating
from reviews.models import Review, Comment, Like
from products.models import PurchasedProduct

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=128)
    confirm_password = serializers.CharField(write_only=True, max_length=128)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "confirm_password",
            "nickname",
            "age",
            "bio",
            "gender",
        ]

    def validate(self, attrs):
        REGEX_EMAIL = "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        if not re.fullmatch(REGEX_EMAIL, attrs["email"]):
            raise serializers.ValidationError({"email": "이메일이 올바르지 않습니다."})

        if len(attrs["password"]) < 8:
            raise serializers.ValidationError(
                {"password": "패스워드는 8자 이상 입력되어야 합니다."}
            )

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password_confirm": "패스워드가 일치하지 않습니다."}
            )

        if len(attrs["nickname"]) > 20:
            raise serializers.ValidationError(
                {"nickname": "닉네임의 최대 길이는 20자 입니다."}
            )

        if attrs.get("age") is not None:
            if attrs["age"] < 0 or attrs["age"] > 150:
                raise serializers.ValidationError(
                    {"age": "나이는 0세 이상 150세 이하로 입력 가능합니다."}
                )

        return attrs

    def send_verification_email(self, user, uid, token):
        message = render_to_string(
            "accounts/account_active_email.html",
            {
                "user": user,
                "domain": "127.0.0.1:8000",  # 실제 도메인으로 교체
                "uid": uid,
                "token": token,
            },
        )
        send_mail(
            subject="Activate your account",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname"),
            gender=validated_data.get("gender"),
            age=validated_data.get("age"),
            bio=validated_data.get("bio"),
        )
        user.is_active = False  # 이메일 인증 전에는 계정 비활성화
        user.save()

        # 이메일 전송을 위한 토큰 생성
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))  # .decode("utf-8")

        # 이메일 전송
        self.send_verification_email(user, uid, token)

        return user


class UserSigninSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # 사용자가 존재하는지 확인
        user = User.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError(
                "이메일 혹은 패스워드가 일치하지 않습니다."
            )

        # 비활성화된 계정일 경우
        if not user.is_active:
            self.send_activation_email(user)
            raise serializers.ValidationError(
                "계정이 비활성화 상태입니다. 이메일 인증을 통해 계정을 활성화해주세요."
            )

        # 사용자 인증
        if not user.check_password(password):
            raise serializers.ValidationError(
                "이메일 혹은 패스워드가 일치하지 않습니다."
            )

        return attrs

    def send_activation_email(self, user):

        # 이메일 전송을 위한 토큰 생성
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        subject = "Activate Your Account"
        message = render_to_string(
            "accounts/account_active_email.html",  # 이메일 템플릿 경로
            {
                "user": user,
                "domain": "127.0.0.1:8000",  # 도메인 설정
                "uid": uid,  # 사용자 ID 인코딩
                "token": token,  # 활성화 토큰 생성
            },
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # 발신자 이메일
            [user.email],  # 수신자 이메일
            fail_silently=False,
        )


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["old_password", "new_password", "confirm_password"]

    def validate_old_password(self, value):
        """기존 비밀번호를 바르게 입력하였는지 확인합니다.
        기존 패스워드와 입력한 old_password가 다르다면 에러 메세지를 출력하고
        일차한다면 패스워드를 리턴합니다."""

        user = self.context
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"error": "기존 패스워드가 일치하지 않습니다."}
            )
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"error": "새로운 패스워드와 확인 패스워드가 일치하지 않습니다."}
            )

        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"error": "기존 패스워드와 변경하려는 패스워드가 동일합니다."}
            )

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "nickname",
            "gender",
            "age",
            "bio",
        ]

    def validate_age(self, value):
        if value and ((value < 0) or (value > 150)):
            raise serializers.ValidationError(
                {"error": "나이는 0세 이상 150세 이하로 입력 가능합니다."}
            )
        return value


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["title"]


class ReviewSerializer(serializers.ModelSerializer):
    movie = serializers.ReadOnlyField(source="movie.title")

    class Meta:
        model = Review
        fields = ["movie", "content", "private"]


class CommentSerializer(serializers.ModelSerializer):
    movie = serializers.ReadOnlyField(source="movie.title")

    class Meta:
        model = Comment
        fields = ["review", "content"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nickname"]


class RatingSerializer(serializers.ModelSerializer):
    movie = serializers.ReadOnlyField(source="movie.title")

    class Meta:
        model = Rating
        fields = ["movie", "score"]


class LikedReviewSerializer(serializers.ModelSerializer):
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["review"]

    def to_representation(self, instance):
        # 부모 클래스의 to_representation() 호출
        representation = super().to_representation(instance)

        # review가 None이거나 직렬화 결과가 비어 있으면 빈 딕셔너리 반환 방지
        if not representation.get("review"):
            return None  # 빈 객체가 아닌 None을 반환하여 리스트에서 제거되도록 처리

        return representation


class LikedCommentSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["comment"]

    def to_representation(self, instance):
        # 부모 클래스의 to_representation() 호출
        representation = super().to_representation(instance)

        # comment가 None이거나 직렬화 결과가 비어 있으면 빈 딕셔너리 반환 방지
        if not representation.get("comment"):
            return None  # 빈 객체가 아닌 None을 반환하여 리스트에서 제거되도록 처리

        return representation


class PurchasedProductSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = PurchasedProduct
        fields = [
            "product",
            "merchant_uid",
            "price",
            "status",
        ]

    def get_product(self, obj):
        return obj.product.name

    def get_status(self, obj):
        return dict(PurchasedProduct.STATUS_SELECT).get(obj.status)


class UserProfileSerializer(serializers.ModelSerializer):
    liked_movies = MovieSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True,)
    followings = UserSerializer(many=True)
    followings_count = serializers.IntegerField(
        source="followings.count", read_only=True
    )
    followers = UserSerializer(many=True)
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)
    rated_movie = RatingSerializer(many=True, read_only=True, source="ratings")
    liked_reviews = serializers.SerializerMethodField()
    liked_comments = serializers.SerializerMethodField()
    purchased_products = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "nickname",
            "followings",
            "followings_count",
            "followers",
            "followers_count",
            "gender",
            "age",
            "bio",
            "rated_movie",
            "liked_movies",
            "reviews",
            "liked_reviews",
            "liked_comments",
            "purchased_products",
        ]

    def get_liked_reviews(self, obj):
        # LikedReviewSerializer로 직렬화한 후 유효한 데이터만 필터링
        reviews = LikedReviewSerializer(
            obj.likes_given.filter(review__isnull=False), many=True
        ).data
        return [
            review for review in reviews if review
        ]  # None 값이 아닌 유효한 리뷰만 반환

    def get_liked_comments(self, obj):
        # LikedCommentSerializer로 직렬화한 후 유효한 데이터만 필터링
        comments = LikedCommentSerializer(
            obj.likes_given.filter(comment__isnull=False), many=True
        ).data
        return [
            comment for comment in comments if comment
        ]  # None 값이 아닌 유효한 댓글만 반환

    def get_purchased_products(self, obj):
        # PurchasedProductSerializer로 직렬화한 후 유효한 데이터만 반환
        products = PurchasedProductSerializer(obj.products.all(), many=True).data
        return [product for product in products if product]
