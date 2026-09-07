"""Remove diagnostic rows created during counseling smoke tests."""

from services.counseling.models import CounselingSurvey, CounselingWorkshop, ExternalReferralProvider, SELGoal

deleted = []
for qs, label in [
    (CounselingWorkshop.objects.filter(title__startswith="DIAG"), "workshops"),
    (CounselingWorkshop.objects.filter(title__startswith="SMOKE"), "smoke_workshops"),
    (ExternalReferralProvider.objects.filter(name__startswith="DIAG"), "providers"),
    (ExternalReferralProvider.objects.filter(name__startswith="SMOKE"), "smoke_providers"),
    (CounselingSurvey.objects.filter(title__startswith="DIAG"), "surveys"),
    (CounselingSurvey.objects.filter(title__startswith="SMOKE"), "smoke_surveys"),
    (SELGoal.objects.filter(goal_description__startswith="DIAG"), "sel_goals"),
    (SELGoal.objects.filter(goal_description__startswith="SMOKE"), "smoke_sel_goals"),
]:
    n = qs.count()
    if n:
        qs.delete()
    deleted.append(f"{label}: {n}")

print(", ".join(deleted))
