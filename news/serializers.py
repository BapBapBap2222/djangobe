from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_fullname = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'thumbnail', 'author',
            'author_name', 'author_fullname', 'views_count', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'views_count']

    def validate_title(self, value):
        normalized = value.strip()
        if not normalized:
            raise serializers.ValidationError("Title cannot be blank.")
        return normalized

    def validate_content(self, value):
        normalized = value.strip()
        if not normalized:
            raise serializers.ValidationError("Content cannot be blank.")
        return normalized

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret.get('thumbnail'):
            request = self.context.get('request', None)
            if request is not None:
                ret['thumbnail'] = request.build_absolute_uri(ret['thumbnail'])
        return ret
