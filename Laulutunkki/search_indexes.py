from haystack import indexes
from Laulutunkki.models import Song, Booklet


class SongIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created = indexes.DateTimeField(model_attr='created')

    # Index by title and lyrics for autocomplete
    title_auto = indexes.EdgeNgramField(model_attr='title')
    lyrics_auto = indexes.EdgeNgramField(model_attr='lyrics')
    category_auto = indexes.EdgeNgramField(model_attr='category')

    def get_model(self):
        return Song

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class BookletIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    created = indexes.DateTimeField(model_attr='created')

    # Index title for autocomplete
    title_auto = indexes.EdgeNgramField(model_attr='title') 
    author_auto = indexes.EdgeNgramField(model_attr='author')

    def get_model(self):
        return Booklet

    def index_queryset(self, using=None):
        return self.get_model().objects.all()