from flask import request
from flask_restful import marshal, Resource


class ListResource(Resource):
    query = None
    model = None
    fields = {}
    envelope = 'books_list'

    def get(self):
        self.get_objects()
        result = marshal(self.objects, self.fields, envelope=self.envelope)
        return result, 200

    def get_query(self):
        return self.query or self.model.query

    def get_objects(self):
        query = self.get_query()
        self.objects = self.query.all()


class ObjectResource(Resource):
    query = None
    model = None
    model_id_field = None
    fields = {}

    def get(self, id):
        self.object_id = id
        self.get_object()
        if self.object is not None:
            result = marshal(self.object, self.fields)
            return result, 200
        else:
            return {}, 404

    def get_query(self):
        return self.query or self.model.query

    def get_object(self):
        query = self.get_query()
        self.object = self.query.filter_by(**{self.model_id_field: self.object_id}).one_or_none()


class PaginationMixin:
    """Pagination mixin. Request params are handled by flask-sqlalchemy Paginator class"""
    paginate_by = 10
    page_url = None

    def get_pagination_links(self):

        links = {'base': request.base_url, 'total': self.paginator.total}
        print()

        if self.paginator.next_num:
            links = {**links, 'next': f'{request.base_url}?page={self.paginator.next_num}'}

        if self.paginator.prev_num:
            links = {**links, 'prev': f'{request.base_url}?page={self.paginator.prev_num}'}

        if 1 < self.paginator.pages != self.paginator.page:
            links = {**links, 'last': f'{request.base_url}?page={self.paginator.pages}'}

        return links

    def get_query(self):
        query =super().get_query()
        return query

    def get_objects(self):
        query = self.get_query()
        self.paginator = query.paginate(per_page=self.paginate_by)
        self.objects = self.paginator.items


class PaginatedListResource(PaginationMixin, ListResource):
    def get(self):
        self.get_objects()
        links = self.get_pagination_links()
        result = marshal(self.objects, self.fields, envelope=self.envelope)
        result.update({'links': links})
        result.move_to_end('links', last=False)
        return result, 200

class OnlyJsonMixin:
    def dispatch_request(self, *args, **kwargs):
        if not request.is_json:
            return {'message':'Only JSON allowed'},400
        return super().dispatch_request(*args, **kwargs)

# class AdminAccessMixin:
#     def get(self, *args, **kwargs):
#         pass
#