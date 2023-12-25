import csv
import re

from django.utils import timezone

from board.models import Card, EstimationQuestionSet
from timelogging.models import TimeLog

estimation_question_sets = EstimationQuestionSet.objects.filter(
    _estimation_questions__question__icontains='hours').values_list('pk', flat=True)
cards = Card.objects.filter(
    active_question_set__in=estimation_question_sets,
    subtasks__task__title__icontains='Developing'
).distinct().iterator()

with open('../dataset.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(
        csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    items = []
    for c in cards:
        t = TimeLog.objects.filter(
            task_assignment__task__card_subtask__card=c
        ).order_by('-duration').first()
        if not t:
            continue

        title = re.sub(',', '|', c.title)
        
        user_profile = t.employment.applicant.user_profile_id
        hours_q = c.card_estimations.filter(
            question__question__icontains='hours', estimator=user_profile).first()
        confidence_q = c.card_estimations.filter(
            question__question__icontains='confidence', estimator=user_profile).first()
        interest_q = c.card_estimations.filter(
            question__question__icontains='interest', estimator=user_profile).first()
        
        hours_response = float(hours_q.answer) if hours_q else 4.0
        confidence_response = float(confidence_q.answer) if confidence_q else 5.0
        interest_response = float(interest_q.answer) if interest_q else 5.0
        severity = c.tags.filter(name__icontains='severity').first()
        if severity == 'Minor-Severity':
            severity_response = 1
        elif severity == 'Major Severity':
            severity_response = 2
        elif severity == 'Critical Severity':
            severity_response = 3
        else:
            severity_response = 1

        now = timezone.now()
        years_of_experience = (now - t.employment.start_date).days / 365.25

        if hours_response == 0:
            hours_response = 20.0
        if confidence_response == 0:
            confidence_response = 1
        if interest_response == 0:
            interest_response = 1

        try:
            team_size = c.assignees.count()
        except Exception:
            team_size = 1

        items.append([
            title,
            t.duration,
            hours_response,
            confidence_response,
            interest_response,
            severity_response,
            years_of_experience,
            team_size,
        ])

    csv_writer.writerows([
        ['task', 'duration', 'hours', 'confidence', 'interest', 'severity', 'years of experience', 'team size'],
        *items])
