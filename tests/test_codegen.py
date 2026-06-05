"""
Phase 3 — Code Generator Tests.

Verifies translation of parsed dictionary to full Django REST project.
"""

import pytest
from apiforge.compiler.codegen import (
    generate_django_model,
    generate_serializer,
    generate_views,
    generate_app_urls,
    write_generated_code,
)


class TestGenerateDjangoComponents:
    """Test individual component generators."""

    @pytest.fixture
    def mock_data(self):
        return {
            "resource": "Product",
            "fields": [{"name": "name", "type": "string"}]
        }

    def test_generates_model(self, mock_data):
        code = generate_django_model(mock_data)
        assert "class Product(models.Model):" in code
        assert "name = models.CharField(max_length=255)" in code

    def test_generates_serializer(self, mock_data):
        code = generate_serializer(mock_data)
        assert "from rest_framework import serializers" in code
        assert "class ProductSerializer(serializers.ModelSerializer):" in code
        assert "model = Product" in code
        assert "fields = '__all__'" in code

    def test_generates_views(self, mock_data):
        code = generate_views(mock_data)
        assert "from rest_framework import viewsets" in code
        assert "class ProductViewSet(viewsets.ModelViewSet):" in code
        assert "queryset = Product.objects.all()" in code
        assert "serializer_class = ProductSerializer" in code

    def test_generates_app_urls(self, mock_data):
        code = generate_app_urls(mock_data)
        assert "router.register(r'products', ProductViewSet" in code
        assert "path('', include(router.urls))" in code


class TestWriteGeneratedProject:
    """Test full folder writing logic."""

    def test_creates_django_project_structure(self, tmp_path):
        mock_data = {
            "resource": "Product",
            "fields": [{"name": "name", "type": "string"}]
        }
        
        project_dir = tmp_path / "django_project"
        write_generated_code(mock_data, output_dir=str(project_dir))

        # Check project files
        assert (project_dir / "manage.py").exists()
        assert (project_dir / "settings.py").exists()
        assert (project_dir / "urls.py").exists()

        # Check app files
        app_dir = project_dir / "app"
        assert (app_dir / "__init__.py").exists()
        assert (app_dir / "models.py").exists()
        assert (app_dir / "serializers.py").exists()
        assert (app_dir / "views.py").exists()
        assert (app_dir / "urls.py").exists()
