"""
Phase 7 — Relational Django App Code Generator.

Generates models.py, serializers.py, views.py, and urls.py for a multi-resource schema,
mapping belongs_to fields to models.ForeignKey relations.
"""

from pathlib import Path
import os


def generate_django_model(parsed_data: dict) -> str:
    """Generate models.py content for all resources in the schema."""
    lines = [
        "from django.db import models",
        "",
        "",
    ]

    type_map = {
        "string": "models.CharField(max_length=255)",
        "integer": "models.IntegerField()",
        "decimal": "models.DecimalField(max_digits=10, decimal_places=2)",
        "boolean": "models.BooleanField(default=False)",
        "email": "models.EmailField()",
    }

    for resource in parsed_data["resources"]:
        resource_name = resource["resource"]
        fields = resource["fields"]

        lines.extend([
            f"class {resource_name}(models.Model):",
        ])

        for field in fields:
            name = field["name"]
            field_type = field["type"]

            if field_type == "belongs_to":
                target = field["target"]
                django_field = f"models.ForeignKey('{target}', on_delete=models.CASCADE)"
            elif field_type in type_map:
                django_field = type_map[field_type]
            else:
                raise ValueError(f"Unsupported field type: '{field_type}'")

            lines.append(f"    {name} = {django_field}")

        lines.append("")

        # Choose str representing field
        str_field = "pk"
        field_names = [f["name"] for f in fields]
        field_types = {f["name"]: f["type"] for f in fields}

        if "name" in field_names:
            str_field = "name"
        elif "email" in field_names:
            str_field = "email"
        else:
            for name, ftype in field_types.items():
                if ftype in ("string", "email"):
                    str_field = name
                    break

        lines.extend([
            "    def __str__(self):",
            f"        return str(self.{str_field})",
            "",
            "",
        ])

    return "\n".join(lines).strip() + "\n"


def generate_serializer(parsed_data: dict) -> str:
    """Generate serializers.py content for all resources."""
    lines = [
        "from rest_framework import serializers",
    ]

    models = [r["resource"] for r in parsed_data["resources"]]
    lines.append(f"from .models import {', '.join(models)}")
    lines.append("")

    for resource in parsed_data["resources"]:
        resource_name = resource["resource"]
        lines.extend([
            "",
            f"class {resource_name}Serializer(serializers.ModelSerializer):",
            "    class Meta:",
            f"        model = {resource_name}",
            "        fields = '__all__'",
        ])

    return "\n".join(lines).strip() + "\n"


def generate_views(parsed_data: dict) -> str:
    """Generate views.py content for all resources."""
    lines = [
        "from rest_framework import viewsets",
    ]

    models = [r["resource"] for r in parsed_data["resources"]]
    lines.append(f"from .models import {', '.join(models)}")
    lines.append(f"from .serializers import {', '.join(f'{m}Serializer' for m in models)}")
    lines.append("")

    for resource in parsed_data["resources"]:
        resource_name = resource["resource"]
        lines.extend([
            "",
            f"class {resource_name}ViewSet(viewsets.ModelViewSet):",
            f"    queryset = {resource_name}.objects.all()",
            f"    serializer_class = {resource_name}Serializer",
        ])

    return "\n".join(lines).strip() + "\n"


def generate_app_urls(parsed_data: dict) -> str:
    """Generate app/urls.py routing for all resources."""
    lines = [
        "from django.urls import path, include",
        "from rest_framework.routers import DefaultRouter",
    ]

    models = [r["resource"] for r in parsed_data["resources"]]
    imports = ", ".join(f"{m}ViewSet" for m in models)
    lines.extend([
        f"from .views import {imports}",
        "",
        "router = DefaultRouter()",
    ])

    for resource in parsed_data["resources"]:
        resource_name = resource["resource"]
        route_name = resource_name.lower() + "s"
        lines.append(
            f"router.register(r'{route_name}', {resource_name}ViewSet, basename='{resource_name.lower()}')"
        )

    lines.extend([
        "",
        "urlpatterns = [",
        "    path('', include(router.urls)),",
        "]",
    ])

    return "\n".join(lines).strip() + "\n"


def generate_project_settings() -> str:
    """Generate settings.py configuration."""
    return """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = 'django-insecure-api-forge-project-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'rest_framework',
    'app',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""


def generate_project_urls() -> str:
    """Generate root urls.py routing."""
    return """from django.urls import path, include

urlpatterns = [
    path('api/', include('app.urls')),
]
"""


def generate_manage_py() -> str:
    """Generate manage.py entrypoint."""
    return """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"""


def write_generated_code(parsed_data: dict, output_dir: str = "generated") -> str:
    """Write all project files to make a running Django REST app."""
    project_path = Path(output_dir)
    project_path.mkdir(exist_ok=True)
    
    app_path = project_path / "app"
    app_path.mkdir(exist_ok=True)

    (app_path / "__init__.py").write_text("")

    (app_path / "models.py").write_text(generate_django_model(parsed_data))
    (app_path / "serializers.py").write_text(generate_serializer(parsed_data))
    (app_path / "views.py").write_text(generate_views(parsed_data))
    (app_path / "urls.py").write_text(generate_app_urls(parsed_data))

    (project_path / "settings.py").write_text(generate_project_settings())
    (project_path / "urls.py").write_text(generate_project_urls())

    manage_file = project_path / "manage.py"
    manage_file.write_text(generate_manage_py())
    os.chmod(manage_file, 0o755)

    return str(project_path.absolute())
