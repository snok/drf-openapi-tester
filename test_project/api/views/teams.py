from rest_framework_json_api.views import RelationshipView
from rest_framework.views import Response
    
class TeamMembersRelationshipView(RelationshipView):
    def post(self, request, *args, **kwargs):
        return Response({}, 200)