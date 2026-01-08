from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from enums.job_type import JobType
from exceptions.collector_not_in_pool_error import CollectorNotInPoolError
from exceptions.job_name_exists_error import JobNameExistsError
from exceptions.job_not_exist_error import JobNotExistsError
from exceptions.produce_failure_error import ProduceFailureError
from exceptions.unauthorized_api_key import UnauthorizedApiKeyError
from models.db_schemas.jobs import GeneralJob
from models.validation_schemas.create_schemas.jobs import GeneralJobCreate
from models.validation_schemas.update_schemas.jobs import GeneralJobUpdate
from services.job_service import JobService


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def mock_pool_repo():
    return AsyncMock()


@pytest.fixture
def job_service(mock_repo, mock_pool_repo):
    service = JobService(mock_repo, mock_pool_repo)
    # Mock producer
    service.producer = AsyncMock()
    return service


# ==========================================
# CREATE JOB TESTS
# ==========================================


@pytest.mark.asyncio
async def test_create_job_success(
    init_beanie_db, job_service, mock_repo, mock_pool_repo
):
    # Setup
    mock_pool_repo.get.return_value = MagicMock(collector_clusters=["ocp4-col1"])
    mock_repo.get.return_value = None  # Job does not exist

    job_data = GeneralJobCreate(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["localhost:9090"],
    )

    # Execute
    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event = AsyncMock()
        response = await job_service.create(
            job_data, authorized_pools=["maas-pool1"], is_admin=False
        )

        # Verify
        assert "created successfully" in response.detail
        mock_repo.create.assert_called_once()
        mock_producer.send_event.assert_called_once()


@pytest.mark.asyncio
async def test_create_job_exists(
    init_beanie_db, job_service, mock_repo, mock_pool_repo
):
    mock_pool_repo.get.return_value = MagicMock(collector_clusters=["ocp4-col1"])
    mock_repo.get.return_value = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
    )

    job_data = GeneralJobCreate(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["localhost:9090"],
    )

    with pytest.raises(JobNameExistsError):
        await job_service.create(
            job_data, authorized_pools=["maas-pool1"], is_admin=False
        )


@pytest.mark.asyncio
async def test_create_job_unauthorized(init_beanie_db, job_service):
    job_data = GeneralJobCreate(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["localhost:9090"],
    )

    with pytest.raises(UnauthorizedApiKeyError):
        await job_service.create(
            job_data, authorized_pools=["other-pool"], is_admin=False
        )


@pytest.mark.asyncio
async def test_create_job_collector_not_in_pool(
    init_beanie_db, job_service, mock_pool_repo
):
    # Setup - mock pool check to return False (collector not in pool)
    # Mock pool_repo.get to return a pool that DOES NOT contain the collector
    mock_pool_repo.get.return_value = MagicMock(collector_clusters=["other-cluster"])

    job_data = GeneralJobCreate(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-missing-cluster",
        job_type=JobType.GENERAL,
        targets=["localhost:9090"],
    )

    with pytest.raises(CollectorNotInPoolError):
        await job_service.create(
            job_data, authorized_pools=["maas-pool1"], is_admin=False
        )


@pytest.mark.asyncio
async def test_create_job_produce_failure(
    init_beanie_db, job_service, mock_repo, mock_pool_repo
):
    mock_pool_repo.get.return_value = MagicMock(collector_clusters=["ocp4-col1"])
    mock_repo.get.return_value = None
    mock_repo.create = AsyncMock()
    mock_repo.delete = AsyncMock()

    job_data = GeneralJobCreate(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
    )

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event.side_effect = ProduceFailureError("Kafka error")

        with pytest.raises(ProduceFailureError):
            await job_service.create(job_data, ["maas-pool1"], False)

        mock_repo.create.assert_called_once()
        mock_repo.delete.assert_called_once()


# ==========================================
# DELETE JOB TESTS
# ==========================================


