from rest_framework.serializers import ModelSerializer

from films.models import Films


class FilmModelSerializer(ModelSerializer):
    class Meta:
        model = Films
        exclude = ('slug',)


class ListFilmModelSerializer(ModelSerializer):
    direction = FilmModelSerializer(read_only=True)

    """
    List all FILMS command GET
    """

    class Meta:
        model = Films
        fields = ('id','direction', 'title', 'description', 'email', 'is_published', 'country', 'city', 'category', 'sub_category', 'author', 'type')

class FilmListModelSerializer(ModelSerializer):
    direction = FilmModelSerializer(read_only=True)

    class Meta:
        model = Films
        exclude = ('slug', )

class CreateFilmModelSerializer(ModelSerializer):
    direction = FilmModelSerializer(read_only=True)
    """
    Create FILM command POST
    """

    class Meta:
        model = Films
        exclude = ('slug', 'create_date', 'update_date')

class UpdateFilmModelSerializer(ModelSerializer):
    """
    Update Film obj/{id} PUT/PATCH
    """

    class Meta:
        model = Films
        exclude = ('slug', 'create_date', 'update_date')

class RetrieveFilmModelSerializer(ModelSerializer):
    direction = FilmModelSerializer(read_only=True)
    """
    GET ONE obj/{id} RETRIEVE
    """

    class Meta:
        model = Films
        fields = ('id', 'direction', 'title', 'description', 'email', 'is_published', 'country', 'city', 'category',
                  'sub_category', 'author', 'type')
