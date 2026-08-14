from pathlib import Path


def test_production_compose_exists_and_contains_required_services():
    compose = Path(__file__).resolve().parents[2] / "docker-compose.production.yml"
    content = compose.read_text()
    for service in ("db:", "redis:", "backend:", "celery:"):
        assert service in content
    assert "postgres_data:" in content
    assert "redis_data:" in content
    assert "medical_documents:" in content


def test_celery_application_exists():
    worker = Path(__file__).resolve().parents[1] / "app" / "worker" / "celery_app.py"
    content = worker.read_text()
    assert "Celery(" in content
    assert "CELERY_BROKER_URL" in content