@pytest.mark.asyncio
async def test_delete_job_success(init_beanie_db, job_service, mock_repo):
    # Setup
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
    )
    mock_repo.get.return_value = mock_job

    # Execute
    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event = AsyncMock()
        response = await job_service.delete(
            "test-job", "maas-pool1", "ocp4-col1", ["maas-pool1"], False
        )

        # Verify
        assert "deleted successfully" in response.detail
        mock_repo.delete.assert_called_once_with(mock_job)
        mock_producer.send_event.assert_called_once()


@pytest.mark.asyncio
async def test_delete_job_not_found(init_beanie_db, job_service, mock_repo):
    mock_repo.get.return_value = None

    with pytest.raises(JobNotExistsError):
        await job_service.delete(
            "test-job", "maas-pool1", "ocp4-col1", ["maas-pool1"], False
        )


@pytest.mark.asyncio
async def test_delete_job_unauthorized(init_beanie_db, job_service):
    with pytest.raises(UnauthorizedApiKeyError):
        await job_service.delete(
            "test-job", "maas-pool1", "ocp4-col1", ["other-pool"], False
        )


@pytest.mark.asyncio
async def test_delete_job_produce_failure(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
    )
    mock_repo.get.return_value = mock_job
    mock_repo.delete = AsyncMock()
    mock_repo.create = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event.side_effect = ProduceFailureError("Kafka error")

        with pytest.raises(ProduceFailureError):
            await job_service.delete(
                "test-job", "maas-pool1", "ocp4-col1", ["maas-pool1"], False
            )

        mock_repo.delete.assert_called_once()
        mock_repo.create.assert_called_once()


# ==========================================
# UPDATE JOB TESTS
# ==========================================


@pytest.mark.asyncio
async def test_update_job_success(init_beanie_db, job_service, mock_repo):
    # Setup
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
    )
    mock_repo.get.return_value = mock_job

    job_update = GeneralJobUpdate(targets=["t2"], scrape_interval=60)

    # Execute
    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event = AsyncMock()
        response = await job_service.update(
            "test-job", "maas-pool1", job_update, "ocp4-col1", ["maas-pool1"], False
        )

        # Verify
        assert "updated successfully" in response.detail
        mock_repo.update.assert_called_once()
        mock_producer.send_event.assert_called_once()


@pytest.mark.asyncio
async def test_update_job_not_found(init_beanie_db, job_service, mock_repo):
    mock_repo.get.return_value = None
    job_update = GeneralJobUpdate(targets=["t2"])

    with pytest.raises(JobNotExistsError):
        await job_service.update(
            "test-job", "maas-pool1", job_update, "ocp4-col1", ["maas-pool1"], False
        )


@pytest.mark.asyncio
async def test_update_job_unauthorized(init_beanie_db, job_service):
    job_update = GeneralJobUpdate(targets=["t2"])
    with pytest.raises(UnauthorizedApiKeyError):
        await job_service.update(
            "test-job", "maas-pool1", job_update, "ocp4-col1", ["other-pool"], False
        )


@pytest.mark.asyncio
async def test_update_job_produce_failure(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
    )
    mock_repo.get.return_value = mock_job
    mock_repo.update = AsyncMock()
    job_update = GeneralJobUpdate(targets=["t2"])

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event.side_effect = ProduceFailureError("Kafka error")

        with pytest.raises(ProduceFailureError):
            await job_service.update(
                "test-job", "maas-pool1", job_update, "ocp4-col1", ["maas-pool1"], False
            )

        assert mock_repo.update.call_count == 2


# ==========================================
# ADD TARGET TESTS
# ==========================================


