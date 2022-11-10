from django_filters import FilterSet, DateRangeFilter
from .models import Reply, Post


class PostFilter(FilterSet):
    created = DateRangeFilter()

    def __init__(self, *args, **kwargs):
        super(PostFilter, self).__init__(*args, **kwargs)
        self.filters['post'].queryset = Post.objects.filter(author_id=kwargs['request'])

    class Meta:
        model = Reply
        fields = ('text', 'created', 'post')