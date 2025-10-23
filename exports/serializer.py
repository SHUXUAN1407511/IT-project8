from rest_framework import serializers

class ExportTableSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    data = serializers.DictField(child=serializers.ListField(), allow_empty=False)

    def validate(self, attrs):
        data = attrs['data']
        lengths = {k: len(v) for k, v in data.items()}
        if len(set(lengths.values())) > 1:
            raise serializers.ValidationError({'data': f'All columns must have the same length, got: {lengths}'})
        return attrs