@pytest.mark.asyncio
async def test_add_target_success(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event = AsyncMock()
        response = await job_service.add_target(
            "test-job", "maas-pool1", "ocp4-col1", "t2", ["maas-pool1"], False
        )

        assert "added to job" in response.detail
        assert "t2" in mock_job.targets
        mock_repo.save.assert_called()


@pytest.mark.asyncio
async def test_add_target_not_found(init_beanie_db, job_service, mock_repo):
    mock_repo.get.return_value = None
    with pytest.raises(JobNotExistsError):
        await job_service.add_target(
            "test-job", "maas-pool1", "ocp4-col1", "t2", ["maas-pool1"], False
        )


@pytest.mark.asyncio
async def test_add_target_unauthorized(init_beanie_db, job_service):
    with pytest.raises(UnauthorizedApiKeyError):
        await job_service.add_target(
            "test-job", "maas-pool1", "ocp4-col1", "t2", ["other-pool"], False
        )


@pytest.mark.asyncio
async def test_add_target_not_supported(init_beanie_db, job_service, mock_repo):
    # Basic auth is accessed in get method so we need to ensure it's None on the mocked object
    mock_repo.get.return_value = MagicMock(spec=object, basic_auth=None)

    with pytest.raises(HTTPException) as exc:
        await job_service.add_target(
            "test-job", "maas-pool1", "ocp4-col1", "t2", ["maas-pool1"], False
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_add_target_produce_failure(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event.side_effect = ProduceFailureError("Kafka error")

        with pytest.raises(ProduceFailureError):
            await job_service.add_target(
                "test-job", "maas-pool1", "ocp4-col1", "t2", ["maas-pool1"], False
            )

        assert "t2" not in mock_job.targets
        assert mock_repo.save.call_count == 2


# ==========================================
# DELETE TARGET TESTS
# ==========================================


@pytest.mark.asyncio
async def test_delete_target_success(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1", "t2"],
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event = AsyncMock()
        response = await job_service.delete_target(
            "test-job", "maas-pool1", "ocp4-col1", "t2", ["maas-pool1"], False
        )

        assert "deleted from job" in response.detail
        assert "t2" not in mock_job.targets
        mock_repo.save.assert_called()


@pytest.mark.asyncio
async def test_delete_target_not_found(init_beanie_db, job_service, mock_repo):
    mock_repo.get.return_value = None
    with pytest.raises(JobNotExistsError):
        await job_service.delete_target(
            "test-job", "maas-pool1", "ocp4-col1", "t2", ["maas-pool1"], False
        )


@pytest.mark.asyncio
async def test_delete_target_unauthorized(init_beanie_db, job_service):
    with pytest.raises(UnauthorizedApiKeyError):
        await job_service.delete_target(
            "test-job", "maas-pool1", "ocp4-col1", "t2", ["other-pool"], False
        )


@pytest.mark.asyncio
async def test_delete_target_not_supported(init_beanie_db, job_service, mock_repo):
    mock_repo.get.return_value = MagicMock(spec=object, basic_auth=None)
    with pytest.raises(HTTPException) as exc:
        await job_service.delete_target(
            "test-job", "maas-pool1", "ocp4-col1", "t2", ["maas-pool1"], False
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_delete_target_produce_failure(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1", "t2"],
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event.side_effect = ProduceFailureError("Kafka error")

        with pytest.raises(ProduceFailureError):
            await job_service.delete_target(
                "test-job", "maas-pool1", "ocp4-col1", "t2", ["maas-pool1"], False
            )

        assert "t2" in mock_job.targets
        assert mock_repo.save.call_count == 2


# ==========================================
# ADD LABEL TESTS
# ==========================================


@pytest.mark.asyncio
async def test_add_label_success(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
        labels={},
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    labels = {"env": "prod"}

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event = AsyncMock()
        response = await job_service.add_label(
            "test-job", "maas-pool1", "ocp4-col1", labels, ["maas-pool1"], False
        )

        assert "added to job" in response.detail
        assert mock_job.labels["env"] == "prod"
        mock_repo.save.assert_called()


@pytest.mark.asyncio
async def test_add_label_not_found(init_beanie_db, job_service, mock_repo):
    mock_repo.get.return_value = None
    with pytest.raises(JobNotExistsError):
        await job_service.add_label(
            "test-job", "maas-pool1", "ocp4-col1", {"k": "v"}, ["maas-pool1"], False
        )


@pytest.mark.asyncio
async def test_add_label_unauthorized(init_beanie_db, job_service):
    with pytest.raises(UnauthorizedApiKeyError):
        await job_service.add_label(
            "test-job", "maas-pool1", "ocp4-col1", {"k": "v"}, ["other-pool"], False
        )


@pytest.mark.asyncio
async def test_add_label_produce_failure(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
        labels={},
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event.side_effect = ProduceFailureError("Kafka error")

        with pytest.raises(ProduceFailureError):
            await job_service.add_label(
                "test-job", "maas-pool1", "ocp4-col1", {"k": "v"}, ["maas-pool1"], False
            )

        assert "k" not in (mock_job.labels or {})
        assert mock_repo.save.call_count == 2


# ==========================================
# UPDATE LABEL TESTS
# ==========================================


@pytest.mark.asyncio
async def test_update_label_success(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
        labels={"env": "dev"},
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event = AsyncMock()
        response = await job_service.update_label(
            "test-job", "maas-pool1", "ocp4-col1", "env", "prod", ["maas-pool1"], False
        )

        assert "updated to job" in response.detail
        assert mock_job.labels["env"] == "prod"
        mock_repo.save.assert_called()


@pytest.mark.asyncio
async def test_update_label_not_found(init_beanie_db, job_service, mock_repo):
    mock_repo.get.return_value = None
    with pytest.raises(JobNotExistsError):
        await job_service.update_label(
            "test-job", "maas-pool1", "ocp4-col1", "k", "v", ["maas-pool1"], False
        )


@pytest.mark.asyncio
async def test_update_label_key_not_found(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
        labels={},
    )
    mock_repo.get.return_value = mock_job

    with pytest.raises(HTTPException) as exc:
        await job_service.update_label(
            "test-job",
            "maas-pool1",
            "ocp4-col1",
            "missing_key",
            "v",
            ["maas-pool1"],
            False,
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_update_label_unauthorized(init_beanie_db, job_service):
    with pytest.raises(UnauthorizedApiKeyError):
        await job_service.update_label(
            "test-job", "maas-pool1", "ocp4-col1", "k", "v", ["other-pool"], False
        )


@pytest.mark.asyncio
async def test_update_label_produce_failure(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
        labels={"k": "old"},
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event.side_effect = ProduceFailureError("Kafka error")

        with pytest.raises(ProduceFailureError):
            await job_service.update_label(
                "test-job", "maas-pool1", "ocp4-col1", "k", "new", ["maas-pool1"], False
            )

        assert mock_job.labels["k"] == "old"
        assert mock_repo.save.call_count == 2


# ==========================================
# DELETE LABEL TESTS
# ==========================================


@pytest.mark.asyncio
async def test_delete_label_success(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
        labels={"env": "dev"},
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event = AsyncMock()
        response = await job_service.delete_label(
            "test-job", "maas-pool1", "ocp4-col1", "env", ["maas-pool1"], False
        )

        assert "deleted from job" in response.detail
        assert "env" not in mock_job.labels
        mock_repo.save.assert_called()


@pytest.mark.asyncio
async def test_delete_label_not_found(init_beanie_db, job_service, mock_repo):
    mock_repo.get.return_value = None
    with pytest.raises(JobNotExistsError):
        await job_service.delete_label(
            "test-job", "maas-pool1", "ocp4-col1", "k", ["maas-pool1"], False
        )


@pytest.mark.asyncio
async def test_delete_label_unauthorized(init_beanie_db, job_service):
    with pytest.raises(UnauthorizedApiKeyError):
        await job_service.delete_label(
            "test-job", "maas-pool1", "ocp4-col1", "k", ["other-pool"], False
        )


@pytest.mark.asyncio
async def test_delete_label_produce_failure(init_beanie_db, job_service, mock_repo):
    mock_job = GeneralJob(
        job_name="test-job",
        maas_pool="maas-pool1",
        collector_cluster="ocp4-col1",
        job_type=JobType.GENERAL,
        targets=["t1"],
        labels={"k": "v"},
    )
    mock_repo.get.return_value = mock_job
    mock_repo.save = AsyncMock()

    with patch("services.job_service.producer") as mock_producer:
        mock_producer.send_event.side_effect = ProduceFailureError("Kafka error")

        with pytest.raises(ProduceFailureError):
            await job_service.delete_label(
                "test-job", "maas-pool1", "ocp4-col1", "k", ["maas-pool1"], False
            )

        assert "k" in mock_job.labels
        assert mock_repo.save.call_count == 2
