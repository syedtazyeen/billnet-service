#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django


def get_apps_in_directory():
    """Get all apps in the apps/ directory that have apps.py."""
    apps_dir = os.path.join(os.path.dirname(__file__), "apps")
    app_names = []

    if os.path.exists(apps_dir):
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            if os.path.isdir(item_path):
                apps_py_path = os.path.join(item_path, "apps.py")
                if os.path.exists(apps_py_path):
                    if item == "auth":
                        continue
                    app_names.append(item)

    return app_names


def makemigrations():
    """Run makemigrations for all apps in apps/ directory."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from django.core.management import call_command  # pylint: disable=import-outside-toplevel

    app_names = get_apps_in_directory()
    if not app_names:
        print("⚠️ No apps found with apps.py in apps/ directory")
        return

    print(f"🔄 Running makemigrations for {len(app_names)} apps: {', '.join(app_names)}")

    for app_name in app_names:
        try:
            print(f"\n🔄 Running makemigrations for {app_name}...")
            call_command("makemigrations", app_name, verbosity=1)
            print(f"✅ Completed makemigrations for {app_name}")
        except Exception as e:
            print(f"❌ Error running makemigrations for {app_name}: {str(e)}")

    print(f"\n✅ Completed makemigrations for all {len(app_names)} apps")


def migrate():
    """Run migrate for all apps in apps/ directory."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from django.core.management import call_command  # pylint: disable=import-outside-toplevel

    app_names = get_apps_in_directory()
    if not app_names:
        print("⚠️ No apps found with apps.py in apps/ directory")
        return

    print(f"🔄 Running migrate for {len(app_names)} apps: {', '.join(app_names)}")

    for app_name in app_names:
        try:
            print(f"\n🔄 Running migrate for {app_name}...")
            call_command("migrate", app_name, verbosity=1)
            print(f"✅ Completed migrate for {app_name}")
        except Exception as e:
            print(f"❌ Error running migrate for {app_name}: {str(e)}")

    print(f"\n✅ Completed migrate for all {len(app_names)} apps")


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
