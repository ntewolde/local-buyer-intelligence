from app.tasks import recompute_scores_task

def test_recompute_scores_task_runs():
    result = recompute_scores_task.delay(1, "lawn_care", "fake-client-id")
    assert result.successful()



