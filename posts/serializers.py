from rest_framework import serializers
from .models import Post, PostImage, Category
from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']

class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    images = PostImageSerializer(many=True, read_only=True)
    author_phone_number = PhoneNumberField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'category', 'description', 'date', 'author_phone_number', 'author_email', 'product_name', 'images']
        read_only_fields = ['date']

    def create(self, validated_data):
        images_data = self.context.get('request').FILES.getlist('images') if self.context.get('request') else []
        post = Post.objects.create(**validated_data)
        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)
        return post

    def update(self, instance, validated_data):
        images_data = self.context.get('request').FILES.getlist('images') if self.context.get('request') else []
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.author_phone_number = validated_data.get('author_phone_number', instance.author_phone_number)
        instance.author_email = validated_data.get('author_email', instance.author_email)
        instance.product_name = validated_data.get('product_name', instance.product_name)
        instance.save()
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                PostImage.objects.create(post=instance, image=image_data)
        return instance

    def validate_product_name(self, value):
        if len(value) > 255:
            raise serializers.ValidationError("Product name is too long.")
        return value

    def validate_author_email(self, value):
        if "@" not in value:
            raise serializers.ValidationError("Invalid Email")
        return value

    def validate(self, data):
        if self.context and self.context.get('request'):
            image_count = len(self.context.get('request').FILES.getlist('images'))
            if image_count > 6:
                raise serializers.ValidationError({"non_field_errors": ["Too many images uploaded."] })
        return data